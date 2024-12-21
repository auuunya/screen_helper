from typing import Union, Dict, Any, Optional, Tuple, Callable, List
import cv2
import numpy as np
import mss

class ScreenToolkit:
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

class GraphicToolkit:
    def __init__(self, entity: Union[str, np.ndarray], mode: Optional[int] = None) -> None:
        if not entity:
            raise RuntimeError(f"entity cannot be empty!")
        if isinstance(entity, str):
            try:
                entity = cv2.imread(entity, mode)
                if entity is None:
                    raise FileNotFoundError(f"Failed to load image from '{entity}'")
            except cv2.error as e:
                raise ValueError(f"Failed to load image from '{entity}': {e}")
        if isinstance(entity, np.ndarray):
            if entity.size == 0:
                raise ValueError("Empty numpy array cannot be used as entity!")
        self.entity = entity
        self.threshold_modes = {
            "binary": cv2.THRESH_BINARY,
            "binary_inv": cv2.THRESH_BINARY_INV,
            "trunc": cv2.THRESH_TRUNC,
            "tozero": cv2.THRESH_TOZERO,
            "tozero_inv": cv2.THRESH_TOZERO_INV,
            "otsu": cv2.THRESH_OTSU,
            "triangle": cv2.THRESH_TRIANGLE
        }
    def get_entity(self) -> np.ndarray:
        """
        Returns the image entity (np.ndarray).
        
        :return: The image data as a numpy array.
        """
        return self.entity
    def preprocess_entity(self, entity: np.ndarray, options: Dict[str, Any] = None, return_steps: bool = False) -> np.ndarray:
        """
        Preprocess the input entity dynamically based on the provided options (grayscale, blur, histogram equalization, binarization).
        
        :param options: Preprocessing options which control grayscale conversion, blurring, histogram equalization, and binarization.
        :return: Preprocessed entity (image).
        """
        default_options = {
            "gray": False,
            "noise_reduction": {"enable": False, "method": "median", "ksize": 3},
            "blur": {"enable": False, "kernel_size": (5, 5)},
            "binarization": {"enable": False, "threshold_value": 150, "threshold_max_value": 255, "mode": "binary"},
            "equalize": False,
            "invert": False,
            "canny_edge": {"enable": False, "lower_threshold": 100, "upper_threshold": 200},
            "morphology": {"enable": False, "operation": "dilate", "kernel_size": (3, 3), "iterations": 1},
            "sharpen": {"enable": False},
            "custom_functions": []
        }
        if options is None:
            options = default_options

        steps = {}  
        processed_image = self.entity.copy()

        if options.get("gray", False):
            processed_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)
            steps["gray"] = processed_image.copy()

        noise_config = options.get("noise_reduction", {})
        if noise_config.get("enable", False):
            method = noise_config.get("method", "median")
            ksize = noise_config.get("ksize", 3)
            if method == "median":
                processed_image = cv2.medianBlur(processed_image, ksize)
            elif method == "gaussian":
                processed_image = cv2.GaussianBlur(processed_image, (ksize, ksize), 0)
            steps["noise_reduction"] = processed_image.copy()

        blur_config = options.get("blur", {})
        if blur_config.get("enable", False):
            kernel_size = blur_config.get("kernel_size", (5, 5))
            processed_image = cv2.GaussianBlur(processed_image, kernel_size, 0)
            steps["blur"] = processed_image.copy()

        if options.get("equalize", False) and len(processed_image.shape) == 2:
            processed_image = cv2.equalizeHist(processed_image)
            steps["equalize"] = processed_image.copy()

        bin_config = options.get("binarization", {})
        if bin_config.get("enable", False):
            threshold_value = bin_config.get("threshold_value", 150)
            max_value = bin_config.get("threshold_max_value", 255)
            mode_str = bin_config.get("mode", "binary")
            mode = self.threshold_modes.get(mode_str, cv2.THRESH_BINARY)
            _, processed_image = cv2.threshold(processed_image, threshold_value, max_value, mode)
            steps["binarization"] = processed_image.copy()
        
        if options.get("invert", False):
            processed_image = cv2.bitwise_not(processed_image)
            steps["invert"] = processed_image.copy()

        canny_config = options.get("canny_edge", {})
        if canny_config.get("enable", False):
            lower = canny_config.get("lower_threshold", 100)
            upper = canny_config.get("upper_threshold", 200)
            processed_image = cv2.Canny(processed_image, lower, upper)
            steps["canny_edge"] = processed_image.copy()

        morph_config = options.get("morphology", {})
        if morph_config.get("enable", False):
            operation = morph_config["operation"]
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, morph_config["kernel_size"])
            iterations = morph_config["iterations"]
            if operation == "dilate":
                processed_image = cv2.dilate(processed_image, kernel, iterations=iterations)
            elif operation == "erode":
                processed_image = cv2.erode(processed_image, kernel, iterations=iterations)
            steps["morphology"] = processed_image.copy()

        if options.get("sharpen", {}).get("enable", False):
            sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
            processed_image = cv2.filter2D(processed_image, -1, sharpen_kernel)
            steps["sharpen"] = processed_image.copy()

        for i, func_dict in enumerate(options.get("custom_functions", [])):
            func, params = func_dict["function"], func_dict.get("params", {})
            if callable(func):
                processed_image = func(processed_image, **params)
                steps[f"custom_function_{i+1}"] = processed_image.copy()
                
        if return_steps:
            steps["final"] = processed_image
            return steps
        return processed_image

    def resize_entity(
        self,
        size: Optional[Tuple[int, int]] = None, 
        scale: Optional[float] = None, 
        interpolation: int = cv2.INTER_LINEAR
    ) -> np.ndarray:
        """
        A general method for resizing an image, supporting both fixed size and scaling by a factor.

        :param size: The target size for the image (width, height). If provided, scale_factor will be ignored.
        :param scale: The scaling factor, indicating how much to enlarge or shrink the image (e.g., 2 means double the size).
        :param interpolation: The interpolation method for resizing.
        :return: The resized image, numpy array.
        """
        if size is None and scale is None:
            raise ValueError("Either size or scale must be provided.")
        if size is not None and scale is not None:
            raise ValueError("Cannot specify both size and scale.")
        height, width = self.entity.shape[:2]
        if size is not None:
            new_width, new_height = size
        elif scale is not None:
            new_width = int(width * scale)
            new_height = int(height * scale)
        resized_image = cv2.resize(self.entity, (new_width, new_height), interpolation=interpolation)
        return resized_image