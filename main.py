# Import necessary modules
import sys
import tiktoken
import os

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
        int: The total number of tokens in the file.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'", file=sys.stderr)
        return -1 # Indicate an error

    try:
        # Read the content of the file
        with open(file_path, 'r', encoding='utf-8') as f:
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
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return -1

if __name__ == "__main__":
    # Check if a file path argument is provided
    if len(sys.argv) < 2:
        print("Usage: python your_script_name.py <path_to_file>", file=sys.stderr)
        print("Example: python count_tokens.py my_document.txt", file=sys.stderr)
        sys.exit(1) # Exit with an error code

    # Get the file path from the command-line arguments
    input_file_path = sys.argv[1]

    # Count tokens
    token_count = count_tokens_in_file(input_file_path)

    if token_count != -1:
        print(f"File: '{input_file_path}'")
        print(f"Encoding used: cl100k_base")
        print(f"Total tokens: {token_count}")
    else:
        sys.exit(1) # Exit with an error if token counting failed
