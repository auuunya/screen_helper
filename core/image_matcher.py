import cv2
import numpy as np
from typing import List, Dict, Any, Optional

class ImageMatcher:
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