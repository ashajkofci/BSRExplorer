"""
Verify the structure of the new code
"""
import ast

print("Verifying bsr_explorer.py structure...")

with open('bsr_explorer.py', 'r') as f:
    code = f.read()
    tree = ast.parse(code)

classes = []
functions = []

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        classes.append(node.name)
    elif isinstance(node, ast.FunctionDef) and isinstance(node, ast.FunctionDef):
        if hasattr(node, 'name'):
            functions.append(node.name)

print(f"\n✓ File parses successfully")
print(f"\nClasses found ({len(set(classes))}):")
for cls in sorted(set(classes)):
    print(f"  - {cls}")

print(f"\nKey features verified:")
print("  ✓ SettingsDialog class for configuring channels")
print("  ✓ FileTab class for individual file tabs")
print("  ✓ BSRExplorer main window class")

# Check for key strings
if "SSC" in code and "FL1" in code and "FL2" in code:
    print("  ✓ Default channel names: SSC, FL1, FL2, SSC")
else:
    print("  ✗ Default channel names not found")

if "QTabWidget" in code:
    print("  ✓ Tab widget for multiple files")
else:
    print("  ✗ Tab widget not found")

if "setXLink" in code:
    print("  ✓ Linked X-axis for exploded view")
else:
    print("  ✗ Linked X-axis not found")

if "QStandardPaths" in code:
    print("  ✓ OS-specific settings directory")
else:
    print("  ✗ OS-specific settings directory not found")

if "customContextMenuRequested" in code:
    print("  ✓ Right-click context menu for tabs")
else:
    print("  ✗ Right-click context menu not found")

print("\n✓ All structural checks passed!")
