import cv2
import numpy as np
from typing import List, Tuple, Dict, Any, Union, Optional
import uuid
from .utils import load_image_file

class Template:
    def __init__(self, identifier: str, template_image: np.ndarray):
        """
        Initialize the Template object.
        
        :param identifier: Unique identifier for the template.
        :param template_image: Template image as a NumPy array.
        """
        self.identifier = identifier
        self.template_image = template_image

class ImageMatcher:

    def __init__(self, scale_factor: float = None, threshold: float = None):
        """
        Initialize the ImageMatcher object.
        
        :param scale_factor: Scale factor for resizing the image during matching.
        :param threshold: Matching threshold to control the sensitivity of the match.
        """
        self._scale_factor = scale_factor
        self._threshold = threshold
        self.templates = {}

    def update_config(self, scale_factor: float = None, threshold: float = None):
        """
        Update the configuration of the image matcher.
        
        :param scale_factor: New scale factor for resizing images during matching.
        :param threshold: New matching threshold.
        """
        if scale_factor is not None:
            self._scale_factor = scale_factor
        if threshold is not None:
            self._threshold = threshold

    def add_image_template(self, template_image: np.ndarray) -> str:
        """
        Add a template image to the matcher.
        
        :param template_image: Template image as a NumPy array.
        :return: Unique identifier for the template.
        """
        template_id = f"templates_{uuid.uuid4()}"
        self.templates[template_id] = Template(template_id, template_image)
        return template_id

    def retrieve_template(self, identifier: str) -> np.ndarray:
        """
        Retrieve a template image by its unique identifier.
        
        :param identifier: Unique identifier of the template.
        :return: Corresponding template image as a NumPy array, or None if not found.
        """
        template = self.templates.get(identifier)
        return template.template_image if template else None
    
    @staticmethod
    def preprocess_input_image(image: np.ndarray, options: Dict[str, Any] = None) -> np.ndarray:
        """
        Preprocess the input image dynamically based on provided options (grayscale, blur, histogram equalization, binarization).
        
        :param image: Input image as a NumPy array.
        :param options: Preprocessing options which control grayscale conversion, blurring, histogram equalization, and binarization.
        :return: Preprocessed image.
        """
        if options is None:
            options = {}

        processed_image = image.copy()
        
        # Convert to grayscale if specified
        if options.get('gray', False):
            processed_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur if specified
        if options.get('blur', False):
            blur_kernel_size = options.get('blur_kernel', (5, 5))
            processed_image = cv2.GaussianBlur(processed_image, blur_kernel_size, 0)

        # Apply histogram equalization if specified (only on grayscale images)
        if options.get('equalize', False) and len(processed_image.shape) == 2:
            processed_image = cv2.equalizeHist(processed_image)
        
        # Apply binary thresholding if specified
        if options.get("threshold", False):
            if len(processed_image.shape) == 3:
                processed_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)
            threshold_value = options.get("threshold_value", 150)
            max_value = options.get("max_value", 255)
            _, processed_image = cv2.threshold(processed_image, threshold_value, max_value, cv2.THRESH_BINARY)
        return processed_image

    def find_template_locations(self, screen: np.ndarray, template: np.ndarray, threshold: float = None) -> List[Tuple[int, int]]:
        """
        Find all locations of the template in the screen image.
        
        :param screen: Current screen image as a NumPy array.
        :param template: Template image as a NumPy array.
        :return: A list of positions (x, y) where the template was found.
        """
        if not threshold:
            threshold = self._threshold
        screen_resized = cv2.resize(screen, None, fx=self._scale_factor, fy=self._scale_factor, interpolation=cv2.INTER_LINEAR)
        result = cv2.matchTemplate(screen_resized, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val < threshold:
            raise RuntimeError(f"Match failed, current threshold {max_val} did not reach defined threshold {threshold}")

        template_matches = []
        y_coords, x_coords = np.where(result >= threshold)
        template_height, template_width = template.shape[:2]
        for x, y in zip(x_coords, y_coords):
            center_x = int((x + template.shape[1] // 2) / self._scale_factor)
            center_y = int((y + template.shape[0] // 2) / self._scale_factor)
            template_matches.append(
                {
                    "template": self.add_image_template(template),
                    "position": (center_x, center_y),
                    "dimensions": (template_width, template_height),
                    "threshold": threshold
                }
            )
        return template_matches

    def find_template_with_contexts(self, screen: np.ndarray, template: np.ndarray, contexts: List[dict], 
                             all_matching: bool = False) -> Union[dict, None]:
        """
        Find all matching positions of the template in the screen image based on context conditions.

        :param screen: Current screen image as a NumPy array.
        :param template: Template image as a NumPy array.
        :param contexts: List of dictionaries containing context templates and related information.
        :param all_matching: If True, all contexts must match for a successful result.
        :return: A dictionary containing match information if a match is found, or None if no match is found.
        """
        template_matches = self.find_template_locations(screen, template)
        if not template_matches:
            return None
        if not contexts:
            return None
        for match in template_matches:
            context_results = self.filter_context_matches(screen, match, contexts)
            if all_matching:
                if context_results and len(context_results) == len(contexts):
                    match["context_matches"] = context_results
                    return match
            else:
                if context_results:
                    match["context_matches"] = context_results
                    return match
        return None

    def filter_context_matches(self, screen: np.ndarray, match: dict, contexts: List[dict]) -> Union[dict, None]:
        """
        Filter the context matches based on the provided contexts and return the detailed match information.

        :param screen: Current screen image as a NumPy array.
        :param match: Dictionary containing the matched template position (x, y).
        :param contexts: List of dictionaries containing context templates and related information.
        :return: A list of context match information, or None if no matches are found.
        """
        context_matches = []
        successful_matches = set()
        for idx, context in enumerate(contexts):
            template_path = context.get("template")
            offset = context.get("offset", {"x": 0, "y": 0})
            threshold = context.get("threshold", self.threshold)
            context_template_ndarray = load_image_file(template_path)
            context_positions = self.find_template_locations(screen, context_template_ndarray, threshold)
            if context_positions:
                for context_position in context_positions:
                    if (idx not in successful_matches and 
                        abs(context_position["position"][0] - match["position"][0]) <= offset.get("x", 0) and
                        abs(context_position["position"][1] - match["position"][1]) <= offset.get("y", 0)):
                        context_matches.append(context_position)
                        successful_matches.add(idx)
                        break 
        return context_matches
        # 重复值较多
        # for idx, context in enumerate(contexts):
        #     template_path = context.get("template")
        #     offset = context.get("offset", {"x": 0, "y": 0})
        #     threshold = context.get("threshold", self.threshold)

        #     context_template_ndarray = load_image_file(template_path)
        #     context_positions = self.find_template_locations(screen, context_template_ndarray, threshold)
        #     context_template_height, context_template_width = context_template_ndarray.shape[:2]
        #     if context_positions:
        #         matched_positions = [
        #             context_position for context_position in context_positions
        #             if (idx not in successful_matches and 
        #                 abs(context_position["position"][0] - match["position"][0]) <= offset.get("x", 0) and
        #                 abs(context_position["position"][1] - match["position"][1]) <= offset.get("y", 0))
        #             ]
                
        #         for context_position in matched_positions:
        #             context_matches.append(context_position)
        #             successful_matches.add(idx)
        # return context_matches
    @staticmethod
    def calculate_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """
        Calculate the Euclidean distance between two positions.
        
        :param pos1: First position as a tuple (x, y).
        :param pos2: Second position as a tuple (x, y).
        :return: Euclidean distance between the two positions.
        """
        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5

    @staticmethod
    def compare_images(
        cls,
        screenshot_before: np.ndarray, 
        screenshot_after: np.ndarray, 
        options: Dict[str, Any] = None, 
        threshold: float = 0.9
    ) -> bool:
        """
        Compare two images for similarity using a threshold.

        :param screenshot_before: The first screenshot.
        :param screenshot_after: The second screenshot.
        :param options: Options for preprocessing images, such as gray scaling, thresholding, etc.
        :param threshold: Similarity threshold, default is 0.9.
        :return: Returns True if the images are different, False if they are similar.
        """
        if options is None:
            options = {}
        # 如果有选项，则进行图像处理
        if options:
            screenshot_before = cls.preprocess_image(screenshot_before, options)
            screenshot_after = cls.preprocess_image(screenshot_after, options)
        # 计算相似度
        similarity = cv2.matchTemplate(screenshot_before, screenshot_after, cv2.TM_CCOEFF_NORMED)
        max_val = np.max(similarity)
        return max_val < threshold

    @staticmethod
    def filter_nearby_matches(matches: List[dict], min_distance: float = 10) -> List[dict]:
        """
        Filter out adjacent duplicate match points, keeping only one from each group of adjacent points.
        
        :param matches: The initial list of match points, each containing a 'position' field.
        :param min_distance: The minimum distance between two match points. Points closer than this distance will be considered duplicates.
        :return: The filtered list of match points.
        """
        filtered_matches = []
        for match in matches:
            too_close = False
            for fmatch in filtered_matches:
                distance = np.linalg.norm(np.array(fmatch['position']) - np.array(match['position']))
                if distance < min_distance:
                    too_close = True
                    break
            if not too_close:
                filtered_matches.append(match)
        return filtered_matches
    
    def find_template_locations_complex(
            self,
            screen: np.ndarray,
            template: np.ndarray,
            color_space: str = 'HSV',  # 'HSV' or 'BGR'
            lower_color: Optional[np.ndarray] = None,  # Lower bound of color range
            upper_color: Optional[np.ndarray] = None,  # Upper bound of color range
            threshold: float = 0.8,  # Matching threshold
            min_area: Optional[float] = None,  # Minimum contour area
            max_area: Optional[float] = None,  # Maximum contour area
            min_aspect_ratio: Optional[float] = None,  # Minimum aspect ratio
            max_aspect_ratio: Optional[float] = None,  # Maximum aspect ratio
            scale_factor: Optional[float] = None  # Screen scaling factor
        ) -> Union[List[Dict], None]:
        """
        Find template image locations in the screen image, returning all matched positions.
        Supports color range filtering, contour filtering, and other parameters.
        
        :param screen: The current screen image (in NumPy array format).
        :param template: The template image as a NumPy array.
        :param color_space: Color space to use, either 'HSV' or 'BGR'.
        :param lower_color: Lower bound of the color range (NumPy array) for color filtering.
        :param upper_color: Upper bound of the color range (NumPy array) for color filtering.
        :param threshold: Template matching threshold, default is 0.8.
        :param min_area: Minimum contour area to filter small contours.
        :param max_area: Maximum contour area to filter large contours. Default is None (no limit).
        :param min_aspect_ratio: Minimum aspect ratio for the matched region.
        :param max_aspect_ratio: Maximum aspect ratio for the matched region.
        :param scale_factor: Screen scaling factor, used to resize the image for different resolutions. Default is 1.0.
        :return: A list of matched template information, or None if no matches are found.
        """
        # 1. Apply color filter if color bounds are provided
        color_mask = None
        if lower_color is not None and upper_color is not None:
            if color_space == 'HSV':
                hsv_screen = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
            elif color_space == 'BGR':
                hsv_screen = screen  # No conversion for BGR
            else:
                raise ValueError("Unsupported color space. Choose either 'HSV' or 'BGR'.")
            # Create color mask
            color_mask = cv2.inRange(hsv_screen, lower_color, upper_color)
        
        # 2. Resize and convert to grayscale
        scale_factor = scale_factor or self.scale_factor
        screen_resized = cv2.resize(screen, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)
        screen_gray = cv2.cvtColor(screen_resized, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        # Use edge detection to find all possible match regions
        edges_screen = cv2.Canny(screen_gray, 100, 200)
        edges_template = cv2.Canny(template_gray, 100, 200)
        
        # 3. Perform template matching
        result = cv2.matchTemplate(edges_screen, edges_template, cv2.TM_CCOEFF_NORMED)
        y_coords, x_coords = np.where(result >= threshold)
        template_matches = []
        template_height, template_width = template.shape[:2]
        
        for x, y in zip(x_coords, y_coords):
            center_x = int((x + template_width // 2) / scale_factor)
            center_y = int((y + template_height // 2) / scale_factor)
            
            # If color mask is provided, ensure the center point is within the color range
            if color_mask is not None:
                if color_mask[y + template_height // 2, x + template_width // 2] == 0:
                    continue  # Skip if center is outside the specified color range
            
            # Extract region of interest (ROI)
            roi = screen[center_y - template_height // 2:center_y + template_height // 2, 
                        center_x - template_width // 2:center_x + template_width // 2]
            
            # Filter by area and aspect ratio if provided
            area = template_width * template_height
            aspect_ratio = float(template_width) / template_height
            if (min_area and area < min_area) or (max_area and area > max_area):
                continue
            if (min_aspect_ratio and aspect_ratio < min_aspect_ratio) or (max_aspect_ratio and aspect_ratio > max_aspect_ratio):
                continue
            
            template_matches.append({
                "position": (center_x, center_y),
                "dimensions": (template_width, template_height),
                "score": result[y, x],
                "roi": roi,
                "threshold": threshold
            })
        return template_matches
   
    def find_template_with_features(
            self,
            screen: np.ndarray, 
            template: np.ndarray, 
            feature_type: str = 'ORB',  # 'ORB', 'SIFT', or 'SURF'
            threshold: float = 0.8,  # Minimum score threshold for matching
            max_matches: Optional[int] = 50  # Optional, maximum number of matches, default is 50
        ) -> Union[List[Dict], None]:
        """
        Use feature matching (ORB, SIFT, SURF) to find template image locations in the screen.
        
        :param screen: The current screen image (in NumPy array format).
        :param template: The template image as a NumPy array.
        :param feature_type: Feature matching method, 'ORB', 'SIFT', or 'SURF'.
        :param threshold: Minimum matching score threshold.
        :param max_matches: Optional, the maximum number of matches to return, default is 50.
        :return: A list of matched results, including the center coordinates of each match.
        """
        # Choose feature detector
        if feature_type == 'ORB':
            feature_detector = cv2.ORB_create()
        elif feature_type == 'SIFT':
            feature_detector = cv2.SIFT_create()
        elif feature_type == 'SURF':
            feature_detector = cv2.xfeatures2d.SURF_create()  # Requires opencv-contrib
        else:
            raise ValueError("Unsupported feature type. Choose from 'ORB', 'SIFT', or 'SURF'.")
        
        # 1. Detect and compute keypoints and descriptors
        kp_screen, des_screen = feature_detector.detectAndCompute(screen, None)
        kp_template, des_template = feature_detector.detectAndCompute(template, None)
        if des_screen is None or des_template is None:
            raise ValueError("Feature detection failed or descriptors could not be computed.")
        
        # 2. Match descriptors using BruteForce matcher
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des_screen, des_template)
        
        # 3. Sort matches by distance
        matches = sorted(matches, key=lambda x: x.distance)
        
        # 4. Select good matches based on threshold
        good_matches = [match for match in matches if match.distance < threshold * max([m.distance for m in matches])]
        
        # 5. Get center coordinates of all matched regions
        template_matches = []
        for match in good_matches[:max_matches]:
            screen_point = kp_screen[match.queryIdx].pt
            center_x = int(screen_point[0])
            center_y = int(screen_point[1])
            template_height, template_width = template.shape[:2]
            template_matches.append({
                "position": (center_x, center_y),
                "dimensions": (template_width, template_height),
                "score": match.distance,  # Matching score
                "threshold": threshold
            })
        
        return template_matches
   