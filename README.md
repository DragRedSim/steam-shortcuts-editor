# 🎮 Steam Shortcuts Editor

A simple GUI application to view and edit Steam shortcuts (non-Steam games/applications) using Python.

## Overview

This tool allows you to:
- View all your Steam shortcuts in a single interface
- Edit shortcut properties (name, executable path, icons, etc.)
- Save changes directly to Steam's shortcuts.vdf file
- Automatically locate your Steam shortcuts file on various platforms

## Requirements

- Python 3.6+
- uv (Python package manager)
- PySide6 (Qt for Python)
- vdf library

## Installation

1. Make sure you have Python installed
2. Install uv (recommended package manager)
3. Clone this repository
4. Run the setup script:
   ```
   chmod +x run.sh
   ./run.sh
   ```

The script will automatically:
- Create a virtual environment
- Install required dependencies
- Launch the application

### Manual Setup

If you prefer to set up manually:

1. Create a virtual environment:
   ```
   uv venv
   source .venv/bin/activate.fish  # For fish shell
   # OR
   source .venv/bin/activate  # For bash/zsh
   ```
2. Install required packages:
   ```
   uv pip install -r requirements.txt
   ```

## Usage

1. Run the editor:
   ```
   ./run.sh
   ```
   Or manually:
   ```
   .venv/bin/python steam_shortcuts_editor.py
   ```

2. The editor will automatically locate and load your Steam shortcuts.vdf file
3. If automatic detection fails, use the "Browse..." button to select your shortcuts.vdf file manually

## Features

- List of all Steam shortcuts
- Edit all properties of each shortcut
- Auto-convert property values to appropriate types
- Save changes directly back to Steam
- User-friendly interface with resizable panels
- Automatic shortcuts.vdf file detection

## Supported Platforms

- Linux (primary development platform)
- Windows (should work, but less tested)
- macOS (should work, but less tested)

The application automatically attempts to find your Steam shortcuts.vdf file in the standard locations:

- Linux: `~/.steam/steam/userdata/<user_id>/config/shortcuts.vdf` or `~/.local/share/Steam/userdata/<user_id>/config/shortcuts.vdf`
- Windows: `C:/Program Files (x86)/Steam/userdata/<user_id>/config/shortcuts.vdf`
- macOS: `~/Library/Application Support/Steam/userdata/<user_id>/config/shortcuts.vdf`

## Troubleshooting

If the application fails to start or find your shortcuts file:

1. Ensure Steam is installed and you have added at least one non-Steam game
2. Check if your shortcuts.vdf file exists in one of the locations mentioned above
3. Use the "Browse..." button to manually locate your shortcuts.vdf file
4. Make sure you have the required dependencies installed

## Development

To contribute to this project:

1. Fork the repository
2. Make your changes
3. Submit a pull request

## License

This project is open source and available for anyone to use and modify. 