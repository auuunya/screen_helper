import cv2
import numpy as np
from typing import List, Tuple, Dict, Any, Union, Optional
import uuid
from core.utils import resize_entity

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
    def __init__(self):
        """
        Initialize the ImageMatcher object.
        """
        self.templates = {}
    # TODO: How to work?
    def generate_entity_config(self, entity: Union[str, np.ndarray], **kwargs) -> dict:
        """
        Generates an image configuration dictionary, accepting either an image path or a NumPy array.
        Args:
            entity: The image path (str) or image data (np.ndarray).
            **kwargs: Additional configuration options such as 'method', 'threshold', 'size', 'scale', 'interpolation'.
        Returns:
            A dictionary containing the image data, matching method, and other configuration information.
        Raises:
            ValueError: If the provided image path is invalid or the image cannot be loaded.
            ValueError: If neither 'size' nor 'scale' is provided.
            ValueError: If both 'size' and 'scale' are provided.
        """
        config = {
            "entity": entity,
            "method": kwargs.get("method", cv2.TM_CCOEFF_NORMED),
            "threshold": kwargs.get("threshold", 0.8),
            "size": kwargs.get("size", None),
            "scale": kwargs.get("scale", 1.0),
            "interpolation": kwargs.get("interpolation", cv2.INTER_LINEAR),
            **kwargs
        }
        mode = config.get("mode")
        # If the entity is a string (path), load the image.
        if isinstance(entity, str):
            try:
                config["entity"] = cv2.imread(entity, mode)
            except cv2.error as e:
                raise ValueError(f"Failed to load image from '{entity}': {e}")
        resized_entity = resize_entity(
            config["entity"],
            size=config["size"],
            scale=config["scale"],
            interpolation=config["interpolation"]
        )
        config["resized_entity"] = resized_entity
        return config
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

    def find_template_locations(
            self, 
            original_image: np.ndarray,
            original_template: np.ndarray,
            resized_image: np.ndarray = None, 
            resized_template: np.ndarray = None, 
            method: int = cv2.TM_CCOEFF_NORMED,
            threshold: float = None
        ) -> List[Dict[str, any]]:
        """
        Find all locations of the template in the screen image. 
        If resized images are not provided, use the original images for matching.
        
        :param resized_image: The screen image after resizing (scaled image), or None to use original_image.
        :param resized_template: The template image after resizing (scaled image), or None to use original_template.
        :param original_image: The original, unresized screen image.
        :param original_template: The original, unresized template image.
        :param method: The method used for template matching (default: cv2.TM_CCOEFF_NORMED).
        :param threshold: The minimum correlation value to consider a match as valid.
        :return: A list of dictionaries containing position, size, and match details for each match.
        
        Raises:
        RuntimeError: If no matches are found, or if threshold is not provided.
        """
        if threshold is None:
            raise RuntimeError("threshold is required for template matching.")
        
        screen_to_use = resized_image if resized_image is not None else original_image
        template_to_use = resized_template if resized_template is not None else original_template
        
        original_image_height, original_image_width = original_image.shape[:2]
        original_template_height, original_template_width = original_template.shape[:2]
        screen_height, screen_width = screen_to_use.shape[:2]
        template_height, template_width = template_to_use.shape[:2]

        scale_x_screen = screen_width / original_image_width
        scale_y_screen = screen_height / original_image_height
        scale_x_template = template_width / original_template_width
        scale_y_template = template_height / original_template_height

        match_result = cv2.matchTemplate(screen_to_use, template_to_use, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match_result)

        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            if min_val > threshold:
                raise RuntimeError(f"Match failed, current max value {min_val} did not reach the defined threshold {threshold}")
        else:
            if max_val < threshold:
                raise RuntimeError(f"Match failed, current max value {max_val} did not reach the defined threshold {threshold}")
        
        match_locations = []
        match_y_coords, match_x_coords = np.where(match_result >= threshold)
        
        for x, y in zip(match_x_coords, match_y_coords):
            original_x = int(x / scale_x_screen)
            original_y = int(y / scale_y_screen)
            original_template_width = int(template_width / scale_x_template)
            original_template_height = int(template_height / scale_y_template)

            center_x = int(original_x + original_template_width // 2)
            center_y = int(original_y + original_template_height // 2)
            match_locations.append(
                {
                    "template": self.add_image_template(template_to_use),
                    "position": (center_x, center_y),
                    "dimensions": (original_template_width, original_template_height),
                    "threshold": threshold
                }
            )
        return match_locations

    def match_template_with_contexts(
            self, 
            template_matches: List[dict], 
            context_matches: List[List[dict]],
            all_matching: bool = False
        ) -> Optional[List[dict]]:
        """
        Find all matching positions of the template in the screen image based on context conditions.

        :param template_matches: List of dictionaries containing matching positions and related information of the template.
        :param context_matches: List of dictionaries containing context template information to check for each match.
        :param all_matching: If True, all contexts must match for a successful result; otherwise, any matching context is enough.
        :return: A list of dictionaries containing match information if matches are found, or None if no match is found.
        """
        matching_results = []
        for match in template_matches:
            context_results = self.apply_context_filters_for_template(match, context_matches, all_matching)
            if context_results:
                match["context_matches"] = context_results
                matching_results.append(match)
                if not all_matching:
                    break
        return matching_results
    def apply_context_filters_for_template(
            self, 
            match: dict, 
            context_matches: List[List[dict]],  # A list of lists, each list is a set of context matches
            all_matching: bool
        ) -> Optional[List[dict]]:
        """
        Filter the context matches based on the provided contexts and return the detailed match information.
        If all_matching is True, every context template must have at least one valid match.

        :param match: Dictionary containing the matched position and related information for a template.
        :param context_matches: A list of lists, where each list contains context template matches for the template.
        :param all_matching: Flag indicating if all context conditions must match for a successful result.
        :return: A list of context match information if matches are found, or None if no matches are found.
        """
        context_results = []
        match_position = match.get('position')
        if not match_position:
            return None
        for context_set in context_matches:
            context_for_current_template = []
            for context in context_set:
                context_position = context.get("position")
                if not context_position:
                    continue
                offset = context.get("offset", {"x": 0, "y": 0})
                if abs(context_position[0] - match_position[0]) <= offset.get("x", 0) and \
                abs(context_position[1] - match_position[1]) <= offset.get("y", 0):
                    context_for_current_template.append(context)
            if context_for_current_template:
                context_results.append(context_for_current_template)
        if all_matching:
            if len(context_results) == len(context_matches):
                return context_results
            else:
                return None
        return context_results
    @staticmethod
    def preprocess_entity(entity: np.ndarray, options: Dict[str, Any] = None) -> np.ndarray:
        """
        Preprocess the input entity dynamically based on the provided options (grayscale, blur, histogram equalization, binarization).
        
        :param entity: Input entity as a NumPy array (image).
        :param options: Preprocessing options which control grayscale conversion, blurring, histogram equalization, and binarization.
        :return: Preprocessed entity (image).
        """
        if options is None:
            options = {}
        processed_entity = entity.copy()
        # Noise reduction processing
        if options.get("denoise", False):
            denoise_method = options.get("denoise_method", "median")
            kernel_size = options.get("denoise_kernel_size", 3)
            
            if denoise_method == "median":
                processed_entity = cv2.medianBlur(processed_entity, kernel_size)
            elif denoise_method == "gaussian":
                processed_entity = cv2.GaussianBlur(processed_entity, (kernel_size, kernel_size), 0)

        # Convert to grayscale if specified
        if options.get('gray', False):
            processed_entity = cv2.cvtColor(processed_entity, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur if specified
        if options.get('blur', False):
            blur_kernel_size = options.get('blur_kernel_size', (5, 5))
            processed_entity = cv2.GaussianBlur(processed_entity, blur_kernel_size, 0)

        # Apply histogram equalization if specified (only on grayscale images)
        if options.get('equalize', False) and len(processed_entity.shape) == 2:
            processed_entity = cv2.equalizeHist(processed_entity)
        
        # Apply binary thresholding if specified
        if options.get("threshold", False):
            if len(processed_entity.shape) == 3:
                processed_entity = cv2.cvtColor(processed_entity, cv2.COLOR_BGR2GRAY)
            threshold_value = options.get("threshold_value", 150)
            threshold_max_value = options.get("threshold_max_value", 255)
            threshold_mode = options.get("threshold_mode", cv2.THRESH_BINARY)
            _, processed_entity = cv2.threshold(processed_entity, threshold_value, threshold_max_value, threshold_mode)
        
        # Invert the image if specified
        if options.get("invert", False):
            processed_entity = cv2.bitwise_not(processed_entity)
        
        # Apply Canny edge detection if specified
        if options.get("canny_edge", False):
            lower_threshold = options.get("canny_lower_threshold", 100)
            upper_threshold = options.get("canny_upper_threshold", 200)
            processed_entity = cv2.Canny(processed_entity, lower_threshold, upper_threshold)
        
        # Apply custom function if specified
        if "custom_function" in options and callable(options["custom_function"]):
            processed_entity = options["custom_function"](processed_entity)
        
        return processed_entity

    @staticmethod
    def are_entities_compatible(*entities: np.ndarray) -> bool:
        """
        Check if the provided entities are compatible for OpenCV operations by matching dtype and shape.
        
        :param entities: A variable number of entities (images) to check.
        :return: True if all entities have the same dtype and shape, otherwise False.
        """
        if len(entities) < 2:
            return True

        first_entity_dtype = entities[0].dtype
        first_entity_shape = entities[0].shape

        for entity in entities[1:]:
            if entity.dtype != first_entity_dtype or entity.shape != first_entity_shape:
                return False
        return True

    @staticmethod
    def calculate_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """
        Calculate the Euclidean distance between two positions.

        :param pos1: First position as a tuple (x, y).
        :param pos2: Second position as a tuple (x, y).
        :return: Euclidean distance between the two positions.
        """
        return np.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    @staticmethod
    def compare_entities(
        entity1: np.ndarray,
        entity2: np.ndarray,
        method: int,
        similarity_threshold: float = 0.9
    ) -> bool:
        """
        Compare two entities (images) for similarity using a threshold.

        :param entity1: The first entity (image).
        :param entity2: The second entity (image).
        :param method: The method used for comparison (e.g., cv2.TM_CCOEFF_NORMED).
        :param similarity_threshold: Similarity threshold, default is 0.9.
        :return: Returns True if the images are considered different, False if they are similar.
        """
        similarity_map = cv2.matchTemplate(entity1, entity2, method)
        max_similarity = np.max(similarity_map)
        return max_similarity < similarity_threshold

    @staticmethod
    def filter_nearby_matches(
        matches: List[Dict[str, Any]],
        min_distance: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Filter out matches that are too close to each other based on a minimum distance.
        
        :param matches: A list of match results.
        :param min_distance: The minimum distance, only matches with distance greater than this will be retained.
        :return: A filtered list of matches.
        """
        filtered_matches = []
        for match in matches:
            center_x, center_y = match["position"]
            too_close = False
            for filtered_match in filtered_matches:
                existing_x, existing_y = filtered_match["position"]
                if abs(center_x - existing_x) < min_distance and abs(center_y - existing_y) < min_distance:
                    too_close = True
                    break
            if not too_close:
                filtered_matches.append(match)
        return filtered_matches