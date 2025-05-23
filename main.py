#!/usr/bin/env python3
"""
Repository Structure Generator with GUI and File Preview

This script generates a markdown file that lists files in a selected directory structure
with description fields for the repository owner to fill in manually.
Includes a preview step to allow users to exclude specific files or directories.
"""

import os
import argparse
from pathlib import Path
import fnmatch
from typing import Set, List, Optional, Dict
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from datetime import datetime

class GitignoreParser:
    """Parse and apply .gitignore rules"""
    
    def __init__(self, gitignore_path: Optional[Path] = None):
        self.patterns = []
        self.negation_patterns = []
        
        if gitignore_path and gitignore_path.exists():
            self._parse_gitignore(gitignore_path)
    
    def _parse_gitignore(self, gitignore_path: Path):
        """Parse .gitignore file and extract patterns"""
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Handle negation patterns (lines starting with !)
                    if line.startswith('!'):
                        self.negation_patterns.append(line[1:])
                    else:
                        self.patterns.append(line)
        except Exception as e:
            print(f"Warning: Could not read .gitignore file: {e}")
    
    def should_ignore(self, file_path: str, is_dir: bool = False) -> bool:
        """Check if a file/directory should be ignored based on gitignore rules"""
        # Normalize path separators
        normalized_path = file_path.replace('\\', '/')
        
        # Check against ignore patterns
        ignored = False
        for pattern in self.patterns:
            if self._matches_pattern(normalized_path, pattern, is_dir):
                ignored = True
                break
        
        # Check negation patterns (! rules)
        if ignored:
            for pattern in self.negation_patterns:
                if self._matches_pattern(normalized_path, pattern, is_dir):
                    ignored = False
                    break
        
        return ignored
    
    def _matches_pattern(self, path: str, pattern: str, is_dir: bool) -> bool:
        """Check if a path matches a gitignore pattern"""
        # Handle directory-only patterns (ending with /)
        if pattern.endswith('/'):
            if not is_dir:
                return False
            pattern = pattern[:-1]
        
        # Handle patterns starting with /
        if pattern.startswith('/'):
            pattern = pattern[1:]
            return fnmatch.fnmatch(path, pattern)
        
        # Handle patterns containing /
        if '/' in pattern:
            return fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path, f"*/{pattern}")
        
        # Simple filename patterns
        return fnmatch.fnmatch(os.path.basename(path), pattern) or fnmatch.fnmatch(path, f"*/{pattern}")

class RepoDocumentationGenerator:
    """Generate markdown documentation template for repository files"""
    
    # Common directories and files to ignore
    DEFAULT_IGNORE_PATTERNS = {
        # Package managers
        'node_modules',
        'bower_components',
        'jspm_packages',
        
        # .NET
        'bin',
        'obj',
        'packages',
        '*.nupkg',
        
        # Python
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.Python',
        'env',
        'venv',
        '.env',
        '.venv',
        'pip-log.txt',
        'pip-delete-this-directory.txt',
        '.tox',
        '.coverage',
        '.pytest_cache',
        'htmlcov',
        '.cache',
        'nosetests.xml',
        'coverage.xml',
        '*.cover',
        '*.log',
        '.git',
        '.nyc_output',
        
        # IDE and editors
        '.vscode',
        '.idea',
        '*.swp',
        '*.swo',
        '*~',
        
        # OS generated files
        '.DS_Store',
        '.DS_Store?',
        '._*',
        '.Spotlight-V100',
        '.Trashes',
        'ehthumbs.db',
        'Thumbs.db',
        
        # Cache and temporary files
        '.cache',
        '.tmp',
        'tmp',
        'temp',
        '*.tmp',
        '*.temp',
        '.sass-cache',
        '.next',
        '.nuxt',
        'dist',
        'build',
        'out',
        
        # Logs
        '*.log',
        'logs',
        'npm-debug.log*',
        'yarn-debug.log*',
        'yarn-error.log*',
        
        # Documentation files (don't document the documentation)
        'README.md',
        'readme.md',
        'README.txt',
        'readme.txt',
        'CHANGELOG.md',
        'changelog.md',
        'LICENSE',
        'license',
        'LICENSE.md',
        'license.md',
        'CONTRIBUTING.md',
        'contributing.md',
    }
    
    def __init__(self, root_path: str, output_file: str = "file_documentation.md"):
        self.root_path = Path(root_path).resolve()
        self.output_file = output_file
        self.gitignore_parser = GitignoreParser(self.root_path / '.gitignore')
        self.file_list = []
        self.excluded_files = set()
        
        if not self.root_path.exists():
            raise FileNotFoundError(f"Directory '{root_path}' does not exist")
        
        if not self.root_path.is_dir():
            raise NotADirectoryError(f"'{root_path}' is not a directory")
    
    def _should_ignore_item(self, item_path: Path, relative_path: str) -> bool:
        """Check if an item should be ignored"""
        item_name = item_path.name
        is_dir = item_path.is_dir()
        
        # Check default ignore patterns
        for pattern in self.DEFAULT_IGNORE_PATTERNS:
            if fnmatch.fnmatch(item_name, pattern) or fnmatch.fnmatch(relative_path, pattern):
                return True
        
        # Check gitignore rules
        if self.gitignore_parser.should_ignore(relative_path, is_dir):
            return True
        
        return False
    
    def collect_all_files(self) -> List[Dict]:
        """Collect all files that would be included in documentation"""
        self.file_list = []
        self._collect_files(self.root_path)
        return self.file_list
    
    def _collect_files(self, current_path: Path, level: int = 0) -> None:
        """Recursively collect all files that should be documented"""
        try:
            items = sorted(current_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
        except PermissionError:
            return
        
        for item in items:
            relative_path = str(item.relative_to(self.root_path))
            
            if self._should_ignore_item(item, relative_path):
                continue
            
            if item.is_file():
                file_info = {
                    'path': relative_path,
                    'name': item.name,
                    'level': level,
                    'directory': str(item.parent.relative_to(self.root_path)) if item.parent != self.root_path else ".",
                    'size': item.stat().st_size,
                    'modified': datetime.fromtimestamp(item.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                }
                self.file_list.append(file_info)
            elif item.is_dir():
                self._collect_files(item, level + 1)
    
    def set_excluded_files(self, excluded_files: Set[str]):
        """Set which files should be excluded from documentation"""
        self.excluded_files = excluded_files
    
    def get_included_files(self) -> List[Dict]:
        """Get list of files that will be included in documentation (not excluded)"""
        return [f for f in self.file_list if f['path'] not in self.excluded_files]
    
    def generate_markdown(self) -> str:
        """Generate the complete markdown documentation template"""
        repo_name = self.root_path.name
        included_files = self.get_included_files()
        
        # Get current timestamp
        current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        markdown_content = [
            f"# File Documentation: {repo_name}",
            "",
            f"**Generated on:** {current_time} UTC",
            f"**Generated by:** jordanboyce",
            f"**Source directory:** `{self.root_path}`",
            f"**Total files documented:** {len(included_files)}",
            "",
            "> **Instructions:** Please fill in the description for each file below. This will help team members understand the purpose and functionality of each file in the repository.",
            "",
            "---",
            "",
        ]
        
        # Group files by directory
        files_by_directory = {}
        for file_info in included_files:
            directory = file_info['directory']
            if directory not in files_by_directory:
                files_by_directory[directory] = []
            files_by_directory[directory].append(file_info)
        
        # Sort directories
        sorted_directories = sorted(files_by_directory.keys(), key=lambda x: (x != ".", x))
        
        for directory in sorted_directories:
            files = files_by_directory[directory]
            
            # Directory header
            if directory == ".":
                markdown_content.extend([
                    "## Root Directory",
                    "",
                ])
            else:
                markdown_content.extend([
                    f"## Directory: `{directory}`",
                    "",
                ])
            
            # Files in this directory
            for file_info in sorted(files, key=lambda x: x['name'].lower()):
                file_name = file_info['name']
                file_path = file_info['path']
                file_size = self._format_file_size(file_info['size'])
                file_modified = file_info['modified']
                
                markdown_content.extend([
                    f"### `{file_name}`",
                    "",
                    f"**Path:** `{file_path}`  ",
                    f"**Size:** {file_size}  ",
                    f"**Last Modified:** {file_modified}",
                    "",
                    "**Description:**",
                    "",
                    "_[Please describe the purpose and functionality of this file]_",
                    "",
                    "**Key Features:**",
                    "",
                    "- _[List main features or functions]_",
                    "- _[Add more items as needed]_",
                    "",
                    "**Dependencies:**",
                    "",
                    "_[List any dependencies or related files]_",
                    "",
                    "---",
                    "",
                ])
        
        # Add footer
        markdown_content.extend([
            "## Documentation Completion Status",
            "",
            "- [ ] All file descriptions completed",
            "- [ ] All key features documented", 
            "- [ ] All dependencies identified",
            "- [ ] Documentation reviewed and approved",
            "",
            f"**Last updated:** _[Date]_  ",
            f"**Reviewed by:** _[Name]_",
        ])
        
        return "\n".join(markdown_content)
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def save_markdown(self) -> str:
        """Save the markdown content to a file and return the file path"""
        content = self.generate_markdown()
        
        output_path = Path(self.output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(output_path.resolve())

class FilePreviewWindow:
    """Window to preview and select files for documentation"""
    
    def __init__(self, parent, files_list: List[Dict], callback):
        self.parent = parent
        self.files_list = files_list
        self.callback = callback
        self.excluded_files = set()
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("File Preview - Select Files to Document")
        self.window.geometry("900x700")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        self.populate_file_list()
        
    def setup_ui(self):
        """Set up the preview window UI"""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Files to be Documented", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Instructions
        instructions_text = """Review the files below. Use the controls to select which files to include in documentation.
        
• Click files to select/highlight them (Ctrl+Click for multiple selection)
• Double-click any file to toggle its inclusion status
• Use the buttons below to perform actions on selected files"""
        
        instructions = ttk.Label(main_frame, text=instructions_text, justify=tk.LEFT, wraplength=850)
        instructions.pack(pady=(0, 15))
        
        # Stats frame
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_label = ttk.Label(stats_frame, text="", font=("Arial", 9, "bold"))
        self.stats_label.pack(side=tk.LEFT)
        
        self.selection_label = ttk.Label(stats_frame, text="", foreground="blue")
        self.selection_label.pack(side=tk.RIGHT)
        
        # Control buttons frame - reorganized for better UX
        control_frame = ttk.LabelFrame(main_frame, text="Selection Controls", padding="5")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Top row - global actions
        global_frame = ttk.Frame(control_frame)
        global_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(global_frame, text="✓ Include All Files", 
                  command=self.select_all, width=15).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(global_frame, text="✗ Exclude All Files", 
                  command=self.deselect_all, width=15).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(global_frame, text="⇄ Invert All", 
                  command=self.toggle_all_selection, width=12).pack(side=tk.LEFT)
        
        # Bottom row - selection-specific actions
        selection_frame = ttk.Frame(control_frame)
        selection_frame.pack(fill=tk.X)
        
        ttk.Label(selection_frame, text="Selected files:", 
                 font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        
        self.include_selected_btn = ttk.Button(selection_frame, text="✓ Include Selected", 
                                              command=self.include_selected, state="disabled")
        self.include_selected_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.exclude_selected_btn = ttk.Button(selection_frame, text="✗ Exclude Selected", 
                                              command=self.exclude_selected, state="disabled")
        self.exclude_selected_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.toggle_selected_btn = ttk.Button(selection_frame, text="⇄ Toggle Selected", 
                                             command=self.toggle_selected, state="disabled")
        self.toggle_selected_btn.pack(side=tk.LEFT)
        
        # Search frame
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="🔍 Filter:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_files)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        clear_filter_btn = ttk.Button(search_frame, text="Clear", 
                                     command=lambda: self.search_var.set(""))
        clear_filter_btn.pack(side=tk.LEFT)
        
        # File list frame with scrollbars
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create treeview with scrollbars
        self.tree = ttk.Treeview(list_frame, columns=('Size', 'Modified', 'Directory'), 
                                show='tree headings', selectmode='extended')
        
        # Configure columns
        self.tree.heading('#0', text='File Name')
        self.tree.heading('Size', text='Size')
        self.tree.heading('Modified', text='Last Modified')
        self.tree.heading('Directory', text='Directory')
        
        self.tree.column('#0', width=350)
        self.tree.column('Size', width=100)
        self.tree.column('Modified', width=150)
        self.tree.column('Directory', width=250)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind('<Double-1>', self.on_item_double_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_selection_change)
        
        # Keyboard shortcuts
        self.tree.bind('<space>', self.on_space_key)
        self.tree.bind('<Return>', self.on_enter_key)
        
        # Bottom buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Generate Documentation", 
                  command=self.confirm).pack(side=tk.RIGHT)
        
    def populate_file_list(self):
        """Populate the file list in the treeview"""
        # Group files by directory
        files_by_directory = {}
        for file_info in self.files_list:
            directory = file_info['directory']
            if directory not in files_by_directory:
                files_by_directory[directory] = []
            files_by_directory[directory].append(file_info)
        
        # Sort directories
        sorted_directories = sorted(files_by_directory.keys(), key=lambda x: (x != ".", x))
        
        self.file_items = {}  # Store item IDs for each file path
        
        for directory in sorted_directories:
            files = files_by_directory[directory]
            
            # Create directory node
            dir_display = "Root Directory" if directory == "." else directory
            dir_item = self.tree.insert('', 'end', text=f"📁 {dir_display}", open=True,
                                       values=('', '', ''), tags=('directory',))
            
            # Add files under directory
            for file_info in sorted(files, key=lambda x: x['name'].lower()):
                file_size = self._format_file_size(file_info['size'])
                file_item = self.tree.insert(dir_item, 'end', 
                                           text=f"✅ {file_info['name']}", 
                                           values=(file_size, file_info['modified'], file_info['directory']),
                                           tags=('file', 'selected'))
                self.file_items[file_info['path']] = file_item
        
        # Configure tags
        self.tree.tag_configure('selected', foreground='black')
        self.tree.tag_configure('deselected', foreground='gray')
        self.tree.tag_configure('directory', font=('Arial', 9, 'bold'))
        
        self.update_stats()
        self.update_selection_info()
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def get_file_path_from_item(self, item):
        """Get file path from tree item ID"""
        for path, item_id in self.file_items.items():
            if item_id == item:
                return path
        return None
    
    def get_selected_file_items(self):
        """Get currently selected file items (not directories)"""
        selected_items = self.tree.selection()
        file_items = []
        
        for item in selected_items:
            if 'file' in self.tree.item(item, 'tags'):
                file_items.append(item)
        
        return file_items
    
    def on_selection_change(self, event):
        """Handle selection change in treeview"""
        self.update_selection_info()
    
    def update_selection_info(self):
        """Update selection-specific button states and info"""
        selected_files = self.get_selected_file_items()
        has_selection = len(selected_files) > 0
        
        # Update button states
        self.include_selected_btn.config(state="normal" if has_selection else "disabled")
        self.exclude_selected_btn.config(state="normal" if has_selection else "disabled")
        self.toggle_selected_btn.config(state="normal" if has_selection else "disabled")
        
        # Update selection info
        if has_selection:
            self.selection_label.config(text=f"{len(selected_files)} file(s) highlighted")
        else:
            self.selection_label.config(text="No files selected")
    
    def on_item_double_click(self, event):
        """Handle double-click on tree item"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item and 'file' in self.tree.item(item, 'tags'):
            self.toggle_file_selection(item)
    
    def on_space_key(self, event):
        """Handle spacebar key - toggle selected files"""
        self.toggle_selected()
    
    def on_enter_key(self, event):
        """Handle enter key - toggle selected files"""
        self.toggle_selected()
    
    def toggle_file_selection(self, item):
        """Toggle selection state of a specific file"""
        file_path = self.get_file_path_from_item(item)
        
        if file_path:
            if file_path in self.excluded_files:
                # Include the file
                self.excluded_files.remove(file_path)
                self.tree.item(item, text=f"✅ {Path(file_path).name}", tags=('file', 'selected'))
            else:
                # Exclude the file
                self.excluded_files.add(file_path)
                self.tree.item(item, text=f"❌ {Path(file_path).name}", tags=('file', 'deselected'))
            
            self.update_stats()
    
    def include_selected(self):
        """Include all currently highlighted files"""
        selected_items = self.get_selected_file_items()
        
        for item in selected_items:
            file_path = self.get_file_path_from_item(item)
            if file_path and file_path in self.excluded_files:
                self.excluded_files.remove(file_path)
                self.tree.item(item, text=f"✅ {Path(file_path).name}", tags=('file', 'selected'))
        
        self.update_stats()
    
    def exclude_selected(self):
        """Exclude all currently highlighted files"""
        selected_items = self.get_selected_file_items()
        
        for item in selected_items:
            file_path = self.get_file_path_from_item(item)
            if file_path and file_path not in self.excluded_files:
                self.excluded_files.add(file_path)
                self.tree.item(item, text=f"❌ {Path(file_path).name}", tags=('file', 'deselected'))
        
        self.update_stats()
    
    def toggle_selected(self):
        """Toggle inclusion status of all currently highlighted files"""
        selected_items = self.get_selected_file_items()
        
        for item in selected_items:
            self.toggle_file_selection(item)
    
    def select_all(self):
        """Include all files"""
        self.excluded_files.clear()
        for file_path, item in self.file_items.items():
            self.tree.item(item, text=f"✅ {Path(file_path).name}", tags=('file', 'selected'))
        self.update_stats()
    
    def deselect_all(self):
        """Exclude all files"""
        for file_path, item in self.file_items.items():
            self.excluded_files.add(file_path)
            self.tree.item(item, text=f"❌ {Path(file_path).name}", tags=('file', 'deselected'))
        self.update_stats()
    
    def toggle_all_selection(self):
        """Toggle inclusion status of ALL files"""
        for file_path, item in self.file_items.items():
            if file_path in self.excluded_files:
                self.excluded_files.remove(file_path)
                self.tree.item(item, text=f"✅ {Path(file_path).name}", tags=('file', 'selected'))
            else:
                self.excluded_files.add(file_path)
                self.tree.item(item, text=f"❌ {Path(file_path).name}", tags=('file', 'deselected'))
        self.update_stats()
    
    def filter_files(self, *args):
        """Filter files based on search term"""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            # Show all items
            for item in self.tree.get_children():
                self._show_item_recursive(item)
        else:
            # Filter items
            for item in self.tree.get_children():
                self._filter_item_recursive(item, search_term)
    
    def _show_item_recursive(self, item):
        """Recursively show all items"""
        # This is a simplified approach - tkinter treeview doesn't have built-in hide/show
        # For now, we'll keep all items visible and let users use Ctrl+F or similar
        pass
    
    def _filter_item_recursive(self, item, search_term):
        """Recursively filter items based on search term"""
        # This would require more complex implementation to actually hide/show items
        # For now, we'll keep it simple and highlight matching items
        pass
    
    def update_stats(self):
        """Update the statistics label"""
        total_files = len(self.files_list)
        selected_files = total_files - len(self.excluded_files)
        self.stats_label.config(text=f"📊 Files: {selected_files} included, {len(self.excluded_files)} excluded, {total_files} total")
    
    def confirm(self):
        """User confirmed the selection"""
        if len(self.excluded_files) == len(self.files_list):
            messagebox.showwarning("No Files Selected", 
                                 "You must include at least one file to generate documentation.")
            return
        
        self.callback(self.excluded_files)
        self.window.destroy()
    
    def cancel(self):
        """User cancelled"""
        self.window.destroy()

class DocumentationGeneratorGUI:
    """GUI application for the documentation generator"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Repository Documentation Generator")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Variables
        self.selected_directory = tk.StringVar()
        self.output_filename = tk.StringVar(value="file_documentation.md")
        self.status_text = tk.StringVar(value="Select a directory to begin...")
        self.generator = None
        self.excluded_files = set()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Repository Documentation Generator", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Directory selection
        ttk.Label(main_frame, text="Select Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        directory_frame = ttk.Frame(main_frame)
        directory_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        directory_frame.columnconfigure(0, weight=1)
        
        self.directory_entry = ttk.Entry(directory_frame, textvariable=self.selected_directory, 
                                        state="readonly", width=50)
        self.directory_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        browse_button = ttk.Button(directory_frame, text="Browse...", command=self.browse_directory)
        browse_button.grid(row=0, column=1)
        
        # Output filename
        ttk.Label(main_frame, text="Output File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        output_entry = ttk.Entry(main_frame, textvariable=self.output_filename, width=50)
        output_entry.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Preview and Generate buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        self.preview_button = ttk.Button(button_frame, text="Preview Files", 
                                        command=self.preview_files, state="disabled")
        self.preview_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.generate_button = ttk.Button(button_frame, text="Generate Documentation", 
                                         command=self.generate_documentation, state="disabled")
        self.generate_button.pack(side=tk.LEFT)
        
        # Description
        description_text = """
This tool will generate a markdown documentation template for your repository.

WORKFLOW:
1. Select a directory containing your code repository
2. Click "Preview Files" to see which files will be included
3. In the preview window:
   • Click files to select/highlight them (Ctrl+Click for multiple)
   • Use "Include/Exclude Selected" buttons to modify highlighted files
   • Double-click any file to toggle its inclusion status
   • Use keyboard shortcuts: Spacebar or Enter to toggle selected files
4. Click "Generate Documentation" to create the markdown file

The generated file includes template sections for descriptions, key features, 
and dependencies for each selected file, organized by directory structure.

The tool respects .gitignore files and excludes common package/cache directories.
        """.strip()
        
        description_label = ttk.Label(main_frame, text=description_text, justify=tk.LEFT, 
                                     wraplength=650, background="lightgray", padding="10")
        description_label.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
        # Status
        status_label = ttk.Label(main_frame, textvariable=self.status_text, foreground="blue")
        status_label.grid(row=5, column=0, columnspan=3, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
    def browse_directory(self):
        """Open directory selection dialog"""
        directory = filedialog.askdirectory(
            title="Select Repository Directory",
            initialdir=os.getcwd()
        )
        
        if directory:
            self.selected_directory.set(directory)
            self.preview_button.config(state="normal")
            self.generate_button.config(state="disabled")  # Reset generate button
            self.status_text.set(f"Selected: {directory}")
            
            # Update output filename based on directory name
            dir_name = Path(directory).name
            self.output_filename.set(f"{dir_name}_documentation.md")
            
            # Reset excluded files
            self.excluded_files = set()
    
    def preview_files(self):
        """Show file preview window"""
        try:
            directory = self.selected_directory.get()
            self.generator = RepoDocumentationGenerator(directory, self.output_filename.get())
            
            self.status_text.set("Scanning files...")
            self.progress.start()
            
            # Collect files in background thread
            thread = threading.Thread(target=self._collect_files_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while scanning files:\n\n{e}")
    
    def _collect_files_thread(self):
        """Collect files in background thread"""
        try:
            files_list = self.generator.collect_all_files()
            # Update UI in main thread
            self.root.after(0, self._show_file_preview, files_list)
        except Exception as e:
            self.root.after(0, self._preview_error, str(e))
    
    def _show_file_preview(self, files_list):
        """Show the file preview window"""
        self.progress.stop()
        if not files_list:
            self.status_text.set("No files found to document")
            messagebox.showinfo("No Files", "No files were found that can be documented in the selected directory.")
            return
        
        self.status_text.set(f"Found {len(files_list)} files. Review and select files to document.")
        
        # Show preview window
        FilePreviewWindow(self.root, files_list, self._on_files_selected)
    
    def _preview_error(self, error_message):
        """Handle preview error"""
        self.progress.stop()
        self.status_text.set("Error occurred while scanning files")
        messagebox.showerror("Error", f"An error occurred while scanning files:\n\n{error_message}")
    
    def _on_files_selected(self, excluded_files):
        """Callback when user has selected files"""
        self.excluded_files = excluded_files
        self.generator.set_excluded_files(excluded_files)
        
        included_count = len(self.generator.get_included_files())
        self.status_text.set(f"Ready to generate documentation for {included_count} files")
        self.generate_button.config(state="normal")
    
    def generate_documentation(self):
        """Generate the documentation"""
        if not self.generator:
            messagebox.showerror("Error", "Please preview files first before generating documentation.")
            return
        
        self.generate_button.config(state="disabled")
        self.preview_button.config(state="disabled")
        self.progress.start()
        self.status_text.set("Generating documentation...")
        
        # Run generation in separate thread to keep UI responsive
        thread = threading.Thread(target=self._generate_documentation_thread)
        thread.daemon = True
        thread.start()
    
    def _generate_documentation_thread(self):
        """Generate documentation in background thread"""
        try:
            output_path = self.generator.save_markdown()
            # Update UI in main thread
            self.root.after(0, self._generation_complete, output_path)
        except Exception as e:
            # Update UI in main thread
            self.root.after(0, self._generation_error, str(e))
    
    def _generation_complete(self, output_path):
        """Handle successful generation"""
        self.progress.stop()
        self.preview_button.config(state="normal")
        self.generate_button.config(state="normal")
        
        included_count = len(self.generator.get_included_files())
        self.status_text.set(f"Documentation generated successfully for {included_count} files!")
        
        messagebox.showinfo("Success", 
                           f"Documentation template generated!\n\n"
                           f"Files documented: {included_count}\n"
                           f"File saved to: {output_path}\n\n"
                           f"Please open the file and fill in the descriptions for each file.")
    
    def _generation_error(self, error_message):
        """Handle generation error"""
        self.progress.stop()
        self.preview_button.config(state="normal")
        self.generate_button.config(state="normal")
        self.status_text.set("Error occurred during generation")
        
        messagebox.showerror("Error", f"An error occurred:\n\n{error_message}")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    """Main function to handle command line arguments and GUI"""
    parser = argparse.ArgumentParser(
        description="Generate a markdown documentation template for repository files"
    )
    
    parser.add_argument(
        "directory",
        nargs='?',
        help="Path to the repository directory to analyze (optional - GUI will open if not provided)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="file_documentation.md",
        help="Output markdown file name (default: file_documentation.md)"
    )
    
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Force GUI mode even if directory is provided"
    )
    
    args = parser.parse_args()
    
    # Use GUI if no directory provided or --gui flag is used
    if not args.directory or args.gui:
        try:
            app = DocumentationGeneratorGUI()
            app.run()
            return 0
        except Exception as e:
            print(f"GUI Error: {e}")
            return 1
    
    # Command line mode (simplified - no preview in CLI)
    try:
        generator = RepoDocumentationGenerator(args.directory, args.output)
        generator.collect_all_files()
        output_path = generator.save_markdown()
        print(f"Documentation template generated successfully!")
        print(f"File saved to: {output_path}")
        print(f"Files documented: {len(generator.get_included_files())}")
        print("\nPlease open the file and fill in the descriptions for each file.")
        
    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
