# New Features Summary

## 1. Settings Menu

**Location**: Settings → Configure Channels & Sample Rate

### Features:
- **Rename Channels**: Customize channel names (defaults: SSC, FL1, FL2, SSC)
- **Adjust Sample Rate**: Change from default 200 kHz
- **Persistent Storage**: Settings automatically saved to OS-specific application data directory
  - Windows: `%APPDATA%\BSRExplorer\settings.json`
  - macOS: `~/Library/Application Support/BSRExplorer/settings.json`
  - Linux: `~/.local/share/BSRExplorer/settings.json`

### How It Works:
1. Click Settings → Configure Channels & Sample Rate
2. Enter custom names for each channel
3. Adjust sample rate if needed
4. Click OK to save
5. All open tabs are automatically updated with new settings

## 2. Tab Support for Multiple Files

### Features:
- **Multiple Files**: Open multiple BSR files simultaneously
- **Tab Interface**: Each file in its own tab
- **Easy Navigation**: Click tabs to switch between files
- **Tab Closing**: Multiple ways to close tabs

### Opening Files in Tabs:
- **Drag & Drop**: Drag one or more BSR files into window → opens new tabs
- **File Menu**: File → Open File (Ctrl+O) → opens in new tab
- **Welcome Screen**: Shows when no files are open

### Tab Management:
- **Close Button**: Click X on tab to close it
- **Right-Click Menu**:
  - Close Tab: Close the selected tab
  - Close Other Tabs: Close all except selected
  - Close All Tabs: Close all tabs (returns to welcome screen)

## 3. Fixed Exploded View

### Features:
- **4 Plots in Same Window**: All plots visible simultaneously
- **Linked Time Axis**: Zoom/pan on one plot affects all time axes
- **Independent Amplitude Axis**: Each plot can be zoomed vertically independently
- **Resizable**: Use splitter handles to adjust plot heights

### How It Works:
1. Check "Explode into 4 Plots"
2. See all 4 channels in separate plots stacked vertically
3. Mouse wheel zoom on any plot: all time axes zoom together
4. Drag vertically on any plot: only that plot's amplitude zooms
5. Drag splitter handles between plots to resize

### Technical Implementation:
- Uses pyqtgraph's `setXLink()` to synchronize time axes
- Y-axis (amplitude) remains independent for each plot
- QSplitter allows manual height adjustment

## Default Channel Names

The default channel names are:
1. **SSC** (Channel 1)
2. **FL1** (Channel 2)
3. **FL2** (Channel 3)
4. **SSC** (Channel 4)

These can be changed at any time through the Settings menu.

## Keyboard Shortcuts

- **Ctrl+O**: Open file
- **Ctrl+Q**: Quit application

## Implementation Details

### Settings Storage
```python
# Settings are stored as JSON:
{
  "channel_names": ["SSC", "FL1", "FL2", "SSC"],
  "sample_rate": 200000
}
```

### Class Structure
- **BSRExplorer**: Main window with tab management
- **FileTab**: Individual file view (one per tab)
- **SettingsDialog**: Configuration dialog
- **BSRReader**: File I/O (unchanged)

### Key Improvements
1. **Settings persistence**: No need to reconfigure on every launch
2. **Multi-file workflow**: Compare multiple files side-by-side via tabs
3. **Better exploded view**: Time-locked plots with independent amplitude scaling
4. **Professional UI**: Menu bar, context menus, keyboard shortcuts
