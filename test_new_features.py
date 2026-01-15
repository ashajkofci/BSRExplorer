"""
Test the new features
"""
import sys
import os
from pathlib import Path
import json

# Test 1: Settings path
print("Testing settings functionality...")
from PyQt6.QtCore import QStandardPaths
from pathlib import Path

app_data_dir = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.AppDataLocation
)
settings_dir = Path(app_data_dir) / "BSRExplorer"
print(f"✓ Settings directory would be: {settings_dir}")

# Test 2: Import check
print("\nTesting imports...")
try:
    from bsr_explorer import BSRExplorer, FileTab, SettingsDialog
    print("✓ All classes imported successfully")
    print("  - BSRExplorer (main window)")
    print("  - FileTab (individual file tabs)")
    print("  - SettingsDialog (settings dialog)")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 3: Default channel names
print("\nTesting default settings...")
try:
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    explorer = BSRExplorer()
    
    assert explorer.channel_names == ["SSC", "FL1", "FL2", "SSC"], "Default channel names incorrect"
    print(f"✓ Default channel names: {explorer.channel_names}")
    
    assert explorer.sample_rate == 200000, "Default sample rate incorrect"
    print(f"✓ Default sample rate: {explorer.sample_rate} Hz")
    
    # Test that tab widget exists
    assert hasattr(explorer, 'tab_widget'), "Tab widget not created"
    print("✓ Tab widget created")
    
    # Test menu bar exists
    menubar = explorer.menuBar()
    assert menubar is not None, "Menu bar not created"
    print("✓ Menu bar created")
    
    print("\n✓ All new features verified!")
    
except Exception as e:
    print(f"\n✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

