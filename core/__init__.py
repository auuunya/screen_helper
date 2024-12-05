# This module is part of a cross-platform automation framework designed for visual automation tasks. 
# It includes functionality for handling screen capture, image matching, OCR recognition, mouse and keyboard control, 
# and window management. The framework supports Windows, Linux, and X11 environments. 
# 
# Key components:
# - `WindowManager`: Manages application windows based on the system (Windows/Linux).
# - `ScreenHelper`: Provides methods for interacting with the screen, including screen capture and resolution handling.
# - `ImageMatcher`: Facilitates image-based matching for automation tasks.
# - `OCRRecognizer`: Recognizes text from images using optical character recognition.
# - `FileManager`: Manages file operations like reading and writing images or logs.
# - `MouseController`: Handles mouse movements and clicks for automation.
# - `KeyboardController`: Simulates keyboard inputs for automation tasks.
# 
# Dependencies:
# - X11 environment (if available) is configured using `xhost` for enabling access to the display server.
# - The module uses platform-specific configurations to select the appropriate window management implementation.
# 
# Please refer to the documentation for installation and usage instructions.
from .utils import is_x11_environment, configure_xhost
if is_x11_environment():
    configure_xhost(enable=True)

from .config import BaseConfig
import warnings
if BaseConfig.system_name == "Windows":
    from .windows_window_manage import WindowManager
elif BaseConfig.system_name != "Linux":
    warnings.warn("暂不支持的操作系统类型")
else:
    from .linux_window_manage import WindowManager

from .defs import ScreenHelperDefs
from .file_manager import FileManager
from .image_matcher import ImageMatcher
from .logger import LoggerController
from .ocr_base import OCRRecognizer
from .result import Result
from .text_recognizer import TextRecognizer
from .screen_helper import ScreenHelper
from .screen_capture import ScreenCapture
from .mouse_controller import MouseController
from .keyboard_controller import KeyboardController