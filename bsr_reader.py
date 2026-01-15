"""
BSR File Reader Module
Handles reading and loading BSR binary files efficiently
"""
import numpy as np
from typing import Optional, Tuple


class BSRReader:
    """
    Reader for BSR binary files containing Nx4 int32 samples.
    Optimized for large files using memory-mapped files.
    """
    
    def __init__(self):
        self.data: Optional[np.ndarray] = None
        self.filename: Optional[str] = None
        self.sample_rate: int = 200000  # 200 kHz
        self.num_channels: int = 4
        
    def load_file(self, filename: str) -> bool:
        """
        Load a BSR file using memory-mapped array for efficiency.
        
        Args:
            filename: Path to the BSR file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use memory-mapped file for large files
            data = np.memmap(filename, dtype=np.int32, mode='r')
            
            # Reshape to Nx4 format
            if len(data) % self.num_channels != 0:
                print(f"Warning: File size not divisible by {self.num_channels}")
                # Truncate to nearest multiple
                data = data[:-(len(data) % self.num_channels)]
            
            self.data = data.reshape(-1, self.num_channels)
            self.filename = filename
            return True
            
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
    def get_channel(self, channel_idx: int) -> Optional[np.ndarray]:
        """
        Get data for a specific channel.
        
        Args:
            channel_idx: Channel index (0-3)
            
        Returns:
            Channel data array or None if invalid
        """
        if self.data is None or channel_idx < 0 or channel_idx >= self.num_channels:
            return None
        return self.data[:, channel_idx]
    
    def get_all_channels(self) -> Optional[np.ndarray]:
        """
        Get all channel data.
        
        Returns:
            Nx4 array or None if no data loaded
        """
        return self.data
    
    def get_time_axis(self) -> Optional[np.ndarray]:
        """
        Get time axis in seconds.
        
        Returns:
            Time array or None if no data loaded
        """
        if self.data is None:
            return None
        return np.arange(len(self.data)) / self.sample_rate
    
    def get_num_samples(self) -> int:
        """Get total number of samples."""
        return len(self.data) if self.data is not None else 0
    
    def get_duration(self) -> float:
        """Get duration in seconds."""
        return self.get_num_samples() / self.sample_rate if self.data is not None else 0.0
    
    def close(self):
        """Close and release file resources."""
        if self.data is not None:
            del self.data
            self.data = None
            self.filename = None
