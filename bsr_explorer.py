"""
BSR Explorer - Main Application
A portable, fast, and optimized viewer for BSR binary files

Version: 1.1.0
Author: Adrian Shajkofci
License: MIT
"""
import sys
import os
import json
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QFileDialog, 
    QSplitter, QCheckBox, QGroupBox, QTabWidget, QMenu,
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QMenuBar,
    QMessageBox, QTextEdit, QProgressDialog
)
from PyQt6.QtCore import Qt, QMimeData, QStandardPaths, QTimer
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QAction
import pyqtgraph as pg
import numpy as np
from bsr_reader import BSRReader

__version__ = "1.1.0"
__author__ = "Adrian Shajkofci"
__license__ = "MIT"


def get_git_version():
    """Get the git commit hash if available"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


class AboutDialog(QDialog):
    """About dialog showing version, author, and license"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("About BSR Explorer")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("<h2>BSR Explorer</h2>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Version info
        git_version = get_git_version()
        version_text = f"Version {__version__}"
        if git_version:
            version_text += f" (git: {git_version})"
        
        version_label = QLabel(version_text)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # Author
        author_label = QLabel(f"<b>Author:</b> {__author__}")
        author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(author_label)
        
        layout.addSpacing(20)
        
        # License
        license_label = QLabel("<b>License:</b>")
        layout.addWidget(license_label)
        
        # License text
        license_text = QTextEdit()
        license_text.setReadOnly(True)
        license_text.setPlainText("""MIT License

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
SOFTWARE.""")
        layout.addWidget(license_text)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class SettingsDialog(QDialog):
    """Dialog for configuring channel names and sample rate"""
    
    def __init__(self, parent, channel_names, sample_rate, max_display_samples):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        
        layout = QFormLayout(self)
        
        # Channel name inputs
        self.channel_inputs = []
        for i, name in enumerate(channel_names):
            line_edit = QLineEdit(name)
            layout.addRow(f"Channel {i+1} Name:", line_edit)
            self.channel_inputs.append(line_edit)
        
        # Sample rate input
        self.sample_rate_input = QLineEdit(str(sample_rate))
        layout.addRow("Sample Rate (Hz):", self.sample_rate_input)
        
        # Max display samples input
        self.max_samples_input = QLineEdit(str(max_display_samples))
        layout.addRow("Max Visible Samples:", self.max_samples_input)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def get_values(self):
        """Get the configured values"""
        channel_names = [inp.text() for inp in self.channel_inputs]
        try:
            sample_rate = int(self.sample_rate_input.text())
        except ValueError:
            sample_rate = 200000  # Default
        try:
            max_samples = int(self.max_samples_input.text())
        except ValueError:
            max_samples = 100000  # Default
        return channel_names, sample_rate, max_samples


class FileTab(QWidget):
    """Widget for a single file tab"""
    
    def __init__(self, parent, filename, channel_names, sample_rate):
        super().__init__(parent)
        self.parent_explorer = parent
        self.filename = filename
        self.reader = BSRReader()
        self.reader.sample_rate = sample_rate
        self.plots = []
        self.plot_items = []
        self.exploded_mode = False
        self.channel_names = channel_names
        self.range_change_connected = False  # Track if signal is connected
        self.last_x_range = None  # Track last X range to detect zoom vs pan
        self.max_display_samples = 100000  # Configurable max samples
        
        self.init_ui()
        self.load_file(filename)
        
    def init_ui(self):
        """Initialize the tab UI"""
        layout = QVBoxLayout(self)
        
        # Control panel
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)
        
        # Info label
        self.info_label = QLabel("Loading...")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)
        
        # Plot area with splitter for resizable plots
        self.plot_splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(self.plot_splitter, 1)
        
        # Initial plot setup
        self.setup_plots()
    
    def create_control_panel(self) -> QWidget:
        """Create the control panel with buttons and options"""
        panel = QGroupBox("Controls")
        layout = QHBoxLayout()
        
        # Explode/Combine view toggle
        self.explode_checkbox = QCheckBox("Explode into 4 Plots")
        self.explode_checkbox.stateChanged.connect(self.toggle_view_mode)
        layout.addWidget(self.explode_checkbox)
        
        # Channel visibility checkboxes
        self.channel_checkboxes = []
        for i in range(4):
            cb = QCheckBox(self.channel_names[i])
            cb.setChecked(True)
            cb.stateChanged.connect(lambda state, idx=i: self.toggle_channel(idx, state))
            self.channel_checkboxes.append(cb)
            layout.addWidget(cb)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def update_channel_names(self, channel_names):
        """Update channel names in UI"""
        self.channel_names = channel_names
        for i, cb in enumerate(self.channel_checkboxes):
            cb.setText(channel_names[i])
        # Update plot titles if in exploded mode
        if self.exploded_mode:
            for i, plot in enumerate(self.plots):
                plot.setTitle(channel_names[i])
    
    def update_sample_rate(self, sample_rate):
        """Update sample rate and refresh plots"""
        self.reader.sample_rate = sample_rate
        if self.reader.data is not None:
            self.update_info_label()
            self.update_plots()
    
    def setup_plots(self):
        """Setup plot widgets"""
        # Clear existing plots - properly remove from QSplitter
        while self.plot_splitter.count() > 0:
            widget = self.plot_splitter.widget(0)
            widget.setParent(None)
            if widget:
                widget.deleteLater()
        self.plots.clear()
        self.plot_items.clear()
        # Reset signal connection flag since old plot widgets are deleted
        self.range_change_connected = False
        
        # Configure pyqtgraph for performance
        pg.setConfigOptions(antialias=False, useOpenGL=True)
        
        if self.exploded_mode:
            # Create 4 separate plots in the same window with linked X axis
            colors = ['r', 'g', 'b', 'y']
            first_plot = None
            num_channels = len(self.channel_names)
            
            for i in range(num_channels):
                plot_widget = pg.PlotWidget(title=self.channel_names[i])
                plot_widget.setLabel('left', 'Amplitude')
                plot_widget.setLabel('bottom', 'Time', units='s')
                plot_widget.showGrid(x=True, y=True, alpha=0.3)
                
                # Link X axis to first plot (time axis locked together)
                if first_plot is None:
                    first_plot = plot_widget
                    # Connect view range change to update data dynamically (only once)
                    if not self.range_change_connected:
                        plot_widget.sigRangeChanged.connect(lambda: self.on_view_range_changed())
                        self.range_change_connected = True
                else:
                    plot_widget.setXLink(first_plot)
                
                # Enable mouse interaction - Y axis independent, X axis linked
                plot_widget.setMouseEnabled(x=True, y=True)

                # Keep Y axis in auto-range so amplitude adapts on zoom
                plot_widget.getViewBox().enableAutoRange(axis=pg.ViewBox.YAxis, enable=True)
                
                plot_item = plot_widget.plot(pen=pg.mkPen(color=colors[i], width=1))
                self.plot_items.append(plot_item)
                self.plots.append(plot_widget)
                self.plot_splitter.addWidget(plot_widget)
                
                # Ensure plot is visible based on checkbox state
                is_checked = self.channel_checkboxes[i].isChecked()
                plot_widget.setVisible(is_checked)
        else:
            # Create single combined plot
            plot_widget = pg.PlotWidget(title="All Channels")
            plot_widget.setLabel('left', 'Amplitude')
            plot_widget.setLabel('bottom', 'Time', units='s')
            plot_widget.showGrid(x=True, y=True, alpha=0.3)
            plot_widget.addLegend()
            
            # Enable mouse interaction
            plot_widget.setMouseEnabled(x=True, y=True)

            # Keep Y axis in auto-range so amplitude adapts on zoom
            plot_widget.getViewBox().enableAutoRange(axis=pg.ViewBox.YAxis, enable=True)
            
            # Connect view range change to update data dynamically (only once)
            if not self.range_change_connected:
                plot_widget.sigRangeChanged.connect(lambda: self.on_view_range_changed())
                self.range_change_connected = True
            
            colors = ['r', 'g', 'b', 'y']
            for i in range(4):
                plot_item = plot_widget.plot(
                    pen=pg.mkPen(color=colors[i], width=1),
                    name=self.channel_names[i]
                )
                self.plot_items.append(plot_item)
            
            self.plots.append(plot_widget)
            self.plot_splitter.addWidget(plot_widget)
    
    def toggle_view_mode(self, state):
        """Toggle between combined and exploded view"""
        self.exploded_mode = (state == Qt.CheckState.Checked.value)
        self.setup_plots()
        
        # Reload data if available
        if self.reader.data is not None:
            self.update_plots()
    
    def toggle_channel(self, channel_idx: int, state):
        """Toggle visibility of a specific channel"""
        if channel_idx < len(self.plot_items):
            visible = (state == Qt.CheckState.Checked.value)
            
            if self.exploded_mode and channel_idx < len(self.plots):
                # In exploded mode, show/hide entire plot widget
                self.plots[channel_idx].setVisible(visible)
                # Update data if making visible
                if visible and self.reader.data is not None:
                    self.update_channel_plot(channel_idx)
            else:
                # In combined mode, hide/show the plot item
                if visible:
                    self.update_channel_plot(channel_idx)
                else:
                    self.plot_items[channel_idx].setData([], [])
    
    def load_file(self, filename: str):
        """Load and display BSR file"""
        # Create progress dialog with cancel button
        progress = QProgressDialog("Loading BSR file...", "Cancel", 0, 100, self)
        progress.setWindowTitle("Loading")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(10)
        QApplication.processEvents()
        
        if progress.wasCanceled():
            return
        
        self.info_label.setText(f"Loading {os.path.basename(filename)}...")
        QApplication.processEvents()
        
        # Load file
        progress.setValue(30)
        progress.setLabelText("Reading file data...")
        QApplication.processEvents()
        
        if progress.wasCanceled():
            return
        
        if self.reader.load_file(filename):
            if progress.wasCanceled():
                return
                
            progress.setValue(60)
            progress.setLabelText("Processing data...")
            QApplication.processEvents()
            
            self.update_info_label()
            
            if progress.wasCanceled():
                return
                
            progress.setValue(80)
            progress.setLabelText("Updating plots...")
            QApplication.processEvents()
            
            self.update_plots()
            
            progress.setValue(100)
            progress.close()
        else:
            progress.close()
            self.info_label.setText("Error loading file")
    
    def update_info_label(self):
        """Update the info label with file statistics"""
        num_samples = self.reader.get_num_samples()
        duration = self.reader.get_duration()
        
        self.info_label.setText(
            f"File: {os.path.basename(self.filename)} | "
            f"Samples: {num_samples:,} | "
            f"Duration: {duration:.2f}s | "
            f"Sample Rate: {self.reader.sample_rate/1000:.0f} kHz"
        )
    
    def update_plots(self):
        """Update plot with current data"""
        if self.reader.data is None:
            return
        
        time_axis = self.reader.get_time_axis()
        
        # For large files, downsample for initial view using histogram method
        num_samples = len(time_axis)
        
        # Update each channel
        for i in range(4):
            if i < len(self.channel_checkboxes) and self.channel_checkboxes[i].isChecked():
                channel_data = self.reader.get_channel(i)
                
                if num_samples > self.max_display_samples:
                    # Use histogram-based downsampling
                    time_down, data_down = self.histogram_downsample(
                        channel_data, time_axis, self.max_display_samples
                    )
                    self.plot_items[i].setData(time_down, data_down)
                else:
                    # Show full resolution
                    self.plot_items[i].setData(time_axis, channel_data)
    
    def update_channel_plot(self, channel_idx: int):
        """Update a specific channel plot"""
        if self.reader.data is None or channel_idx >= len(self.plot_items):
            return
        
        time_axis = self.reader.get_time_axis()
        channel_data = self.reader.get_channel(channel_idx)
        num_samples = len(time_axis)
        
        if num_samples > self.max_display_samples:
            # Use histogram-based downsampling
            time_down, data_down = self.histogram_downsample(
                channel_data, time_axis, self.max_display_samples
            )
            self.plot_items[channel_idx].setData(time_down, data_down)
        else:
            # Show full resolution
            self.plot_items[channel_idx].setData(time_axis, channel_data)
    
    def update_max_display_samples(self, max_samples):
        """Update max display samples setting"""
        self.max_display_samples = max_samples
        if self.reader.data is not None:
            self.update_plots()
    
    def histogram_downsample(self, data, time_axis, target_samples):
        """
        Fast fully-vectorized downsampling using histogram-based approach that preserves extrema.
        
        Args:
            data: Channel data to downsample
            time_axis: Corresponding time axis
            target_samples: Target number of samples
            
        Returns:
            Tuple of (downsampled_time, downsampled_data)
        """
        if len(data) <= target_samples or target_samples <= 0:
            return time_axis, data
        
        # Calculate bin size - use target_samples // 2 since we keep 2 points per bin
        num_bins = max(1, target_samples // 2)
        bin_size = len(data) // num_bins
        
        if bin_size <= 0:
            return time_axis, data
        
        # Truncate data to fit evenly into bins for vectorization
        n_samples = num_bins * bin_size
        data_truncated = data[:n_samples]
        time_truncated = time_axis[:n_samples]
        
        # Reshape into bins for vectorized operations
        data_bins = data_truncated.reshape(num_bins, bin_size)
        time_bins = time_truncated.reshape(num_bins, bin_size)
        
        # Find min and max indices in each bin (vectorized)
        min_indices = np.argmin(data_bins, axis=1)
        max_indices = np.argmax(data_bins, axis=1)
        
        # Extract min and max values and times using advanced indexing
        bin_range = np.arange(num_bins)
        min_data = data_bins[bin_range, min_indices]
        max_data = data_bins[bin_range, max_indices]
        min_time = time_bins[bin_range, min_indices]
        max_time = time_bins[bin_range, max_indices]
        
        # Fully vectorized interleaving of min and max in time order
        # Determine which comes first: min or max
        min_first = min_indices <= max_indices
        
        # Create output arrays (2 points per bin, but may be same point)
        # Pre-allocate for max size (2 * num_bins)
        first_time = np.where(min_first, min_time, max_time)
        first_data = np.where(min_first, min_data, max_data)
        second_time = np.where(min_first, max_time, min_time)
        second_data = np.where(min_first, max_data, min_data)
        
        # Interleave: [first0, second0, first1, second1, ...]
        result_time = np.empty(2 * num_bins, dtype=time_axis.dtype)
        result_data = np.empty(2 * num_bins, dtype=data.dtype)
        result_time[0::2] = first_time
        result_time[1::2] = second_time
        result_data[0::2] = first_data
        result_data[1::2] = second_data
        
        return result_time, result_data
    
    def on_view_range_changed(self):
        """Handle view range changes to dynamically resample data on zoom only"""
        if self.reader.data is None or len(self.plots) == 0:
            return
        
        # Get the view range from the first plot (they're all linked)
        plot = self.plots[0]
        view_range = plot.viewRange()
        x_range = view_range[0]  # [min_time, max_time]
        
        # Check if this is a zoom (range size changed) or just a pan (range shifted)
        current_range_size = x_range[1] - x_range[0]
        
        if self.last_x_range is not None:
            last_range_size = self.last_x_range[1] - self.last_x_range[0]
            # Only update if zoom changed (range size changed significantly)
            # Use 0.1% threshold for more sensitive detection
            if last_range_size > 0 and abs(current_range_size - last_range_size) / last_range_size < 0.001:
                # This is just a pan, not a zoom - don't resample
                self.last_x_range = x_range
                return
        
        # Update last range before resampling
        self.last_x_range = x_range
        
        # Calculate which data points are visible
        time_axis_full = self.reader.get_time_axis()
        num_samples = len(time_axis_full)
        
        # Expand range by 2x on each side for better context
        range_margin = current_range_size  # Add 1x range on each side (total 3x)
        expanded_start = x_range[0] - range_margin
        expanded_end = x_range[1] + range_margin
        
        # Find indices for expanded range
        start_idx = max(0, int(expanded_start * self.reader.sample_rate))
        end_idx = min(num_samples, int(expanded_end * self.reader.sample_rate))
        
        # Calculate how many points are in the visible range
        visible_samples = end_idx - start_idx
        
        if visible_samples <= 0:
            return
        
        # Update plots with appropriate data resolution
        for i in range(4):
            if i < len(self.channel_checkboxes) and self.channel_checkboxes[i].isChecked():
                channel_data = self.reader.get_channel(i)
                
                if visible_samples > self.max_display_samples:
                    # Use histogram-based downsampling to preserve extrema
                    time_slice = time_axis_full[start_idx:end_idx]
                    data_slice = channel_data[start_idx:end_idx]
                    time_down, data_down = self.histogram_downsample(
                        data_slice, time_slice, self.max_display_samples
                    )
                    self.plot_items[i].setData(time_down, data_down)
                else:
                    # Show full resolution
                    time_slice = time_axis_full[start_idx:end_idx]
                    data_slice = channel_data[start_idx:end_idx]
                    self.plot_items[i].setData(time_slice, data_slice)

        # Re-apply Y auto-range after data updates from zoom
        for plot in self.plots:
            plot.getViewBox().enableAutoRange(axis=pg.ViewBox.YAxis, enable=True)


class BSRExplorer(QMainWindow):
    """Main window for BSR file exploration"""
    
    def __init__(self):
        super().__init__()
        self.channel_names = ["SSC", "FL1", "FL2", "SSC"]  # Default names (fixed last one)
        self.sample_rate = 200000  # Default 200 kHz
        self.max_display_samples = 100000  # Default max visible samples
        self.load_settings()
        
        self.init_ui()
        
    def get_settings_path(self):
        """Get OS-specific settings file path"""
        app_data_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppDataLocation
        )
        settings_dir = Path(app_data_dir) / "BSRExplorer"
        settings_dir.mkdir(parents=True, exist_ok=True)
        return settings_dir / "settings.json"
    
    def load_settings(self):
        """Load settings from OS-specific directory"""
        try:
            settings_path = self.get_settings_path()
            if settings_path.exists():
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    self.channel_names = settings.get('channel_names', self.channel_names)
                    self.sample_rate = settings.get('sample_rate', self.sample_rate)
                    self.max_display_samples = settings.get('max_display_samples', self.max_display_samples)
        except Exception as e:
            print(f"Could not load settings: {e}")
    
    def save_settings(self):
        """Save settings to OS-specific directory"""
        try:
            settings_path = self.get_settings_path()
            settings = {
                'channel_names': self.channel_names,
                'sample_rate': self.sample_rate,
                'max_display_samples': self.max_display_samples
            }
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Could not save settings: {e}")
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("BSR Explorer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget for multiple files
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_widget.customContextMenuRequested.connect(self.show_tab_context_menu)
        main_layout.addWidget(self.tab_widget)
        
        # Add initial empty state
        if self.tab_widget.count() == 0:
            self.show_empty_state()
    
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open File", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = menubar.addMenu("&Settings")
        
        config_action = QAction("&Configure Channels && Sample Rate", self)
        config_action.triggered.connect(self.show_settings_dialog)
        settings_menu.addAction(config_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
    
    def show_about_dialog(self):
        """Show the about dialog"""
        dialog = AboutDialog(self)
        dialog.exec()
    
    def show_settings_dialog(self):
        """Show the settings dialog"""
        dialog = SettingsDialog(self, self.channel_names, self.sample_rate, self.max_display_samples)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.channel_names, self.sample_rate, self.max_display_samples = dialog.get_values()
            self.save_settings()
            
            # Update all open tabs
            for i in range(self.tab_widget.count()):
                widget = self.tab_widget.widget(i)
                if isinstance(widget, FileTab):
                    widget.update_channel_names(self.channel_names)
                    widget.update_sample_rate(self.sample_rate)
                    widget.update_max_display_samples(self.max_display_samples)
    
    def show_empty_state(self):
        """Show empty state message"""
        empty_widget = QWidget()
        layout = QVBoxLayout(empty_widget)
        
        label = QLabel("Drag and drop a BSR file or use File → Open File")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        open_btn = QPushButton("Open File")
        open_btn.clicked.connect(self.open_file)
        layout.addWidget(open_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.tab_widget.addTab(empty_widget, "Welcome")
    
    def open_file(self):
        """Open file dialog to select BSR file"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open BSR File",
            "",
            "BSR Files (*.bsr);;All Files (*.*)"
        )
        
        if filename:
            self.add_file_tab(filename)
    
    def add_file_tab(self, filename: str):
        """Add a new tab for a file"""
        # Remove welcome tab if present
        if self.tab_widget.count() == 1:
            widget = self.tab_widget.widget(0)
            if not isinstance(widget, FileTab):
                self.tab_widget.removeTab(0)
        
        # Create new tab with current settings
        tab = FileTab(self, filename, self.channel_names.copy(), self.sample_rate)
        tab.max_display_samples = self.max_display_samples  # Apply max_display_samples
        tab_name = os.path.basename(filename)
        self.tab_widget.addTab(tab, tab_name)
        self.tab_widget.setCurrentWidget(tab)
    
    def close_tab(self, index: int):
        """Close a tab"""
        widget = self.tab_widget.widget(index)
        if isinstance(widget, FileTab):
            if hasattr(widget.reader, 'close'):
                widget.reader.close()
        self.tab_widget.removeTab(index)
        
        # Show welcome screen if no tabs left
        if self.tab_widget.count() == 0:
            self.show_empty_state()
    
    def show_tab_context_menu(self, position):
        """Show context menu for tabs"""
        tab_bar = self.tab_widget.tabBar()
        index = tab_bar.tabAt(position)
        
        if index >= 0:
            menu = QMenu(self)
            close_action = QAction("Close Tab", self)
            close_action.triggered.connect(lambda: self.close_tab(index))
            menu.addAction(close_action)
            
            close_others_action = QAction("Close Other Tabs", self)
            close_others_action.triggered.connect(lambda: self.close_other_tabs(index))
            menu.addAction(close_others_action)
            
            close_all_action = QAction("Close All Tabs", self)
            close_all_action.triggered.connect(self.close_all_tabs)
            menu.addAction(close_all_action)
            
            menu.exec(tab_bar.mapToGlobal(position))
    
    def close_other_tabs(self, keep_index: int):
        """Close all tabs except the specified one"""
        # Close tabs in reverse order to maintain indices
        for i in range(self.tab_widget.count() - 1, -1, -1):
            if i != keep_index:
                self.close_tab(i)
    
    def close_all_tabs(self):
        """Close all tabs"""
        while self.tab_widget.count() > 0:
            self.close_tab(0)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event for drag and drop"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event for drag and drop - opens new tab"""
        urls = event.mimeData().urls()
        for url in urls:
            filename = url.toLocalFile()
            if filename and (filename.lower().endswith('.bsr') or True):  # Accept all files for now
                self.add_file_tab(filename)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    explorer = BSRExplorer()
    explorer.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
