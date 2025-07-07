"""
Tests for the new directory analysis functionality of tiktokei.
"""

import tempfile
import os
from pathlib import Path

import pytest

from tiktokei.core import (
    get_language_from_path,
    should_ignore_path,
    is_text_file,
    analyze_file,
    analyze_directory,
    analyze_path,
    FileStats,
    ProjectStats
)


class TestLanguageDetection:
    """Test language detection functionality."""
    
    def test_get_language_from_path_python(self):
        """Test language detection for Python files."""
        assert get_language_from_path(Path("test.py")) == "Python"
        
    def test_get_language_from_path_javascript(self):
        """Test language detection for JavaScript files."""
        assert get_language_from_path(Path("test.js")) == "JavaScript"
        assert get_language_from_path(Path("test.jsx")) == "JavaScript"
        
    def test_get_language_from_path_typescript(self):
        """Test language detection for TypeScript files."""
        assert get_language_from_path(Path("test.ts")) == "TypeScript"
        assert get_language_from_path(Path("test.tsx")) == "TypeScript"
        
    def test_get_language_from_path_markdown(self):
        """Test language detection for Markdown files."""
        assert get_language_from_path(Path("README.md")) == "Markdown"
        assert get_language_from_path(Path("test.markdown")) == "Markdown"
        
    def test_get_language_from_path_dockerfile(self):
        """Test language detection for Dockerfile."""
        assert get_language_from_path(Path("Dockerfile")) == "Dockerfile"
        assert get_language_from_path(Path("dockerfile")) == "Dockerfile"
        
    def test_get_language_from_path_unknown(self):
        """Test language detection for unknown files."""
        assert get_language_from_path(Path("test.unknown")) == "Other"


class TestFileFiltering:
    """Test file filtering functionality."""
    
    def test_should_ignore_git(self):
        """Test ignoring git directories."""
        assert should_ignore_path(Path("project/.git/config"))
        assert should_ignore_path(Path(".git"))
        
    def test_should_ignore_node_modules(self):
        """Test ignoring node_modules."""
        assert should_ignore_path(Path("project/node_modules/package/index.js"))
        
    def test_should_ignore_pycache(self):
        """Test ignoring __pycache__."""
        assert should_ignore_path(Path("src/__pycache__/module.pyc"))
        
    def test_should_not_ignore_regular_files(self):
        """Test not ignoring regular files."""
        assert not should_ignore_path(Path("src/main.py"))
        assert not should_ignore_path(Path("README.md"))


class TestFileAnalysis:
    """Test file analysis functionality."""
    
    def test_is_text_file_text(self):
        """Test text file detection for text files."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Hello, world!")
            temp_file = f.name
        
        try:
            assert is_text_file(Path(temp_file))
        finally:
            os.unlink(temp_file)
    
    def test_is_text_file_binary(self):
        """Test text file detection for binary files."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.bin') as f:
            f.write(b'\x00\x01\x02\x03')
            temp_file = f.name
        
        try:
            assert not is_text_file(Path(temp_file))
        finally:
            os.unlink(temp_file)
    
    def test_analyze_file_success(self):
        """Test successful file analysis."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write("def hello():\n    print('Hello, world!')\n")
            temp_file = f.name
        
        try:
            file_stats = analyze_file(Path(temp_file))
            assert file_stats is not None
            assert isinstance(file_stats, FileStats)
            assert file_stats.lines > 0
            assert file_stats.tokens > 0
            assert file_stats.size > 0
        finally:
            os.unlink(temp_file)
    
    def test_analyze_file_binary(self):
        """Test analyzing binary file returns None."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.bin') as f:
            f.write(b'\x00\x01\x02\x03')
            temp_file = f.name
        
        try:
            file_stats = analyze_file(Path(temp_file))
            assert file_stats is None
        finally:
            os.unlink(temp_file)


class TestDirectoryAnalysis:
    """Test directory analysis functionality."""
    
    def test_analyze_path_single_file(self):
        """Test analyzing a single file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write("print('Hello, world!')")
            temp_file = f.name
        
        try:
            stats = analyze_path(temp_file)
            assert isinstance(stats, ProjectStats)
            assert stats.total_files == 1
            assert stats.total_tokens > 0
            assert "Python" in stats.languages
        finally:
            os.unlink(temp_file)
    
    def test_analyze_path_directory(self):
        """Test analyzing a directory with multiple files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create some test files
            (temp_path / "main.py").write_text("print('Hello from Python')")
            (temp_path / "script.js").write_text("console.log('Hello from JS');")
            (temp_path / "README.md").write_text("# Test Project")
            
            # Create subdirectory
            sub_dir = temp_path / "src"
            sub_dir.mkdir()
            (sub_dir / "utils.py").write_text("def helper(): pass")
            
            stats = analyze_path(temp_path)
            assert isinstance(stats, ProjectStats)
            assert stats.total_files == 4
            assert "Python" in stats.languages
            assert "JavaScript" in stats.languages
            assert "Markdown" in stats.languages
            assert stats.languages["Python"].total_files == 2
            assert stats.total_tokens > 0
    
    def test_analyze_path_with_ignored_files(self):
        """Test that ignored files are not analyzed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create regular files
            (temp_path / "main.py").write_text("print('Hello')")
            
            # Create ignored directories/files
            git_dir = temp_path / ".git"
            git_dir.mkdir()
            (git_dir / "config").write_text("some git config")
            
            pycache_dir = temp_path / "__pycache__"
            pycache_dir.mkdir()
            (pycache_dir / "main.pyc").write_text("compiled python")
            
            stats = analyze_path(temp_path)
            assert stats.total_files == 1  # Only main.py should be counted
            assert "Python" in stats.languages
