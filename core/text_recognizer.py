import cv2
import numpy as np
from typing import List, Tuple
class TextRecognizer:
    @staticmethod
    def find_all_text_positions(data: dict, target_text: str) -> List[Tuple[str, Tuple[int, int]]]:
        """
        查找匹配目标文本的文本及其中心坐标。
        
        :param data: OCR 识别结果字典，包含 {'text': [...], 'left': [...], 'top': [...], 'width': [...], 'height': [...]}
        :param target_text: 要查找的目标文本
        :return: 所有匹配文本及其信息的列表，格式为 [{ "word": "文本", "center_position": (center_x, center_y), "size": (width, height) }, ...]
        """
        text_positions = []
        target_lower = target_text.lower()
        
        # 查找所有匹配的文本
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
        根据上下文查找指定文本的位置。
        
        :param data: OCR 识别结果字典，包含 {'text': [...], 'left': [...], 'top': [...], 'width': [...], 'height': [...]}
        :param target_text: 要查找的目标文本
        :param contexts: 上下文文本列表和偏移量，格式为 [{"text": "control", "offset": {"x": 10, "y": 10}}, ...]
        :param all_matching: 是否要求所有上下文都匹配，默认为 False
        :return: 包含目标文本位置、大小和匹配状态的字典，如果没有找到，则返回 None
        """
        target_lower = target_text.lower()
        potential_matches = []

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
        检查某个上下文文本是否在指定坐标附近，并符合偏移要求。
        
        :param data: OCR 识别结果的字典
        :param context: 包含上下文文本和偏移的字典 {"text": "control", "offset": {"x": 10, "y": 10}}
        :param x: 当前文本块的 x 坐标
        :param y: 当前文本块的 y 坐标
        :param width: 当前文本块的宽度
        :param height: 当前文本块的高度
        :return: 如果上下文文本在指定坐标附近并符合偏移则返回其信息，否则返回 None
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
                # 检查上下文文本的位置是否在偏移量范围内
                if (abs(context_center[0] - current_center[0]) <= offset.get("x", 0) and 
                    abs(context_center[1] - current_center[1]) <= offset.get("y", 0)):
                    return {
                        "text": word,
                        "position": (context_center[0], context_center[1]),
                        "dimensions": (word_width, word_height)
                    }
        return None
    
    @staticmethod
    def draw_match(image: np.ndarray, match: dict, color: Tuple[int, int, int] = (0, 255, 0), thickness: int = 2) -> np.ndarray:
        """
        在图像上绘制单个匹配的矩形框。
        
        :param image: 原始图像
        :param match: 匹配的字典，包含 'position' 和 'dimensions' 键
        :param color: 矩形框的颜色
        :param thickness: 边框厚度
        """
        center_x, center_y = match["position"]
        width, height = match["dimensions"]
        top_left = (int(center_x - width / 2), int(center_y - height / 2))
        bottom_right = (int(center_x + width / 2), int(center_y + height / 2))
        cv2.rectangle(image, top_left, bottom_right, color, thickness)
        return image

    @staticmethod
    def draw_matches(image: np.ndarray, matches: List[dict], 
                     color: Tuple[int, int, int] = (0, 255, 0), thickness: int = 2) -> np.ndarray:
        """
        批量绘制多个匹配到的文本区域矩形框。
        
        :param image: 原始图像
        :param matches: 匹配到的坐标和尺寸列表 [(center_x1, center_y1, width1, height1), ...]
        :param color: 绘制框的颜色 (B, G, R)，默认为绿色
        :param thickness: 矩形框的边框宽度，默认为 2
        :return: 绘制所有匹配位置矩形框的图像
        """
        image_copy = image.copy()
        for match in matches:
            image_copy = TextRecognizer.draw_match(image_copy, match, color=color, thickness=thickness)
        return image_copy