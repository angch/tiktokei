"""
Core functionality for token counting using tiktoken.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Union, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict

try:
    import tiktoken
except ImportError:
    print("Error: tiktoken is not installed. Install with: pip install tiktoken", file=sys.stderr)
    sys.exit(1)


@dataclass
class FileStats:
    """Statistics for a single file."""
    path: Path
    lines: int = 0
    tokens: int = 0
    size: int = 0
    
    
@dataclass 
class LanguageStats:
    """Statistics for a specific file type/language."""
    name: str
    files: List[FileStats] = field(default_factory=list)
    total_files: int = 0
    total_lines: int = 0
    total_tokens: int = 0
    total_size: int = 0
    
    def add_file(self, file_stats: FileStats):
        """Add a file to this language's statistics."""
        self.files.append(file_stats)
        self.total_files += 1
        self.total_lines += file_stats.lines
        self.total_tokens += file_stats.tokens
        self.total_size += file_stats.size


@dataclass
class ProjectStats:
    """Overall project statistics."""
    languages: Dict[str, LanguageStats] = field(default_factory=dict)
    total_files: int = 0
    total_lines: int = 0
    total_tokens: int = 0
    total_size: int = 0
    
    def add_file_stats(self, language: str, file_stats: FileStats):
        """Add file statistics to the project."""
        if language not in self.languages:
            self.languages[language] = LanguageStats(name=language)
        
        self.languages[language].add_file(file_stats)
        self.total_files += 1
        self.total_lines += file_stats.lines
        self.total_tokens += file_stats.tokens
        self.total_size += file_stats.size


# Common file extensions mapped to language names
LANGUAGE_EXTENSIONS = {
    # Programming languages
    '.py': 'Python',
    '.js': 'JavaScript', 
    '.jsx': 'JavaScript',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript',
    '.java': 'Java',
    '.c': 'C',
    '.cpp': 'C++',
    '.cc': 'C++',
    '.cxx': 'C++',
    '.h': 'C Header',
    '.hpp': 'C++ Header',
    '.cs': 'C#',
    '.php': 'PHP',
    '.rb': 'Ruby',
    '.go': 'Go',
    '.rs': 'Rust',
    '.swift': 'Swift',
    '.kt': 'Kotlin',
    '.scala': 'Scala',
    '.r': 'R',
    '.m': 'Objective-C',
    '.pl': 'Perl',
    '.sh': 'Shell',
    '.bash': 'Shell',
    '.zsh': 'Shell',
    '.fish': 'Shell',
    '.ps1': 'PowerShell',
    '.lua': 'Lua',
    '.dart': 'Dart',
    '.elm': 'Elm',
    '.clj': 'Clojure',
    '.hs': 'Haskell',
    '.ml': 'OCaml',
    '.fs': 'F#',
    '.jl': 'Julia',
    '.nim': 'Nim',
    '.zig': 'Zig',
    '.v': 'V',
    '.cr': 'Crystal',
    
    # Web languages
    '.html': 'HTML',
    '.htm': 'HTML',
    '.xml': 'XML',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.sass': 'Sass',
    '.less': 'Less',
    '.vue': 'Vue',
    '.svelte': 'Svelte',
    
    # Data/Config
    '.json': 'JSON',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.toml': 'TOML',
    '.ini': 'INI',
    '.cfg': 'Config',
    '.conf': 'Config',
    '.sql': 'SQL',
    '.graphql': 'GraphQL',
    '.gql': 'GraphQL',
    
    # Documentation
    '.md': 'Markdown',
    '.markdown': 'Markdown',
    '.rst': 'reStructuredText',
    '.txt': 'Text',
    '.tex': 'LaTeX',
    '.org': 'Org',
    
    # Other
    '.dockerfile': 'Dockerfile',
    '.makefile': 'Makefile',
    '.cmake': 'CMake',
    '.gradle': 'Gradle',
    '.mvn': 'Maven',
}

# Files to ignore
IGNORE_PATTERNS = {
    # Version control
    '.git', '.svn', '.hg', '.bzr',
    # Dependencies/build
    'node_modules', '__pycache__', '.pytest_cache', 'target', 'build', 'dist',
    # IDE/Editor
    '.vscode', '.idea', '.vs', '.atom', '.sublime-workspace',
    # OS
    '.DS_Store', 'Thumbs.db',
    # Others
    '.env', '.cache', '.tmp', 'tmp', 'temp',
}


def get_language_from_path(file_path: Path) -> str:
    """Determine the language/type of a file based on its extension."""
    if file_path.name.lower() in ['dockerfile', 'makefile', 'cmakelists.txt']:
        return file_path.name.title()
    
    suffix = file_path.suffix.lower()
    return LANGUAGE_EXTENSIONS.get(suffix, 'Other')


def should_ignore_path(path: Path) -> bool:
    """Check if a path should be ignored."""
    return any(ignore in path.parts for ignore in IGNORE_PATTERNS)


def count_lines_in_file(file_path: Path) -> int:
    """Count the number of lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except (UnicodeDecodeError, PermissionError):
        # For binary files or files we can't read, return 0
        return 0


def is_text_file(file_path: Path) -> bool:
    """Check if a file is likely a text file."""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\0' in chunk:
                return False  # Binary file
        return True
    except (PermissionError, OSError):
        return False


def count_tokens_in_file(file_path: str, encoding_name: str = "cl100k_base") -> int:
    """
    Reads a file, encodes its content using tiktoken, and returns the token count.

    Args:
        file_path (str): The path to the file to be processed.
        encoding_name (str): The name of the tiktoken encoding to use.
                             Common encodings include "cl100k_base" (for GPT-4, GPT-3.5-Turbo),
                             "p50k_base" (for Codex, text-davinci-002, text-davinci-003),
                             and "r50k_base" (for GPT-3).

    Returns:
        int: The total number of tokens in the file. Returns -1 on error.
    """
    path = Path(file_path)
    if not path.exists():
        print(f"Error: File not found at '{file_path}'", file=sys.stderr)
        return -1

    try:
        # Read the content of the file
        with open(path, 'r', encoding='utf-8') as f:
            text_content = f.read()

        # Get the tiktoken encoding
        # This line will download the encoding if it's not already cached
        encoding = tiktoken.get_encoding(encoding_name)

        # Encode the text and count the tokens
        tokens = encoding.encode(text_content)
        return len(tokens)

    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'", file=sys.stderr)
        return -1
    except UnicodeDecodeError as e:
        print(f"Error: Unable to decode file '{file_path}': {e}", file=sys.stderr)
        return -1
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return -1


def analyze_file(file_path: Path, encoding_name: str = "cl100k_base") -> Optional[FileStats]:
    """
    Analyze a single file and return its statistics.
    
    Args:
        file_path: Path to the file to analyze
        encoding_name: Tiktoken encoding to use
        
    Returns:
        FileStats object or None if file cannot be processed
    """
    try:
        if not file_path.is_file() or not is_text_file(file_path):
            return None
            
        # Get file size
        size = file_path.stat().st_size
        
        # Count lines
        lines = count_lines_in_file(file_path)
        
        # Count tokens
        tokens = count_tokens_in_file(str(file_path), encoding_name)
        if tokens == -1:
            tokens = 0
            
        return FileStats(
            path=file_path,
            lines=lines,
            tokens=tokens,
            size=size
        )
        
    except Exception as e:
        print(f"Warning: Could not analyze file '{file_path}': {e}", file=sys.stderr)
        return None


def analyze_directory(dir_path: Path, encoding_name: str = "cl100k_base") -> ProjectStats:
    """
    Recursively analyze a directory and return project statistics.
    
    Args:
        dir_path: Path to the directory to analyze
        encoding_name: Tiktoken encoding to use
        
    Returns:
        ProjectStats object containing all file statistics
    """
    project_stats = ProjectStats()
    
    if not dir_path.is_dir():
        print(f"Error: '{dir_path}' is not a directory", file=sys.stderr)
        return project_stats
    
    # Walk through all files recursively
    for file_path in dir_path.rglob('*'):
        # Skip if should be ignored
        if should_ignore_path(file_path):
            continue
            
        # Skip directories
        if not file_path.is_file():
            continue
            
        # Analyze the file
        file_stats = analyze_file(file_path, encoding_name)
        if file_stats is not None:
            language = get_language_from_path(file_path)
            project_stats.add_file_stats(language, file_stats)
    
    return project_stats


def analyze_path(path: Union[str, Path], encoding_name: str = "cl100k_base") -> ProjectStats:
    """
    Analyze a file or directory path and return statistics.
    
    Args:
        path: Path to analyze (file or directory)
        encoding_name: Tiktoken encoding to use
        
    Returns:
        ProjectStats object
    """
    path = Path(path)
    project_stats = ProjectStats()
    
    if path.is_file():
        # Single file analysis
        file_stats = analyze_file(path, encoding_name)
        if file_stats is not None:
            language = get_language_from_path(path)
            project_stats.add_file_stats(language, file_stats)
    elif path.is_dir():
        # Directory analysis
        project_stats = analyze_directory(path, encoding_name)
    else:
        print(f"Error: Path '{path}' does not exist", file=sys.stderr)
    
    return project_stats


def count_tokens_in_text(text: str, encoding_name: str = "cl100k_base") -> int:
    """
    Encodes text content using tiktoken and returns the token count.

    Args:
        text (str): The text content to process.
        encoding_name (str): The name of the tiktoken encoding to use.

    Returns:
        int: The total number of tokens in the text.
    """
    try:
        # Get the tiktoken encoding
        encoding = tiktoken.get_encoding(encoding_name)
        
        # Encode the text and count the tokens
        tokens = encoding.encode(text)
        return len(tokens)
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return -1


def get_available_encodings() -> list[str]:
    """
    Get a list of available tiktoken encodings.
    
    Returns:
        list[str]: List of available encoding names.
    """
    try:
        return tiktoken.list_encoding_names()
    except Exception:
        # Fallback to common encodings if tiktoken doesn't have list_encoding_names
        return ["cl100k_base", "p50k_base", "r50k_base", "gpt2"]


def format_number(num: int) -> str:
    """Format a number with thousand separators."""
    return f"{num:,}"


def print_project_stats(project_stats: ProjectStats, show_files: bool = False):
    """
    Print project statistics in a tokei-like format.
    
    Args:
        project_stats: The project statistics to display
        show_files: Whether to show individual file statistics
    """
    if project_stats.total_files == 0:
        print("No files found.")
        return
        
    # Header
    print("=" * 80)
    print(f" Language            Files        Lines       Tokens        Bytes")
    print("=" * 80)
    
    # Sort languages by total tokens (descending)
    sorted_languages = sorted(
        project_stats.languages.items(),
        key=lambda x: x[1].total_tokens,
        reverse=True
    )
    
    # Print each language
    for lang_name, lang_stats in sorted_languages:
        print(f" {lang_name:<18} {lang_stats.total_files:>6} "
              f"{format_number(lang_stats.total_lines):>11} "
              f"{format_number(lang_stats.total_tokens):>11} "
              f"{format_number(lang_stats.total_size):>11}")
        
        # Show individual files if requested
        if show_files and lang_stats.files:
            sorted_files = sorted(lang_stats.files, key=lambda x: x.tokens, reverse=True)
            for file_stat in sorted_files:
                rel_path = str(file_stat.path)
                if len(rel_path) > 50:
                    rel_path = "..." + rel_path[-47:]
                print(f"   {rel_path:<50} "
                      f"{format_number(file_stat.lines):>7} "
                      f"{format_number(file_stat.tokens):>7} "
                      f"{format_number(file_stat.size):>7}")
    
    # Total line
    print("-" * 80)
    print(f" {'Total':<18} {project_stats.total_files:>6} "
          f"{format_number(project_stats.total_lines):>11} "
          f"{format_number(project_stats.total_tokens):>11} "
          f"{format_number(project_stats.total_size):>11}")
    print("=" * 80)
