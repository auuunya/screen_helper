from typing import Tuple, Optional
import os
import glob

import numpy as np
import mss
import cv2

class ScreenCapture:
    """
    Screen capture class that uses mss.mss to capture screenshots.

    This class provides methods for capturing the full screen or a specific region and saving screenshots to directories.

    Methods:
        - create_directory: Creates a directory to save screenshots.
        - capture: Captures a screenshot of the current screen or a specified region.
    """

    def __init__(self):
        """
        Initializes the ScreenCapture class and creates an mss.mss instance for screen capturing.
        """
        self.sct = mss.mss()

    def create_directory(self, dirs: str):
        """
        Create a directory for saving screenshots.

        :param dirs: Directory path where screenshots will be saved.
        :raises ValueError: If there is an error creating the directory.
        """
        try:
            if os.path.exists(dirs):
                for file in glob.glob(os.path.join(dirs, "*")):
                    try:
                        os.remove(file)
                    except OSError as e:
                        print(f"Error deleting file {file}: {e}")
            else:
                os.makedirs(dirs)
        except OSError as e:
            raise ValueError(f"Error creating screenshot directory: {str(e)}")
        
    def capture(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """
        Capture a screenshot of the current screen or a specified region.

        :param region: Optional, the region to capture in the format (left, top, right, bottom).
                       If not provided, the entire screen is captured.
        :return: A screenshot of the screen or region, returned as a numpy array.
        """
        if region:
            monitor = {
                "top": region[1],
                "left": region[0],
                "width": region[2] - region[0],
                "height": region[3] - region[1],
            }
        else:
            monitor = self.sct.monitors[1]
        screenshot = self.sct.grab(monitor)
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)
