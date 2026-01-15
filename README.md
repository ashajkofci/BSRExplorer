# BSR Explorer

A portable, fast, and optimized viewer for BSR (Binary Signal Recording) files.

## Features

- **Fast Loading**: Efficiently handles large files (~500 MB) using memory-mapped files
- **Multi-Channel Visualization**: View all 4 channels simultaneously or exploded into separate plots
- **Modern UI**: 
  - Zoom and pan with mouse wheel and drag
  - Pinch-to-zoom support on touchscreens
  - Auto-resize plots with window
- **Drag and Drop**: Simply drag a BSR file into the window
- **Channel Control**: Toggle individual channels on/off
- **High Performance**: Downsampling for initial display, OpenGL acceleration
- **Extensible Architecture**: Modular design for adding filters and processing

## File Format

BSR files are binary files containing:
- **Format**: Nx4 int32 samples
- **Sample Rate**: 200 kHz
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
- Windows: `BSRExplorer-Windows.zip`
- Linux: `BSRExplorer-Linux.tar.gz`
- macOS: `BSRExplorer-macOS.zip`

## Usage

### Opening Files

1. **Drag and Drop**: Drag a `.bsr` file into the application window
2. **File Menu**: Click "Open File" button and select a BSR file

### Navigation

- **Zoom**: Mouse wheel or pinch gesture
- **Pan**: Click and drag on the plot
- **Reset View**: Double-click on the plot

### View Modes

- **Combined View**: All 4 channels in one plot with different colors
- **Exploded View**: Check "Explode into 4 Plots" to see each channel in a separate, resizable plot

### Channel Control

- Use the Ch1-Ch4 checkboxes to show/hide individual channels

## Architecture

The application is designed with modularity in mind:

```
bsr_explorer.py      # Main GUI application (PyQt6)
bsr_reader.py        # Data loading and file I/O
```

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
- **Downsampling**: Initial display shows downsampled data (max 100k points)
- **OpenGL**: Hardware-accelerated rendering via pyqtgraph
- **Lazy Loading**: Only active channels are processed

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

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.