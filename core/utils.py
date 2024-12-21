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

def draw_shape(
    image: np.ndarray, 
    shape: str,  # 新增形状类型参数
    position: Tuple[int, int], 
    size: Tuple[int, int], 
    color: Tuple[int, int, int] = (0, 255, 0), 
    thickness: int = 1
) -> np.ndarray:
    """
    Draw a shape (rectangle, circle, or ellipse) on the image.
    
    :param image: The original image.
    :param shape: The type of shape to draw ('rectangle', 'circle', 'ellipse').
    :param position: The top-left position for rectangles, or the center for circles/ellipses (x, y).
    :param size: The dimensions for rectangles (width, height) or radius for circles (radius) or axes for ellipses (major, minor).
    :param color: The color of the shape (B, G, R), default is green.
    :param thickness: The thickness of the shape's border, default is 1.
    :return: The image with the shape drawn.
    """
    x, y = position
    if shape == 'rectangle':
        width, height = size
        cv2.rectangle(image, (x, y), (x + width, y + height), color, thickness)
    elif shape == 'circle':
        radius = size[0]  # Only the first value of size is used as radius
        cv2.circle(image, (x, y), radius, color, thickness)
    elif shape == 'ellipse':
        major_axis, minor_axis = size  # major axis and minor axis for ellipse
        cv2.ellipse(image, (x, y), (major_axis, minor_axis), 0, 0, 360, color, thickness)
    else:
        raise ValueError(f"Unsupported shape type: {shape}")
    return image

def draw_shapes(
    image: np.ndarray, 
    shapes: List[str],  # List of shapes for each region
    positions: List[Tuple[int, int]],  # List of positions
    sizes: List[Tuple[int, int]],  # List of sizes (width, height) for rectangles or (radius) for circles
    border_color: Tuple[int, int, int] = (0, 255, 0), 
    border_thickness: int = 1
) -> np.ndarray:
    """
    Draw shapes on the image (rectangle, circle, ellipse).
    
    :param image: The original image.
    :param shapes: A list of shapes to draw ('rectangle', 'circle', 'ellipse').
    :param positions: A list of positions for each shape.
    :param sizes: A list of sizes for each shape (width, height) for rectangles, (radius) for circles, or (major_axis, minor_axis) for ellipses.
    :param border_color: The color of the shapes (B, G, R), default is green.
    :param border_thickness: The thickness of the shape borders, default is 1.
    :return: The image with all shapes drawn.
    """
    if len(shapes) != len(positions) or len(shapes) != len(sizes):
        raise ValueError("The number of shapes must match the number of positions and sizes.")
    
    result_image = image.copy()
    for shape, position, size in zip(shapes, positions, sizes):
        result_image = draw_shape(result_image, shape, position, size, color=border_color, thickness=border_thickness)
    return result_image

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

def calculate_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """
    Calculate the Euclidean distance between two positions.

    :param pos1: First position as a tuple (x, y).
    :param pos2: Second position as a tuple (x, y).
    :return: Euclidean distance between the two positions.
    """
    return np.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

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

def draw_text(
    image: np.ndarray,
    text: str,
    position: Tuple[int, int],
    font_scale: float = 0.5,
    font_color: Tuple[int, int, int] = (0, 255, 0),
    border_color: Optional[Tuple[int, int, int]] = (0, 0, 0),
    border_thickness: Optional[int] = None,
    thickness: int = 1,
    alignment: str = "left"
    ) -> np.ndarray:
    """
    Draws text on an image, with dynamic border thickness and alignment support.
    :param image: original image (BGR format)
    :param text: the content of the text to be drawn.
    :param position: the position (x, y) of the bottom left corner of the text.
    :param font_scale: the scale of the font size, default is 0.5
    :param font_color: font color (B, G, R), default is green
    :param border_color: border color (B, G, R), if None, then no border is drawn
    :param border_thickness: the thickness of the border, if None, it will be calculated dynamically according to the font size
    :param thickness: thickness of the font, default is 1
    :param alignment: alignment mode, can be “left”, “center”, “right”, default is “left”.
    :return: the image after drawing the text
    """
    image_copy = image.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX

    if border_thickness is None:
        border_thickness = max(1, int(font_scale * 2))

    text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
    text_width, text_height = text_size
    x, y = position

    if alignment == "center":
        x -= text_width // 2
    elif alignment == "right":
        x -= text_width

    if border_color:
        cv2.putText(image_copy, text, (x - border_thickness, y), font, font_scale, border_color, thickness + border_thickness, lineType=cv2.LINE_AA)
        cv2.putText(image_copy, text, (x + border_thickness, y), font, font_scale, border_color, thickness + border_thickness, lineType=cv2.LINE_AA)
        cv2.putText(image_copy, text, (x, y - border_thickness), font, font_scale, border_color, thickness + border_thickness, lineType=cv2.LINE_AA)
        cv2.putText(image_copy, text, (x, y + border_thickness), font, font_scale, border_color, thickness + border_thickness, lineType=cv2.LINE_AA)

    cv2.putText(image_copy, text, (x, y), font, font_scale, font_color, thickness, lineType=cv2.LINE_AA)
    return image_copy