# TikTokei

A command-line tool to count tokens in text files using OpenAI's tiktoken library. Works like `tokei` but for token counting instead of lines of code.

## Features

- **Recursive directory analysis**: Analyze entire projects and subdirectories
- **Multiple encoding support**: Use various tiktoken encodings (cl100k_base, p50k_base, r50k_base, etc.)
- **Language detection**: Automatically detect file types and group statistics by language
- **Tokei-style output**: Clean, organized summary tables showing files, lines, tokens, and bytes
- **Individual file stats**: Option to show per-file token counts
- **Smart filtering**: Automatically ignores common build artifacts, dependencies, and version control files
- **Stdin support**: Read from stdin for pipe operations
- **Quiet mode**: Perfect for scripting and automation

## Installation

### Using uvx without installation

Use `uvx --from "git+https://github.com/angch/tiktokei@main" tiktokei`

Example:

```bash
 % uvx --from "git+https://github.com/angch/tiktokei@main" tiktokei .
 Updated https://github.com/angch/tiktokei (de4b857)
   Built tiktokei @ git+https://github.com/angch/tiktokei@de4b8577316e26d98172ba1c06ebcbff9b434df9
Installed 8 packages in 14ms
Directory: /Users/angch/build/tiktokei
Encoding used: cl100k_base

================================================================================
 Language            Files        Lines       Tokens        Bytes
================================================================================
 Python                 98      47,708     449,945   1,541,083
 Other                  65       8,990     267,744     530,319
 Text                    9         239       2,613      12,853
 Markdown                2         213       1,416       6,066
 Shell                   1         124       1,075       4,180
 JavaScript              1         110         840       3,655
 PowerShell              1          82         675       2,762
 TOML                    1          74         558       1,831
 Config                  1           6          54         177
 JSON                    1           1          23          73
--------------------------------------------------------------------------------
 Total                 180      57,547     724,943   2,102,999
================================================================================
```

### Using uv (recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install the project
git clone <your-repo-url>
cd tiktokei

# Install dependencies and the project
uv sync
```

### Using pip

```bash
# Install from source
pip install -e .

# Or install dependencies manually
pip install tiktoken
```

## Usage

### Basic usage

```bash
# Count tokens in current directory (recursive)
tiktokei

# Count tokens in a specific directory
tiktokei src/

# Count tokens in a single file
tiktokei document.txt

# Use a different encoding
tiktokei --encoding p50k_base

# Show individual file statistics
tiktokei --files

# Read from stdin
echo "Hello, world!" | tiktokei --stdin

# Quiet mode (only output total token count)
tiktokei --quiet
```

### Available commands

```bash
# Show help
tiktokei --help

# List available encodings
tiktokei --list-encodings

# Show version
tiktokei --version

# Show per-file statistics
tiktokei --files
```

### Example Output

```
Directory: /home/user/myproject
Encoding used: cl100k_base

================================================================================
 Language            Files        Lines       Tokens        Bytes
================================================================================
 Python                 12        1,847        3,421       67,890
 JavaScript              8        1,203        2,156       45,782
 Markdown                3          456          892       12,345
 JSON                    2           89          234        3,456
 YAML                    1           34           67          789
--------------------------------------------------------------------------------
 Total                  26        3,629        6,770      130,262
================================================================================
```

## Encodings

The tool supports various tiktoken encodings:

- **cl100k_base**: Used by GPT-4, GPT-3.5-Turbo (default)
- **p50k_base**: Used by Codex, text-davinci-002, text-davinci-003
- **r50k_base**: Used by GPT-3 models
- **gpt2**: Used by GPT-2 models

## Supported Languages

TikTokei automatically detects and categorizes files by language based on file extensions:

**Programming Languages**: Python, JavaScript, TypeScript, Java, C/C++, C#, PHP, Ruby, Go, Rust, Swift, Kotlin, and many more

**Web Technologies**: HTML, CSS, SCSS, Vue, Svelte

**Data/Config**: JSON, YAML, TOML, SQL, XML

**Documentation**: Markdown, reStructuredText, LaTeX

**Other**: Dockerfiles, Makefiles, Shell scripts, and more

## Ignored Files and Directories

TikTokei automatically ignores common build artifacts and directories:
- Version control: `.git`, `.svn`, `.hg`
- Dependencies: `node_modules`, `__pycache__`, `target`, `build`, `dist`
- IDE files: `.vscode`, `.idea`, `.vs`
- Temporary files and caches

## Development

### Setting up development environment

```bash
# Install with development dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Format code
uv run black .

# Lint code
uv run ruff check .
```

### Project structure

```
tiktokei/
├── tiktokei/
│   ├── __init__.py
│   ├── core.py      # Core token counting and analysis functionality
│   └── cli.py       # Command-line interface
├── tests/
│   └── ...
├── pyproject.toml   # Project configuration
└── README.md
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Requirements

- Python 3.8+
- tiktoken
