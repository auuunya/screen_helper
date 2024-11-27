import string
import random
import os
import cv2
import numpy as np
from typing import List, Tuple, Optional

def generate_random_string(length=8, use_letters=True, use_digits=True, use_punctuation=False):
    """
    生成一个随机字符串
    :param length: 随机字符串的长度
    :param use_letters: 是否包含字母（默认是 True）
    :param use_digits: 是否包含数字（默认是 True）
    :param use_punctuation: 是否包含特殊字符（默认是 False）
    :return: 随机字符串
    """
    characters = ""
    if use_letters:
        characters += string.ascii_letters
    if use_digits:
        characters += string.digits
    if use_punctuation:
        characters += string.punctuation

    if not characters:
        raise ValueError("至少需要包含一种字符类型（字母、数字或特殊字符）")

    return ''.join(random.choice(characters) for _ in range(length))
def is_x11_environment():
    """判断当前是否是 X11 环境"""
    display = os.environ.get("DISPLAY")
    return display is not None and display.startswith(":")

def configure_xhost(enable: bool = True) -> None:
    """
    配置 xhost 动态开启或关闭
    :param enable: True 为启用 (xhost +), False 为禁用 (xhost -)
    """
    try:
        if enable:
            os.system("xhost +")
        else:
            os.system("xhost -")
    except Exception as ex:
        raise RuntimeError(f"An error occurred while configuring xhost: {ex}")

def record_snapshot(screenshot: np.ndarray, screenshot_file: Optional[str] = "record_snapshot.png"):
    """
    保存当前快照到指定路径
    :param screenshot: 要保存的屏幕快照 (numpy 数组格式)
    :param file_path: 快照保存路径 (包含文件名及扩展名)，默认为 "screenshot.png"
    """
    try:
        cv2.imwrite(screenshot_file, screenshot)
    except cv2.error as e:
        raise ValueError(f"截屏保存出错: {str(e)}")

def draw_match(image: np.ndarray, 
                match: dict, 
                color: Tuple[int, int, int] = (0, 255, 0), 
                thickness: int = 2) -> np.ndarray:
    """
    在图像上绘制单个匹配的矩形框。
    
    :param image: 原始图像
    :param match: 匹配的字典，包含 'position' 和 'dimensions' 键
    :param color: 矩形框的颜色，默认为绿色 (B, G, R)
    :param thickness: 边框厚度，默认为 2
    :return: 绘制矩形框后的图像
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
    批量绘制多个匹配到的图像区域矩形框，允许自定义颜色、边框宽度，并可选择保存图像。
    
    :param image: 原始图像
    :param matches: 匹配到的区域字典列表，每个字典包含 'position' 和 'dimensions' 键
    :param color: 绘制框的颜色 (B, G, R)，默认为绿色
    :param thickness: 矩形框的边框宽度，默认为 2
    :return: 绘制所有匹配位置矩形框后的图像
    """
    image_copy = image.copy()
    for match in matches:
        image_copy = draw_match(image_copy, match, color=color, thickness=thickness)
    return image_copy