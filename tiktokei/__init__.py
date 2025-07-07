"""
TikTokei - A command-line tool to count tokens in text files using tiktoken.
"""

__version__ = "0.1.0"
__author__ = "Ang Chin Han"
__email__ = "ang.chin.han@gmail.com"

from .core import count_tokens_in_file

__all__ = ["count_tokens_in_file"]
