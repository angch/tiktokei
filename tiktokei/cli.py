"""
Command-line interface for tiktokei.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .core import (
    count_tokens_in_file, 
    count_tokens_in_text, 
    get_available_encodings,
    analyze_path,
    print_project_stats
)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="tiktokei",
        description="Count tokens in text files using tiktoken (like tokei but for tokens)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tiktokei                                 # Count tokens in current directory
  tiktokei src/                           # Count tokens in src directory  
  tiktokei document.txt                   # Count tokens in document.txt
  tiktokei document.txt --encoding p50k_base  # Use different encoding
  tiktokei --list-encodings               # Show available encodings
  echo "Hello world" | tiktokei --stdin   # Count tokens from stdin
  tiktokei --files                        # Show individual file statistics
        """,
    )
    
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to file or directory to process (default: current directory)"
    )
    
    parser.add_argument(
        "--encoding",
        "-e",
        default="cl100k_base",
        help="Tiktoken encoding to use (default: cl100k_base)"
    )
    
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read text from stdin instead of files"
    )
    
    parser.add_argument(
        "--files",
        "-f",
        action="store_true",
        help="Show individual file statistics"
    )
    
    parser.add_argument(
        "--list-encodings",
        action="store_true",
        help="List all available encodings and exit"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.2.0"
    )
    
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Only output the total token count"
    )
    
    return parser


def main() -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle list encodings
    if args.list_encodings:
        encodings = get_available_encodings()
        if not args.quiet:
            print("Available encodings:")
        for encoding in encodings:
            print(f"  {encoding}" if not args.quiet else encoding)
        return 0
    
    # Handle stdin input
    if args.stdin:
        try:
            text = sys.stdin.read()
            token_count = count_tokens_in_text(text, args.encoding)
            if token_count == -1:
                return 1
                
            if args.quiet:
                print(token_count)
            else:
                print(f"Text from stdin")
                print(f"Encoding used: {args.encoding}")
                print(f"Total tokens: {token_count}")
            return 0
            
        except KeyboardInterrupt:
            print("\nOperation cancelled.", file=sys.stderr)
            return 1
    
    # Handle file/directory input
    target_path = Path(args.path)
    if not target_path.exists():
        print(f"Error: Path not found at '{target_path}'", file=sys.stderr)
        return 1
    
    # Analyze the path
    try:
        project_stats = analyze_path(target_path, args.encoding)
        
        if project_stats.total_files == 0:
            if args.quiet:
                print("0")
            else:
                print("No files found to analyze.")
            return 0
        
        # Output results
        if args.quiet:
            print(project_stats.total_tokens)
        else:
            if target_path.is_file():
                # Single file - show simple output
                print(f"File: '{target_path}'")
                print(f"Encoding used: {args.encoding}")
                print(f"Total tokens: {project_stats.total_tokens:,}")
            else:
                # Directory - show tokei-style output
                print(f"Directory: {target_path.resolve()}")
                print(f"Encoding used: {args.encoding}")
                print()
                print_project_stats(project_stats, show_files=args.files)
        
        return 0
        
    except KeyboardInterrupt:
        print("\nOperation cancelled.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
