import string
import random
import os
import cv2
import re
import numpy as np
from typing import List, Tuple, Optional

def generate_random_string(length=8, use_letters=True, use_digits=True, use_punctuation=False):
    """
    Generate a random string.
    :param length: Length of the random string.
    :param use_letters: Whether to include letters (default is True).
    :param use_digits: Whether to include digits (default is True).
    :param use_punctuation: Whether to include special characters (default is False).
    :return: A random string.
    """
    characters = ""
    if use_letters:
        characters += string.ascii_letters
    if use_digits:
        characters += string.digits
    if use_punctuation:
        characters += string.punctuation

    if not characters:
        raise ValueError("At least one character type (letters, digits, or special characters) must be included.")

    return ''.join(random.choice(characters) for _ in range(length))

def is_x11_environment():
    """Check if the current environment is X11."""
    display = os.environ.get("DISPLAY")
    return display is not None and display.startswith(":")

def configure_xhost(enable: bool = True) -> None:
    """
    Configure xhost to enable or disable dynamically.
    :param enable: True to enable (xhost +), False to disable (xhost -).
    """
    try:
        if enable:
            os.system("xhost +")
        else:
            os.system("xhost -")
    except Exception as ex:
        raise RuntimeError(f"An error occurred while configuring xhost: {ex}")

def record_snapshot(image: np.ndarray, record_file: Optional[str] = "record_snapshot.png"):
    """
    Save the current snapshot to the specified path.
    :param image: The screen snapshot to save (numpy array format).
    :param record_file: The file path to save the snapshot (including filename and extension), defaults to "record_snapshot.png".
    """
    try:
        cv2.imwrite(record_file, image)
    except cv2.error as e:
        raise ValueError(f"Error saving snapshot: {str(e)}")

def load_image_file(template_path: str) -> np.ndarray:
    """
    Load a template and handle potential exceptions.
    """
    try:
        context_template_ndarray = cv2.imread(template_path)
        return context_template_ndarray
    except Exception:
        raise ValueError(f"Could not read template: {template_path}")

def draw_match(image: np.ndarray, 
                match: dict, 
                color: Tuple[int, int, int] = (0, 255, 0), 
                thickness: int = 2) -> np.ndarray:
    """
    Draw a rectangle around a matched region in the image.
    
    :param image: The original image.
    :param match: A dictionary containing 'position' and 'dimensions' keys for the matched region.
    :param color: The color of the rectangle (B, G, R), default is green.
    :param thickness: The thickness of the rectangle border, default is 2.
    :return: The image with the rectangle drawn around the matched region.
    """
    x, y = match["position"]
    width, height = match["dimensions"]
    top_left = (int(x - width / 2), int(y - height / 2))
    bottom_right = (int(x + width / 2), int(y + height / 2))
    cv2.rectangle(image, top_left, bottom_right, color, thickness)
    return image

def draw_matches(
    image: np.ndarray, 
    matches: List[dict], 
    color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2,
) -> np.ndarray:
    """
    Draw rectangles around multiple matched regions in the image, allowing customization of colors, border width, and saving the image.
    
    :param image: The original image.
    :param matches: A list of dictionaries containing matched region details, each with 'position' and 'dimensions' keys.
    :param color: The color of the rectangles (B, G, R), default is green.
    :param thickness: The thickness of the rectangle borders, default is 2.
    :return: The image with rectangles drawn around all matched regions.
    """
    image_copy = image.copy()
    for match in matches:
        image_copy = draw_match(image_copy, match, color=color, thickness=thickness)
    return image_copy

def match_title(text, pattern, match_mode="exact", ignore_case=False):
    """
    Compare the window title with the given pattern for matching.
    
    Parameters:
    text (str): The window title to match.
    pattern (str): The pattern to match, which can be a specific string or regular expression.
    match_mode (str): The matching mode, supports the following options:
                      - "exact": Exact match, the window title must exactly match the pattern.
                      - "contains": Contains match, checks if the window title contains the pattern.
                      - "regex": Regex match, uses the regular expression pattern to match.
    ignore_case (bool): Whether to ignore case when matching. If True, case is ignored.
    
    Returns:
    bool: True if the window title matches the pattern, False otherwise.
    
    Exceptions:
    ValueError: Raised if the matching mode is invalid or the regular expression is invalid.
    """
    if ignore_case:
        text = text.lower()
        pattern = pattern.lower()
    if match_mode == "exact":
        return text == pattern
    elif match_mode == "contains":
        return pattern in text
    elif match_mode == "regex":
        try:
            return re.search(pattern, text) is not None
        except re.error:
            raise ValueError(f"Invalid regular expression: {pattern}")
    else:
        raise ValueError(f"Invalid match mode: {match_mode}")
