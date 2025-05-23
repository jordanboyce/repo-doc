# Repository Documentation Generator

A powerful Python tool that automatically generates comprehensive markdown documentation templates for your code repositories. The tool provides both a user-friendly GUI and command-line interface, allowing you to create structured documentation with customizable file selection and intelligent filtering.

## 🚀 Features

### Core Functionality
- **Interactive GUI** with file explorer integration
- **File Preview System** - Review and select which files to document
- **Smart Filtering** - Respects `.gitignore` files and excludes common package/cache directories
- **Structured Output** - Generates organized markdown with description templates
- **Cross-Platform** - Works on Windows, macOS, and Linux

### File Management
- **Gitignore Integration** - Automatically respects repository `.gitignore` rules
- **Package Directory Exclusion** - Skips `node_modules`, `__pycache__`, `bin`, `obj`, etc.
- **Cache File Filtering** - Excludes temporary files, logs, and IDE configurations
- **Custom Exclusions** - Manual file selection in preview mode

### Documentation Features
- **Organized by Directory** - Files grouped by their directory structure
- **File Metadata** - Includes file size, modification date, and path information
- **Template Sections** - Pre-formatted sections for descriptions, features, and dependencies
- **Completion Tracking** - Built-in checklist for documentation progress

## 📋 Requirements

- **Python 3.6+**
- **tkinter** (usually included with Python)
- Built-in Python libraries: `pathlib`, `fnmatch`, `threading`, `argparse`

### System-Specific Notes

**Linux Users**: Some distributions don't include tkinter by default:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install tkinter

# Fedora
sudo dnf install python3-tkinter
```

## 🛠 Installation

### Option 1: Virtual Environment (Recommended)

```bash
# Clone or download the script
mkdir repo-doc-generator
cd repo-doc-generator

# Create virtual environment
python3 -m venv repo_doc_env

# Activate virtual environment
# Linux/macOS:
source repo_doc_env/bin/activate
# Windows:
repo_doc_env\Scripts\activate

# Save the script as repo_structure_generator.py
# Then run it
python repo_structure_generator.py
```

### Option 2: Direct Usage

```bash
# Simply save the script and run
python repo_structure_generator.py
```

### Quick Setup Script

**Linux/macOS:**
```bash
#!/bin/bash
# setup.sh
echo "Setting up Repository Documentation Generator..."

python3 -m venv repo_doc_env
source repo_doc_env/bin/activate

python3 -c "import tkinter; print('✓ tkinter available')" || {
    echo "❌ tkinter not found. Install with:"
    echo "Ubuntu/Debian: sudo apt-get install python3-tk"
    exit 1
}

echo "✓ Setup complete! Run: python repo_structure_generator.py"
```

**Windows:**
```batch
@echo off
REM setup.bat
echo Setting up Repository Documentation Generator...

python -m venv repo_doc_env
call repo_doc_env\Scripts\activate.bat

python -c "import tkinter; print('✓ tkinter available')" || (
    echo ❌ tkinter not found. Please install Python with tkinter support.
    exit /b 1
)

echo ✓ Setup complete! Run: python repo_structure_generator.py
```

## 🖥 Usage

### GUI Mode (Default)

```bash
# Launch GUI interface
python repo_structure_generator.py

# Force GUI even with directory argument
python repo_structure_generator.py --gui
```

**GUI Workflow:**
1. **Select Directory**: Click "Browse..." to choose your repository
2. **Preview Files**: Click "Preview Files" to see what will be documented
3. **Customize Selection**: In the preview window:
   - ✅ Check/uncheck files to include/exclude
   - Use "Select All", "Deselect All", or "Toggle Selection"
   - Filter files using the search box
   - Double-click items to toggle selection
4. **Generate**: Click "Generate Documentation" to create the markdown file

### Command Line Mode

```bash
# Basic usage
python repo_structure_generator.py /path/to/your/repo

# Custom output file
python repo_structure_generator.py /path/to/your/repo -o custom_docs.md

# Show help
python repo_structure_generator.py --help
```

## 📁 File Filtering

### Automatically Excluded

The tool intelligently excludes common files and directories:

**Package Managers:**
- `node_modules`, `bower_components` (JavaScript)
- `bin`, `obj`, `packages` (.NET)
- `__pycache__`, `venv`, `.pytest_cache` (Python)

**Development Files:**
- `.git`, `.vscode`, `.idea`
- `*.log`, `*.tmp`, cache directories
- OS files (`.DS_Store`, `Thumbs.db`)

**Documentation Files:**
- `README.md`, `LICENSE`, `CHANGELOG.md`

### Gitignore Integration

The tool automatically reads and respects `.gitignore` files:
- Supports standard gitignore patterns
- Handles negation rules (`!` prefix)
- Processes directory-specific rules

## 📄 Output Format

### Generated Documentation Structure

```markdown
# File Documentation: ProjectName

**Generated on:** 2025-05-23 21:35:56 UTC
**Generated by:** jordanboyce
**Source directory:** `/path/to/project`
**Total files documented:** 15

## Root Directory

### `main.py`

**Path:** `main.py`
**Size:** 2.4 KB
**Last Modified:** 2025-05-23 15:30:22

**Description:**

_[Please describe the purpose and functionality of this file]_

**Key Features:**

- _[List main features or functions]_
- _[Add more items as needed]_

**Dependencies:**

_[List any dependencies or related files]_

---
```

### Completion Tracking

Each generated file includes:
- [ ] All file descriptions completed
- [ ] All key features documented
- [ ] All dependencies identified
- [ ] Documentation reviewed and approved

## 🎯 Use Cases

### 1. New Team Member Onboarding
Generate documentation templates to help new developers understand your codebase structure.

### 2. Code Review Preparation
Create comprehensive file documentation before major code reviews.

### 3. Project Handover
Document your project structure when transferring to another team.

### 4. Architecture Documentation
Generate templates for architectural documentation and system overviews.

## ⚙️ Configuration

### Default Ignore Patterns

You can modify the `DEFAULT_IGNORE_PATTERNS` set in the `RepoDocumentationGenerator` class:

```python
DEFAULT_IGNORE_PATTERNS = {
    'node_modules',
    '__pycache__',
    '.git',
    # Add your custom patterns here
}
```

### Custom Gitignore Location

The tool automatically looks for `.gitignore` in the repository root. For custom locations:

```python
# Modify the GitignoreParser initialization
gitignore_parser = GitignoreParser(custom_path / '.gitignore')
```

## 🔧 Troubleshooting

### Common Issues

**1. "tkinter not found" Error**
```bash
# Solution varies by OS (see Installation section above)
sudo apt-get install python3-tk  # Ubuntu/Debian
```

**2. "Permission Denied" Errors**
- Ensure you have read permissions for the target directory
- Some system directories may be restricted

**3. GUI Not Opening**
```bash
# Test tkinter installation
python3 -c "import tkinter; tkinter.Tk()"
```

**4. No Files Found**
- Check if your directory contains files that aren't filtered out
- Verify `.gitignore` patterns aren't too restrictive
- Use the preview to see what files are being excluded

### Debug Mode

For troubleshooting, you can add debug output:

```python
# Add to the beginning of main()
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

### Development Setup

```bash
# Clone/download the project
git clone <repository-url>
cd repo-documentation-generator

# Create development environment
python3 -m venv dev-env
source dev-env/bin/activate  # Linux/macOS
# dev-env\Scripts\activate   # Windows

# Install development dependencies (if any)
pip install -r requirements-dev.txt  # If you create this file
```

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Add docstrings for all classes and functions
- Keep functions focused and single-purpose

### Testing

```bash
# Manual testing
python repo_structure_generator.py --gui
python repo_structure_generator.py test-directory
```

### Feature Requests

When suggesting new features:
1. Describe the use case
2. Provide example scenarios
3. Consider backward compatibility
4. Think about cross-platform implications

## 📝 Examples

### Example 1: Python Project

```bash
# Generate docs for a Python project
python repo_structure_generator.py my-python-app

# Output: my-python-app_documentation.md
```

### Example 2: Web Application

```bash
# Document a React/Node.js app (automatically excludes node_modules)
python repo_structure_generator.py my-web-app -o webapp-docs.md
```

### Example 3: Multi-language Project

```bash
# Document a complex project with multiple languages
python repo_structure_generator.py enterprise-app
# Use preview mode to select only relevant files
```

## 📊 File Statistics

The tool provides insights about your project:
- Total files scanned
- Files included/excluded
- Directory structure overview
- File size and modification information

## 🚀 Future Enhancements

Potential improvements for future versions:
- **Code Analysis**: Detect function/class definitions
- **Dependency Mapping**: Automatically detect file dependencies
- **Export Formats**: Support for other documentation formats
- **Template Customization**: User-defined documentation templates
- **Git Integration**: Show commit history and authors

## 📄 License

This project is released under the MIT License. Feel free to use, modify, and distribute as needed.

## 👨‍💻 Author

**jordanboyce**
- Created: 2025-05-23
- Last Updated: 2025-05-23 21:35:56 UTC

## 🙏 Acknowledgments

- Built with Python's excellent standard library
- GUI powered by tkinter
- Inspired by the need for better code documentation workflows

---

**Happy Documenting! 📚**

For issues, feature requests, or contributions, please feel free to reach out or submit a pull request.
