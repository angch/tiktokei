"""
Tests for the core functionality of tiktokei.
"""

import tempfile
import os
from pathlib import Path

import pytest

from tiktokei.core import (
    count_tokens_in_file, 
    count_tokens_in_text, 
    get_available_encodings,
    get_language_from_path,
    should_ignore_path,
    is_text_file,
    analyze_file,
    FileStats
)


class TestTokenCounting:
    """Test token counting functionality."""
    
    def test_count_tokens_in_text_basic(self):
        """Test basic token counting for text."""
        text = "Hello, world!"
        count = count_tokens_in_text(text)
        assert count > 0
        assert isinstance(count, int)
    
    def test_count_tokens_in_text_empty(self):
        """Test token counting for empty text."""
        text = ""
        count = count_tokens_in_text(text)
        assert count == 0
    
    def test_count_tokens_different_encodings(self):
        """Test that different encodings may produce different counts."""
        text = "Hello, world! This is a test."
        
        count_cl100k = count_tokens_in_text(text, "cl100k_base")
        count_p50k = count_tokens_in_text(text, "p50k_base")
        
        assert count_cl100k > 0
        assert count_p50k > 0
        # They might be the same or different, but both should be positive
    
    def test_count_tokens_in_file_basic(self):
        """Test token counting for a file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Hello, world! This is a test file.")
            temp_file = f.name
        
        try:
            count = count_tokens_in_file(temp_file)
            assert count > 0
            assert isinstance(count, int)
        finally:
            os.unlink(temp_file)
    
    def test_count_tokens_in_file_nonexistent(self):
        """Test token counting for a non-existent file."""
        count = count_tokens_in_file("/path/that/does/not/exist.txt")
        assert count == -1
    
    def test_get_available_encodings(self):
        """Test that we can get available encodings."""
        encodings = get_available_encodings()
        assert isinstance(encodings, list)
        assert len(encodings) > 0
        assert "cl100k_base" in encodings


class TestFileHandling:
    """Test file handling edge cases."""
    
    def test_empty_file(self):
        """Test token counting for an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            # Write nothing to create an empty file
            temp_file = f.name
        
        try:
            count = count_tokens_in_file(temp_file)
            assert count == 0
        finally:
            os.unlink(temp_file)
    
    def test_unicode_file(self):
        """Test token counting for a file with unicode characters."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write("Hello, 世界! This is a test with émojis 🚀🎉")
            temp_file = f.name
        
        try:
            count = count_tokens_in_file(temp_file)
            assert count > 0
            assert isinstance(count, int)
        finally:
            os.unlink(temp_file)
