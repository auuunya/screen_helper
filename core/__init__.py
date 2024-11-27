from .utils import is_x11_environment, configure_xhost
if is_x11_environment():
    configure_xhost(enable=True)

from .config import BaseConfig
if BaseConfig.system_name == "Windows":
    from .window_manage import WindowsManagerCtypes

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