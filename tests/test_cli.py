"""
Tests for the CLI functionality of tiktokei.
"""

import tempfile
import os
from io import StringIO
import sys
from unittest.mock import patch

from tiktokei.cli import main, create_parser


class TestCLI:
    """Test CLI functionality."""
    
    def test_parser_creation(self):
        """Test that the argument parser is created correctly."""
        parser = create_parser()
        assert parser.prog == "tiktokei"
    
    def test_help_option(self):
        """Test that help option works."""
        parser = create_parser()
        
        # This should not raise an exception
        help_text = parser.format_help()
        assert "tiktokei" in help_text
        assert "Count tokens" in help_text
    
    def test_file_argument_parsing(self):
        """Test parsing of file arguments."""
        parser = create_parser()
        
        args = parser.parse_args(["test.txt"])
        assert args.path == "test.txt"
        assert args.encoding == "cl100k_base"  # default
        assert not args.stdin
        assert not args.quiet
        assert not args.files
    
    def test_encoding_argument(self):
        """Test parsing of encoding argument."""
        parser = create_parser()
        
        args = parser.parse_args(["test.txt", "--encoding", "p50k_base"])
        assert args.path == "test.txt"
        assert args.encoding == "p50k_base"
    
    def test_stdin_flag(self):
        """Test parsing of stdin flag."""
        parser = create_parser()
        
        args = parser.parse_args(["--stdin"])
        assert args.stdin is True
        assert args.path == "."  # default path
    
    def test_files_flag(self):
        """Test parsing of files flag.""" 
        parser = create_parser()
        
        args = parser.parse_args(["--files"])
        assert args.files is True
    
    def test_quiet_flag(self):
        """Test parsing of quiet flag."""
        parser = create_parser()
        
        args = parser.parse_args(["test.txt", "--quiet"])
        assert args.quiet is True
    
    def test_list_encodings_flag(self):
        """Test parsing of list encodings flag."""
        parser = create_parser()
        
        args = parser.parse_args(["--list-encodings"])
        assert args.list_encodings is True


class TestMainFunction:
    """Test the main function behavior."""
    
    def test_main_with_nonexistent_file(self):
        """Test main function with a non-existent file."""
        with patch('sys.argv', ['tiktokei', '/path/that/does/not/exist.txt']):
            exit_code = main()
            assert exit_code == 1
    
    def test_main_with_list_encodings(self):
        """Test main function with list encodings flag."""
        with patch('sys.argv', ['tiktokei', '--list-encodings']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                exit_code = main()
                assert exit_code == 0
                output = mock_stdout.getvalue()
                assert "cl100k_base" in output
    
    def test_main_with_stdin(self):
        """Test main function with stdin input."""
        test_input = "Hello, world!"
        
        with patch('sys.argv', ['tiktokei', '--stdin']):
            with patch('sys.stdin', StringIO(test_input)):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    exit_code = main()
                    assert exit_code == 0
                    output = mock_stdout.getvalue()
                    assert "Total tokens:" in output
    
    def test_main_with_real_file(self):
        """Test main function with a real file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Hello, world! This is a test file.")
            temp_file = f.name
        
        try:
            with patch('sys.argv', ['tiktokei', temp_file]):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    exit_code = main()
                    assert exit_code == 0
                    output = mock_stdout.getvalue()
                    assert "Total tokens:" in output
                    assert temp_file in output
        finally:
            os.unlink(temp_file)
