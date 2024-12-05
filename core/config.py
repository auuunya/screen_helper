# This class provides configuration settings for the automation framework based on the underlying system platform.
# It allows setting system-specific parameters such as character encoding, scaling factor, and threshold for image matching.
# The configuration is designed to handle Windows and non-Windows (Linux/macOS) environments.
# 
# Key configurations:
# - `system_name`: The operating system's name (e.g., Windows, Linux).
# - `character`: Line-ending character sequence based on the OS.
# - `spacing`: Character encoding used (GBK for Windows, UTF-8 for other systems).
# - `scale_factor`: Scaling factor for image processing (1 for Windows, 2 for other systems).
# - `debug`: A flag to enable or disable debug mode.
# - `threshold`: A threshold value for image matching.
# 
# Methods:
# - `state_debug(enable: bool)`: Enable or disable debug mode.
# - `set_scale_factor(factor)`: Set the scaling factor for image processing.
# - `set_threshold(threshold)`: Set the threshold for image matching.

import platform

class BaseConfig:
    system_name = platform.system()
    character = "\r\n" if system_name == "Windows" else "\n"
    spacing = "GBK" if system_name == "Windows" else "utf-8"
    scale_factor = 1 if system_name == "Windows" else 2
    debug = False
    threshold = 0.8

    @classmethod
    def state_debug(cls, enable: bool = False):
        """
        Enable debug mode by setting the debug flag to True.
        
        :param enable: Whether to enable or disable debug mode.
        """
        cls.debug = enable

    @classmethod
    def set_scale_factor(cls, factor):
        """
        Set the scaling factor for image processing.
        
        :param factor: The scaling factor value (e.g., 1 for Windows, 2 for others).
        """
        cls.scale_factor = factor

    @classmethod
    def set_threshold(cls, threshold):
        """
        Set the image matching threshold.
        
        :param threshold: The threshold value (between 0 and 1) for image matching accuracy.
        """
        cls.threshold = threshold
