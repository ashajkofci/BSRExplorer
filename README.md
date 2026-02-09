# BSR Explorer

A portable, fast, and optimized viewer for BSR (Binary Signal Recording) files.

**Author:** Adrian Shajkofci  
**License:** MIT

## Features

- **Fast Loading**: Efficiently handles large files (~500 MB) using memory-mapped files
- **Multi-Channel Visualization**: View all 4 channels simultaneously or exploded into separate plots
- **Multiple File Tabs**: Open and compare multiple BSR files in tabs
- **Configurable Channels**: Rename channels and adjust sample rate (Settings menu)
- **Smart Downsampling**: 
  - Histogram-based algorithm preserves signal extrema (peaks and troughs)
  - Only resamples on zoom (not pan) for smooth navigation
  - Automatically shows full resolution when zoomed in
- **Modern UI**: 
  - Zoom and pan with mouse wheel and drag
  - Pinch-to-zoom support on touchscreens
  - Auto-resize plots with window
  - Linked time axis in exploded view
- **Drag and Drop**: Drag BSR files into the window to open new tabs
- **Channel Control**: Toggle individual channels on/off
- **Tab Management**: Right-click on tabs to close individual or multiple tabs
- **Persistent Settings**: Channel names and sample rate stored in OS-specific directory
- **High Performance**: Dynamic downsampling based on zoom level, OpenGL acceleration
- **Extensible Architecture**: Modular design for adding filters and processing

## File Format

BSR files are binary files containing:
- **Format**: Nx4 int32 samples
- **Sample Rate**: 200 kHz (configurable)
- **Channels**: 4 channels per sample

## Installation

### Option 1: Run from Source

1. Install Python 3.11 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the application:
```bash
python bsr_explorer.py
```

### Option 2: Download Pre-built Executable

Download the latest release for your platform from the [Releases](../../releases) page:
- Windows: `BSRExplorer-Windows.zip` (portable) or `BSRExplorer-Windows-Installer.exe` (installer)
- Linux: `BSRExplorer-Linux.tar.gz`
- macOS: `BSRExplorer-macOS.zip` (portable) or `BSRExplorer-macOS-Installer.dmg` (installer)

## Usage

### Opening Files

1. **Drag and Drop**: Drag one or more `.bsr` files into the application window to open them in new tabs
2. **File Menu**: Use File → Open File (Ctrl+O) to select a BSR file

### Multiple Files

- **Tabs**: Each file opens in its own tab
- **Switch Files**: Click on tabs to switch between files
- **Close Tabs**: Click the X on a tab or right-click for more options:
  - Close Tab
  - Close Other Tabs
  - Close All Tabs

### Settings

Access Settings → Configure Channels & Sample Rate to:
- **Rename Channels**: Default names are SSC, FL1, FL2, SSC
- **Adjust Sample Rate**: Change from default 200 kHz
- Settings are automatically saved to your OS-specific application data directory:
  - Windows: `%APPDATA%\BSRExplorer\settings.json`
  - macOS: `~/Library/Application Support/BSRExplorer/settings.json`
  - Linux: `~/.local/share/BSRExplorer/settings.json`

### Navigation

- **Zoom**: Mouse wheel or pinch gesture
- **Pan**: Click and drag on the plot
- **Reset View**: Double-click on the plot
- **Dynamic Resolution**: When you zoom in, the application automatically fetches full-resolution data for the visible range

### View Modes

- **Combined View**: All 4 channels in one plot with different colors
- **Exploded View**: Check "Explode into 4 Plots" to see each channel in a separate plot
  - Time axis is synchronized across all plots (zoom/pan together)
  - Amplitude axis is independent for each plot
  - Plots are resizable using the splitter handles

### Channel Control

- Use the channel checkboxes (default: SSC, FL1, FL2, SSC) to show/hide individual channels
- Channel names can be customized in Settings

### About

Access Help → About to view:
- Application version
- Git commit hash (if running from source)
- Author information
- MIT License text

## Architecture

The application is designed with modularity in mind:

```
bsr_explorer.py      # Main GUI application (PyQt6)
bsr_reader.py        # Data loading and file I/O
LICENSE              # MIT License
```

### Key Components

- **BSRExplorer**: Main window managing tabs and menus
- **FileTab**: Individual file view (one per tab)
- **SettingsDialog**: Configuration dialog for channels and sample rate
- **AboutDialog**: Application information and license
- **BSRReader**: Memory-mapped file I/O

### Extending the Application

#### Adding New Filters

To add signal processing filters, you can extend the `BSRReader` class:

```python
def apply_filter(self, channel_idx: int, filter_type: str):
    """Apply a filter to a specific channel"""
    # Add your filter implementation here
    pass
```

#### Adding More Channels

The architecture supports extending beyond 4 channels. Modify the `num_channels` parameter in `BSRReader` and update the UI accordingly.

## Performance Optimization

- **Memory Mapping**: Large files are memory-mapped for efficient loading
- **Smart Downsampling**: Histogram-based algorithm that:
  - Preserves extrema (min/max) from each data bin
  - Only resamples on zoom operations (not pan)
  - Automatically switches to full resolution when zoomed in
  - Keeps important signal features (peaks and troughs)
- **OpenGL**: Hardware-accelerated rendering via pyqtgraph
- **Lazy Loading**: Only active channels are processed
- **View-based Updates**: Data resolution adapts to zoom level

## Development

### Building Executables

The project includes GitHub Actions workflows for automated builds. To build locally:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name BSRExplorer bsr_explorer.py
```

### Testing

To test with a sample BSR file, you can create one:

```python
import numpy as np

# Create sample data: 1 second at 200 kHz, 4 channels
samples = 200000
data = np.random.randint(-1000, 1000, size=(samples, 4), dtype=np.int32)
data.tofile('sample.bsr')
```

## Requirements

- Python 3.11+
- NumPy >= 1.24.0
- PyQt6 >= 6.6.0
- pyqtgraph >= 0.13.3

## License

MIT License

Copyright (c) 2026 Adrian Shajkofci

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

**Adrian Shajkofci**

For questions, issues, or feature requests, please use the GitHub issue tracker.