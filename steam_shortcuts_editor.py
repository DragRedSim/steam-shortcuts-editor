import vdf
import sys
import json
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QListView, QFrame, QScrollArea, QPushButton,
    QLineEdit, QTextEdit, QMessageBox, QGridLayout, QSplitter,
    QFileDialog, QRadioButton, QAbstractItemView, QButtonGroup
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, QItemSelectionModel, QItemSelection
import ctypes

class SteamShortcutsEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Default path (will be set properly in find_shortcuts_path)
        self.shortcuts_path = None
        
        # Set up the UI
        self.setWindowTitle("Steam Shortcuts Editor")
        self.setMinimumSize(900, 600)
        
        # Try to automatically find the shortcuts.vdf path
        self.enable_save = self.find_shortcuts_path()

        # Load the data if path exists
        if self.shortcuts_path:
            self.load_data()
        
        # Create the UI
        self.setup_ui()
    
    def find_shortcuts_path(self):
        """Try to automatically locate the shortcuts.vdf file"""
        # Common locations for Steam userdata
        possible_locations = [
            Path.home() / ".steam/steam/userdata",  # Linux
            Path.home() / ".local/share/Steam/userdata",  # Alternative Linux
            Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Steam/userdata",  # Windows
            Path.home() / "Library/Application Support/Steam/userdata"  # macOS
        ]
        
        for location in possible_locations:
            if location.exists() and location.is_dir():
                # Look for userdata directories
                for user_dir in location.iterdir():
                    if user_dir.is_dir():
                        # Check for shortcuts.vdf
                        shortcuts_file = user_dir / "config" / "shortcuts.vdf"
                        if shortcuts_file.exists():
                            self.shortcuts_path = str(shortcuts_file)
                            return True
        
        return False
    
    def load_data(self):
        """Load data from shortcuts.vdf file"""
        try:
            with open(self.shortcuts_path, 'rb') as f:
                self.data = vdf.binary_load(f)
            self.original_data = self.data.copy()  # Keep a copy for comparison
            self.enable_save = True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load shortcuts file: {e}")
            self.data = {"shortcuts": {}}
            self.original_data = self.data.copy()
            self.enable_save = False
        
        try:
            self.save_button.isEnabled(self.enable_save)
        except:
            pass
    
    def setup_ui(self):
        """Set up the main UI components"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create path selection widget
        path_widget = QWidget()
        path_layout = QHBoxLayout(path_widget)
        path_layout.setContentsMargins(0, 0, 0, 0)
        
        path_layout.addWidget(QLabel("Shortcuts File:"))
        self.path_edit = QLineEdit()
        if self.shortcuts_path:
            self.path_edit.setText(self.shortcuts_path)
        self.path_edit.setReadOnly(True)
        path_layout.addWidget(self.path_edit, 1)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_shortcuts_file)
        path_layout.addWidget(browse_button)
        
        main_layout.addWidget(path_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter, 1)
        
        # Create sort options
        self.sort_type = QButtonGroup(exclusive=True)
        sort_id = QRadioButton("File order")
        sort_id.setChecked(True)
        sort_name = QRadioButton("Shortcut Name")
        self.sort_type.addButton(sort_id, 1) # id numbers are used to map against the shortcut list model
        self.sort_type.addButton(sort_name, 0)
        self.sort_type.idToggled.connect(self.sort_shortcuts)
        self.sort_order = 1

        # Create left panel for shortcut list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_header_panel = QWidget()
        left_header_layout = QHBoxLayout(left_header_panel)
        left_header_layout.addWidget(QLabel("Shortcuts:"))
        left_header_layout.addStretch()
        left_header_layout.addWidget(QLabel("Sort by:"))
        left_header_layout.addWidget(sort_id)
        left_header_layout.addWidget(sort_name)

        left_layout.addWidget(left_header_panel)
        
        # Create shortcut list
        self.shortcut_list = QStandardItemModel()
        self.shortcut_list_widget = QListView()
        self.shortcut_list_widget.setModel(self.shortcut_list)
        self.shortcut_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.shortcut_list_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.shortcut_list_widget.selectionModel().selectionChanged.connect(self.on_shortcut_select)

        left_layout.addWidget(self.shortcut_list_widget)
        
        # Add shortcuts to list if data is loaded
        if hasattr(self, 'data'):
            self.refresh_shortcut_list()
        
        # Create right panel for properties
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Create scroll area for properties
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.properties_widget = QWidget()
        self.properties_layout = QGridLayout(self.properties_widget)
        scroll_area.setWidget(self.properties_widget)
        right_layout.addWidget(QLabel("Properties:"))
        right_layout.addWidget(scroll_area)
        
        # Create buttons
        buttons_layout = QHBoxLayout()
        self.delete_button = QPushButton("Delete VDF Entry")
        self.delete_button.clicked.connect(self.delete_entry)
        self.delete_button.setDisabled(True)
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_changes)
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_data)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addWidget(self.save_button)
        right_layout.addLayout(buttons_layout)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([200, 700])  # Initial sizes
    
    def browse_shortcuts_file(self):
        """Let the user browse for the shortcuts.vdf file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select shortcuts.vdf file",
            str(Path.home()),
            "VDF Files (*.vdf);;All Files (*)"
        )
        
        if file_path:
            self.shortcuts_path = file_path
            self.path_edit.setText(file_path)
            self.load_data()
            self.refresh_shortcut_list()

    def sort_shortcuts(self, column, checked):
        if checked:
            self.shortcut_list.sort(column)
            self.sort_order = column
    
    def refresh_shortcut_list(self):
        """Refresh the shortcut list in the UI"""
        self.shortcut_list.clear()
        self.shortcut_list.setHorizontalHeaderLabels(["Name", "File Order"])
        if hasattr(self, 'data') and 'shortcuts' in self.data:
            for shortcut_id in self.data['shortcuts']:
                shortcut = self.data['shortcuts'][shortcut_id]
                app_name = dict((k.lower(), v) for k, v in shortcut.items()).get('appname', f"Shortcut {shortcut_id}")
                self.shortcut_list.appendRow([QStandardItem(app_name), QStandardItem(shortcut_id)])
    
    def on_shortcut_select(self, row):
        """Handle selection of a shortcut from the list"""
        # Clear current properties
        while self.properties_layout.count():
            item = self.properties_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.delete_button.setDisabled(True)
        
        if (row.indexes()): 
            shortcut_index = row.indexes()[0] # we ensure only a single selection is possible at construction time, so this should be sufficient
            shortcut_item = self.shortcut_list.itemFromIndex(shortcut_index)
        else:
            self.current_shortcut_id = None
            return
        if shortcut_item.row() < 0 or not hasattr(self, 'data') or 'shortcuts' not in self.data:
            return
        
        # Get shortcut data
        #shortcut_ids = list(self.shortcut_list.column)
        #if shortcut_index >= len(shortcut_ids):
        #    return
            
        shortcut_id = self.shortcut_list.item(shortcut_item.row(), 1).text()
        shortcut = self.data['shortcuts'][shortcut_id]
        
        # Save reference to current shortcut
        self.current_shortcut_name = self.shortcut_list.item(shortcut_item.row(), 0).text()
        self.current_shortcut_id = shortcut_id
        self.entry_widgets = {}
        
        # Add entry for each property
        row = 0
        for key, value in shortcut.items():
            # Add label
            self.properties_layout.addWidget(QLabel(f"{key}:"), row, 0)
            
            # Different handling based on value type
            if isinstance(value, dict):
                text_value = json.dumps(value, indent=2)
                entry = QTextEdit()
                entry.setPlainText(text_value)
                entry.setMinimumHeight(100)
            else:
                # Convert to string for display
                if isinstance(value, bytes):
                    text_value = value.decode('utf-8', errors='replace')
                elif isinstance(value, int):
                    #coerce value stored as unsigned in vdf but parsed as signed back into uint
                    #This is useful because SteamRomManager saves its icon files with this uint value, and writes them into the icon field
                    text_value = str(ctypes.c_uint32(value).value)
                else:
                    text_value = str(value)
                    
                entry = QLineEdit()
                entry.setText(text_value)
            
            self.properties_layout.addWidget(entry, row, 1)
            self.entry_widgets[key] = entry
            row += 1

        self.delete_button.setDisabled(False)

    def delete_entry(self):
        try:
            entry = self.current_shortcut_name
            if (QMessageBox.question(self, "Warning", f"Are you sure you want to delete the entry {entry}?", defaultButton=QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes):
                self.data['shortcuts'].pop(self.current_shortcut_id)
                current_row = self.shortcut_list.findItems(self.current_shortcut_id, column=1)[0].row()
                self.shortcut_list.removeRow(current_row)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed: {e}")
    
    def save_changes(self):
        """Save changes to the shortcuts.vdf file"""
        if not self.shortcuts_path:
            QMessageBox.warning(self, "Warning", "No shortcuts file selected.")
            return
            
        # Save current editing if any
        if hasattr(self, 'current_shortcut_id') and self.current_shortcut_id is not None:
            for key, entry in self.entry_widgets.items():
                if isinstance(entry, QTextEdit):
                    try:
                        # Try to parse as json for dict values
                        value = json.loads(entry.toPlainText())
                    except:
                        value = entry.toPlainText().strip()
                else:
                    value = entry.text()
                    # Try to convert to original type if possible
                    original_value = self.original_data['shortcuts'][self.current_shortcut_id].get(key)
                    if isinstance(original_value, int):
                        try:
                            value = int(value)
                        except ValueError:
                            pass
                
                self.data['shortcuts'][self.current_shortcut_id][key] = value
        
        # Save to file
        try:
            with open(self.shortcuts_path, 'wb') as f:
                vdf.binary_dump(self.data, f)
            QMessageBox.information(self, "Success", "Shortcuts saved successfully!")
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save shortcuts: {e}")
    
    def refresh_data(self):
        """Reload data from file and refresh UI"""
        if self.shortcuts_path:
            self.load_data()
            self.refresh_shortcut_list()
        else:
            QMessageBox.warning(self, "Warning", "No shortcuts file selected.")

def main():
    app = QApplication(sys.argv)
    window = SteamShortcutsEditor()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 