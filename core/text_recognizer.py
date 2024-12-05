import cv2
import numpy as np
from typing import List, Tuple

class TextRecognizer:
    """
    This class provides static methods for recognizing text positions within an OCR result.
    It allows searching for text within OCR data, finding the position and size of text blocks,
    and verifying if the text is near a specific context.

    Methods:
        find_all_text_positions: Finds all occurrences of a target text and their center positions.
        find_text_position: Finds the position of a target text based on context and optional matching conditions.
        _is_context_near: Verifies if a context text is near the target text within the specified offsets.
    """

    @staticmethod
    def find_all_text_positions(data: dict, target_text: str) -> List[Tuple[str, Tuple[int, int]]]:
        """
        Finds all occurrences of the target text and their center positions in the OCR data.
        
        :param data: The OCR result dictionary, containing 'text', 'left', 'top', 'width', 'height' lists.
        :param target_text: The target text to search for.
        :return: A list of dictionaries with the matching text and its center position, including the width and height.
        """
        text_positions = []
        target_lower = target_text.lower()
        
        # Search for all occurrences of the target text
        for i, word in enumerate(data['text']):
            if target_lower in word.lower():
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                center_x = x + 0.5 * w
                center_y = y + 0.5 * h
                text_positions.append(
                    {
                        "text": word,
                        "position": (center_x, center_y),
                        "dimensions": (w, h)
                    }
                )
        return text_positions

    @staticmethod
    def find_text_position(data: dict, target_text: str, contexts: List[dict] = None, all_matching: bool = False) -> dict:
        """
        Finds the position of the target text based on contexts. It checks if the target text is close to 
        specific context text blocks within the OCR data.
        
        :param data: The OCR result dictionary, containing 'text', 'left', 'top', 'width', 'height' lists.
        :param target_text: The target text to search for.
        :param contexts: A list of context dictionaries with 'text' and 'offset' for verifying proximity, 
                         e.g., [{"text": "control", "offset": {"x": 10, "y": 10}}, ...].
        :param all_matching: A flag indicating if all contexts must match the target text. Defaults to False.
        :return: A dictionary with the matching text position, dimensions, and context matches, or None if no match is found.
        """
        target_lower = target_text.lower()
        potential_matches = []

        # Search for potential matches of the target text
        for i, word in enumerate(data['text']):
            if target_lower in word.lower():
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                center_x = x + 0.5 * w
                center_y = y + 0.5 * h
                potential_matches.append({
                    "text": word,
                    "position": (center_x, center_y),
                    "dimensions": (w, h)
                })
        if not potential_matches:
            return None
        if not contexts:
            return None
        
        # Check if the contexts match the potential matches
        for match in potential_matches:
            context_results = []
            for context in contexts:
                context_result = TextRecognizer._is_context_near(data, context, match["position"][0], match["position"][1], *match["dimensions"])
                if context_result:
                    context_results.append(context_result)
            if all_matching:
                if len(context_results) == len(contexts):
                    match["context_matches"] = context_results
                    return match
            else:
                if context_results:
                    match["context_matches"] = context_results
                    return match
        return None

    @staticmethod
    def _is_context_near(data: dict, context: dict, x: int, y: int, width: int, height: int) -> dict:
        """
        Verifies if a context text is near the target text within the specified offsets.
        
        :param data: The OCR result dictionary containing 'text', 'left', 'top', 'width', 'height' lists.
        :param context: A dictionary containing the context 'text' and 'offset' for proximity check.
                        E.g., {"text": "control", "offset": {"x": 10, "y": 10}}.
        :param x: The x-coordinate of the target text's center.
        :param y: The y-coordinate of the target text's center.
        :param width: The width of the target text block.
        :param height: The height of the target text block.
        :return: A dictionary with context text and its position if it's near the target text within the offset range, or None if not.
        """
        context_text = context.get("text")
        offset = context.get("offset", {"x": 0, "y": 0})
        if not context_text:
            return None
        context_lower = context_text.lower()
        current_center = (x + 0.5 * width, y + 0.5 * height)
        for i, word in enumerate(data['text']):
            if context_lower in word.lower():
                cx, cy = data['left'][i], data['top'][i]
                word_width, word_height = data['width'][i], data['height'][i]
                context_center = (cx + 0.5 * word_width, cy + 0.5 * word_height)
                # Check if the context is within the specified offset range
                if (abs(context_center[0] - current_center[0]) <= offset.get("x", 0) and 
                    abs(context_center[1] - current_center[1]) <= offset.get("y", 0)):
                    return {
                        "text": word,
                        "position": (context_center[0], context_center[1]),
                        "dimensions": (word_width, word_height)
                    }
        return None
