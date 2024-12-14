import string
import random
import os
import cv2
import re
import numpy as np
import glob
from typing import List, Tuple, Optional, Any

def generate_random_string(
        length: int = 8, 
        use_letters: bool = True, 
        use_digits: bool = True, 
        use_punctuation: bool = False
    ) -> str:
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

def record_snapshot(
    image: np.ndarray, 
    record_file: Optional[str] = "record_snapshot.png"
):
    """
    Save the current snapshot to the specified path.
    :param image: The screen snapshot to save (numpy array format).
    :param record_file: The file path to save the snapshot (including filename and extension), defaults to "record_snapshot.png".
    """
    try:
        cv2.imwrite(record_file, image)
    except cv2.error as e:
        raise ValueError(f"Error saving snapshot: {str(e)}")

def load_entity_file(
    entity_file: Optional[str], 
    read_mode: Optional[int] = None
) -> np.ndarray:
    """
    Loads the entity file and returns a NumPy array representation of the image.

    :param entity_file: path to the image file. FileNotFoundError is raised if None
    :return: Loads the image as NumPy array
    raises FileNotFoundError: If the image path is None or the image fails to load
    """
    if entity_file is None:
        raise FileNotFoundError(f"Entity file not found: {entity_file}")
    if read_mode is not None:
        entity = cv2.imread(entity_file, read_mode)
    else:
        entity = cv2.imread(entity_file)
    if entity is None:
        raise FileNotFoundError(f"Failed to load entity file: {entity_file}")
    return entity

def draw_match(
    image: np.ndarray, 
    match: dict, 
    color: Tuple[int, int, int] = (0, 255, 0), 
    thickness: int = 2
) -> np.ndarray:
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

def match_title(
    text: str, 
    pattern: str, 
    match_mode: str = "exact", 
    ignore_case: bool = False
) -> bool:
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

def resize_entity(
    entity: np.ndarray, 
    size: Optional[Tuple[int, int]] = None, 
    scale: Optional[float] = None, 
    interpolation: int = cv2.INTER_LINEAR
) -> np.ndarray:
    """
    A general method for resizing an image, supporting both fixed size and scaling by a factor.

    :param entity: The input entity, numpy array.
    :param size: The target size for the image (width, height). If provided, scale_factor will be ignored.
    :param scale: The scaling factor, indicating how much to enlarge or shrink the image (e.g., 2 means double the size).
    :param interpolation: The interpolation method for resizing.
    :return: The resized image, numpy array.
    """
    if size is None and scale is None:
        raise ValueError("Either size or scale must be provided.")
    if size is not None and scale is not None:
        raise ValueError("Cannot specify both size and scale.")
    height, width = entity.shape[:2]
    if size is not None:
        new_width, new_height = size
    elif scale is not None:
        new_width = int(width * scale)
        new_height = int(height * scale)
    resized_image = cv2.resize(entity, (new_width, new_height), interpolation=interpolation)
    return resized_image

def create_directory(
    dirs: str, 
    empty: bool = False
) -> None:
    """
    Create a directory for saving screenshots.

    :param dirs: Directory path where screenshots will be saved.
    :raises ValueError: If there is an error creating the directory.
    """
    try:
        if os.path.exists(dirs):
            for file in glob.glob(os.path.join(dirs, "*")):
                if empty:
                    try:
                        os.remove(file)
                    except Exception as e:
                        raise RuntimeError(f"Error delete file {file}: {e}")
        else:
            os.makedirs(dirs)
    except OSError as e:
        raise ValueError(f"Error creating screenshot directory: {str(e)}")

def convert_to_serializable(obj: Any) -> Any:
    """
    Convert a given object to a serializable form. It handles conversion for specific types like 
    numpy's float32, lists, and dictionaries to ensure they can be serialized into standard Python types.

    Parameters:
    obj (Any): The object to be converted.

    Returns:
    Any: A serializable version of the input object.

    Raises:
    TypeError: If the object type is not supported for conversion.
    """
    if isinstance(obj, np.float32):
        return float(obj)
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    else:
        return obj