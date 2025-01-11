from typing import List, Tuple, Optional, Dict
import utils
class TextRec:
    """
    A class for recognizing and matching text in OCR data, including finding positions
    of matching text and verifying the context of text around a target.
    """

    def generate_text_config(self, text: str, **kwargs) -> dict:
        """
        Generate a configuration dictionary for the target text with optional parameters.

        :param text: The target text to search for.
        :param kwargs: Additional configuration options, such as 'match_mode', 'min_conf', and 'case'.
        :return: A dictionary containing the target text and its configuration.
        """
        config = {
            "text": text,
            "match_mode": kwargs.get("match_mode", "contains"),
            "min_conf": kwargs.get("min_conf", 0),
            "case": kwargs.get("case", True),
            **kwargs
        }
        return config

    def _calculate_center_position(self, left: int, top: int, width: int, height: int) -> Tuple[int, int]:
        """
        Calculate the center position (x, y) of a bounding box based on its left, top, width, and height.

        :param left: The x-coordinate of the top-left corner of the bounding box.
        :param top: The y-coordinate of the top-left corner of the bounding box.
        :param width: The width of the bounding box.
        :param height: The height of the bounding box.
        :return: A tuple (center_x, center_y) representing the center position of the bounding box.
        """
        center_x = int(left + 0.5 * width)
        center_y = int(top + 0.5 * height)
        return center_x, center_y

    def _is_text_match(self, text: str, target: str, match_mode: str, case: bool) -> bool:
        """
        Check if a given text matches the target text according to the specified matching rules.

        :param text: The text to be matched.
        :param target: The target text to match against.
        :param match_mode: Whether the match should be "contains","exact",reg, or partial.
        :param case: Whether the match should be case-sensitive.
        :return: True if the text matches the target, otherwise False.
        """
        return utils.match_text(text, target, match_mode, case)

    def find_matching_text_positions(
        self,
        ocr_data: dict,
        target_config: dict
    ) -> List[dict]:
        """
        Find all positions of matching text based on OCR data and target configuration.

        :param ocr_data: OCR result dictionary containing keys 'text', 'left', 'top', 'width', 'height', 'conf'.
        :param target_config: Configuration dictionary for the target text with keys like 'text', 'match_mode', 'min_conf', 'case'.
        :return: A list of dictionaries containing the matched text and its position and dimensions. If no match is found, return None.
        """
        target_text = target_config.get("text", "")
        match_mode = target_config.get("match_mode", "contains")
        min_conf = target_config.get("min_conf", 0)
        case = target_config.get("case", True)
        
        matching_positions = []

        for i, word in enumerate(ocr_data['text']):
            if ocr_data['conf'][i] < min_conf:
                continue
            
            if self._is_text_match(word, target_text, match_mode, case):
                x, y, w, h = ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i]
                center_position = self._calculate_center_position(x, y, w, h)
                matching_positions.append({
                    "text": word.strip(),
                    "position": center_position,
                    "dimensions": (w, h)
                })

        return matching_positions if matching_positions else None
    def find_position_on_context(
        self,
        ocr_data: Dict[str, List],  # OCR result dictionary
        target_matches: List[Dict[str, object]],  # Pre-matched target text list from find_matching_text_positions
        context_configs: Optional[List[Dict[str, object]]] = None,  # List of context text configurations
        require_all_matches: Optional[bool] = False
    ) -> Optional[List[Dict[str, object]]]:
        """
        Find the position of a target text based on its context in OCR data.

        :param ocr_data: OCR result dictionary containing 'text', 'left', 'top', 'width', 'height', 'conf'.
        :param target_matches: List of pre-matched target text positions with 'text', 'position', and 'dimensions'.
        :param context_configs: A list of context text configurations with optional offset and matching rules.
        :param require_all_matches: Whether all context texts must match. Default is False (at least one context match is required).
        :return: A list of matched target text positions with their context information, or None if no matches are found.
        """
        if not context_configs or not target_matches:
            return None

        matching_results = []
        
        for match in target_matches:
            context_matches = []
            for context_config in context_configs:
                context_match = self._is_context_nearby(
                    ocr_data,
                    context_config,
                    match["position"][0],
                    match["position"][1]
                )
                if context_match:
                    context_matches.append(context_match)

            # If require_all_matches is True, all context must match
            if require_all_matches:
                if len(context_matches) == len(context_configs):
                    match["context_matches"] = context_matches
                    matching_results.append(match)
            # Otherwise, at least one context match is enough
            else:
                if context_matches:
                    match["context_matches"] = context_matches
                    matching_results.append(match)

        return matching_results if matching_results else None
    def _is_context_nearby(
        self, 
        ocr_data: Dict[str, List],  # OCR result dictionary
        context_config: Dict[str, object],  # Context text configuration
        target_x: int, 
        target_y: int
    ) -> Optional[Dict[str, object]]:
        """
        Check if a context text is nearby the target text and meets the offset requirements.

        :param ocr_data: OCR result dictionary.
        :param context_config: Configuration for the context text, including its offset and matching rules.
        :param target_x: The x-coordinate of the target text.
        :param target_y: The y-coordinate of the target text.
        :return: The context text information if it's nearby the target, otherwise None.
        """
        context_text = context_config.get("text")
        offset = context_config.get("offset", {"x": 0, "y": 0})
        match_mode = context_config.get("match_mode", "contains")
        min_conf = context_config.get("min_conf", 0)
        case = context_config.get("case", True)

        if not context_text:
            return None

        # context_lower = context_text.lower() if not case else context_text
        current_center = (target_x, target_y)

        for idx, word in enumerate(ocr_data['text']):
            if ocr_data['conf'][idx] < min_conf:
                continue

            # word_to_compare = word if case else word.lower()
            # Match the context text
            # if (exact and word_to_compare == context_lower) or (not exact and context_lower in word_to_compare):
            if utils.match_text(word, context_text, match_mode, case):
                left, top = ocr_data['left'][idx], ocr_data['top'][idx]
                word_width, word_height = ocr_data['width'][idx], ocr_data['height'][idx]
                context_center = self._calculate_center_position(left, top, word_width, word_height)

                # Check if the context is within the offset range
                if (abs(context_center[0] - current_center[0]) <= offset.get("x", 0) and 
                    abs(context_center[1] - current_center[1]) <= offset.get("y", 0)):
                    return {
                        "text": word,
                        "position": context_center,
                        "dimensions": (word_width, word_height)
                    }
        return None
    # bad context func
    # def find_position_on_context(
    #     self,
    #     ocr_data: Dict[str, List],  # OCR data dictionary
    #     target_config: Dict[str, object],  # Target text configuration dictionary
    #     context_configs: Optional[List[Dict[str, object]]] = None,  # List of context text configurations
    #     require_all_matches: Optional[bool] = False
    # ) -> Optional[List[Dict[str, object]]]:
    #     """
    #     Find the position of a target text based on its context in OCR data.

    #     :param ocr_data: OCR result dictionary containing 'text', 'left', 'top', 'width', 'height', 'conf'.
    #     :param target_config: Configuration dictionary for the target text.
    #     :param context_configs: A list of context text configurations with optional offset and matching rules.
    #     :param require_all_matches: Whether all context texts must match. Default is False (at least one context match is required).
    #     :return: A list of matched target text positions with their context information, or None if no matches are found.
    #     """
    #     if not context_configs:
    #         return None

    #     target_text = target_config.get("text", "")
    #     exact = target_config.get("exact", True)
    #     min_conf = target_config.get("min_conf", 0)
    #     case = target_config.get("case", True)

    #     potential_matches = []

    #     for idx, word in enumerate(ocr_data['text']):
    #         # Filter out words with low conf
    #         if ocr_data['conf'][idx] < min_conf:
    #             continue

    #         # Check if the target text matches
    #         if self._is_text_match(word, target_text, exact, case):
    #             left, top, width, height = ocr_data['left'][idx], ocr_data['top'][idx], ocr_data['width'][idx], ocr_data['height'][idx]
    #             center_position = self._calculate_center_position(left, top, width, height)
    #             potential_matches.append({
    #                 "text": word,
    #                 "position": center_position,
    #                 "dimensions": (width, height)
    #             })

    #     if not potential_matches:
    #         return None

    #     matching_results = []
    #     for match in potential_matches:
    #         context_matches = []
    #         for context_config in context_configs:
    #             context_match = self._is_context_nearby(
    #                 ocr_data,
    #                 context_config,
    #                 match["position"][0],
    #                 match["position"][1]
    #             )
    #             if context_match:
    #                 context_matches.append(context_match)

    #         # If require_all_matches is True, all context must match
    #         if require_all_matches:
    #             if len(context_matches) == len(context_configs):
    #                 match["context_matches"] = context_matches
    #                 matching_results.append(match)
    #         # Otherwise, at least one context match is enough
    #         else:
    #             if context_matches:
    #                 match["context_matches"] = context_matches
    #                 return [match]

    #     return matching_results