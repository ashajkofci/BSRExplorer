"""
BSR Explorer - Main Application
A portable, fast, and optimized viewer for BSR binary files
"""
import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QFileDialog, 
    QSplitter, QCheckBox, QGroupBox
)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
import pyqtgraph as pg
import numpy as np
from bsr_reader import BSRReader


class BSRExplorer(QMainWindow):
    """Main window for BSR file exploration"""
    
    def __init__(self):
        super().__init__()
        self.reader = BSRReader()
        self.plots = []
        self.plot_items = []
        self.exploded_mode = False
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("BSR Explorer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Control panel
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        # Info label
        self.info_label = QLabel("Drag and drop a BSR file or click 'Open File'")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.info_label)
        
        # Plot area with splitter for resizable plots
        self.plot_splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(self.plot_splitter, 1)
        
        # Initial plot setup
        self.setup_plots()
        
    def create_control_panel(self) -> QWidget:
        """Create the control panel with buttons and options"""
        panel = QGroupBox("Controls")
        layout = QHBoxLayout()
        
        # Open file button
        self.open_btn = QPushButton("Open File")
        self.open_btn.clicked.connect(self.open_file)
        layout.addWidget(self.open_btn)
        
        # Explode/Combine view toggle
        self.explode_checkbox = QCheckBox("Explode into 4 Plots")
        self.explode_checkbox.stateChanged.connect(self.toggle_view_mode)
        layout.addWidget(self.explode_checkbox)
        
        # Channel visibility checkboxes
        self.channel_checkboxes = []
        for i in range(4):
            cb = QCheckBox(f"Ch{i+1}")
            cb.setChecked(True)
            cb.stateChanged.connect(lambda state, idx=i: self.toggle_channel(idx, state))
            self.channel_checkboxes.append(cb)
            layout.addWidget(cb)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
        
    def setup_plots(self):
        """Setup plot widgets"""
        # Clear existing plots
        for plot in self.plots:
            self.plot_splitter.removeWidget(plot)
            plot.deleteLater()
        self.plots.clear()
        self.plot_items.clear()
        
        # Configure pyqtgraph for performance
        pg.setConfigOptions(antialias=False, useOpenGL=True)
        
        if self.exploded_mode:
            # Create 4 separate plots
            colors = ['r', 'g', 'b', 'y']
            for i in range(4):
                plot_widget = pg.PlotWidget(title=f"Channel {i+1}")
                plot_widget.setLabel('left', 'Amplitude')
                plot_widget.setLabel('bottom', 'Time', units='s')
                plot_widget.showGrid(x=True, y=True, alpha=0.3)
                
                # Enable mouse interaction
                plot_widget.setMouseEnabled(x=True, y=True)
                
                plot_item = plot_widget.plot(pen=pg.mkPen(color=colors[i], width=1))
                self.plot_items.append(plot_item)
                self.plots.append(plot_widget)
                self.plot_splitter.addWidget(plot_widget)
        else:
            # Create single combined plot
            plot_widget = pg.PlotWidget(title="All Channels")
            plot_widget.setLabel('left', 'Amplitude')
            plot_widget.setLabel('bottom', 'Time', units='s')
            plot_widget.showGrid(x=True, y=True, alpha=0.3)
            plot_widget.addLegend()
            
            # Enable mouse interaction
            plot_widget.setMouseEnabled(x=True, y=True)
            
            colors = ['r', 'g', 'b', 'y']
            for i in range(4):
                plot_item = plot_widget.plot(
                    pen=pg.mkPen(color=colors[i], width=1),
                    name=f"Channel {i+1}"
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
                self.plots[channel_idx].setVisible(visible)
            else:
                # In combined mode, hide/show the plot item
                if visible:
                    self.update_channel_plot(channel_idx)
                else:
                    self.plot_items[channel_idx].setData([], [])
    
    def open_file(self):
        """Open file dialog to select BSR file"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open BSR File",
            "",
            "BSR Files (*.bsr);;All Files (*.*)"
        )
        
        if filename:
            self.load_file(filename)
    
    def load_file(self, filename: str):
        """Load and display BSR file"""
        self.info_label.setText(f"Loading {os.path.basename(filename)}...")
        QApplication.processEvents()
        
        if self.reader.load_file(filename):
            num_samples = self.reader.get_num_samples()
            duration = self.reader.get_duration()
            
            self.info_label.setText(
                f"File: {os.path.basename(filename)} | "
                f"Samples: {num_samples:,} | "
                f"Duration: {duration:.2f}s | "
                f"Sample Rate: {self.reader.sample_rate/1000:.0f} kHz"
            )
            
            self.update_plots()
        else:
            self.info_label.setText("Error loading file")
    
    def update_plots(self):
        """Update plot with current data"""
        if self.reader.data is None:
            return
        
        time_axis = self.reader.get_time_axis()
        
        # For large files, downsample for initial view
        num_samples = len(time_axis)
        max_display_samples = 100000  # Display max 100k points initially
        
        if num_samples > max_display_samples:
            # Downsample by taking every nth point
            step = num_samples // max_display_samples
            time_axis = time_axis[::step]
            downsample = True
        else:
            step = 1
            downsample = False
        
        # Update each channel
        for i in range(4):
            if self.channel_checkboxes[i].isChecked():
                self.update_channel_plot(i, time_axis, step, downsample)
    
    def update_channel_plot(self, channel_idx: int, time_axis=None, step=1, downsample=False):
        """Update a specific channel plot"""
        if self.reader.data is None or channel_idx >= len(self.plot_items):
            return
        
        if time_axis is None:
            time_axis = self.reader.get_time_axis()
            num_samples = len(time_axis)
            max_display_samples = 100000
            
            if num_samples > max_display_samples:
                step = num_samples // max_display_samples
                time_axis = time_axis[::step]
                downsample = True
            else:
                step = 1
                downsample = False
        
        channel_data = self.reader.get_channel(channel_idx)
        if downsample:
            channel_data = channel_data[::step]
        
        self.plot_items[channel_idx].setData(time_axis, channel_data)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event for drag and drop"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event for drag and drop"""
        urls = event.mimeData().urls()
        if urls:
            filename = urls[0].toLocalFile()
            self.load_file(filename)
    
    def resizeEvent(self, event):
        """Handle window resize to auto-adjust plots"""
        super().resizeEvent(event)
        # Plots automatically resize with splitter


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    explorer = BSRExplorer()
    explorer.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
