#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   image_matcher.py
@Desc    :   None
'''

# here put the import lib
import cv2
import numpy as np
from typing import List, Tuple, Dict, Any, Union
import uuid
from .config import BaseConfig

class Template:
    def __init__(self, identifier: str, template_image: np.ndarray):
        """
        初始化模板对象
        :param identifier: 模板的唯一标识符
        :param template_image: 模板图像的 NumPy 数组
        """
        self.identifier = identifier
        self.template_image = template_image

class ImageMatcher:

    def __init__(self, scale_factor: float = 1, threshold: float = 0.8):
        """
        初始化图像匹配器
        :param scale_factor: 图像缩放因子，用于调整待匹配图像的大小
        :param threshold: 匹配的阈值，控制匹配的灵敏度
        """
        self.scale_factor = scale_factor
        self.threshold = threshold
        self.templates = {}

    @classmethod
    def from_config(cls, config: BaseConfig):
        """
        从配置类创建 ImageMatcher 实例
        :param config: BaseConfig 的实例
        :return: ImageMatcher 实例
        """
        return cls(scale_factor=config.scale_factor, threshold=config.threshold)

    def add_image_template(self, template_image: np.ndarray) -> str:
        """
        添加模板到匹配器
        :param template_image: 模板图像的 NumPy 数组
        :return: 模板的唯一标识符
        """
        template_id = f"templates_{uuid.uuid4()}"
        self.templates[template_id] = Template(template_id, template_image)
        return template_id

    def retrieve_template(self, identifier: str) -> np.ndarray:
        """
        根据标识符获取模板图像
        :param identifier: 模板的唯一标识符
        :return: 对应的模板图像 NumPy 数组，如果未找到则返回 None
        """
        template = self.templates.get(identifier)
        return template.template_image if template else None
    
    @staticmethod
    def preprocess_input_image(image: np.ndarray, options: Dict[str, Any] = None) -> np.ndarray:
        """
        动态预处理图像，根据提供的选项调整预处理流程（灰度、模糊、直方图均衡、二值化）
        
        :param image: 输入的图像（numpy 数组格式）
        :param options: 预处理选项，可以控制是否进行灰度转换、模糊处理、直方图均衡、二值化等
        :return: 预处理后的图像
        """
        if options is None:
            options = {}

        processed_image = image.copy()
        
        # 灰度转换
        if options.get('gray', False):
            processed_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)

        # 模糊处理
        if options.get('blur', False):
            blur_kernel_size = options.get('blur_kernel', (5, 5))  # 可以动态调整模糊核大小
            processed_image = cv2.GaussianBlur(processed_image, blur_kernel_size, 0)

        # 直方图均衡（仅在灰度图像上执行）
        if options.get('equalize', False) and len(processed_image.shape) == 2:
            processed_image = cv2.equalizeHist(processed_image)
        
        # 二值化处理
        if options.get("threshold", False):
            # 如果图像未灰度化，则先灰度化
            if len(processed_image.shape) == 3:  # 如果是彩色图像
                processed_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)
            # 动态阈值设定
            threshold_value = options.get("threshold_value", 150)
            max_value = options.get("max_value", 255)
            _, processed_image = cv2.threshold(processed_image, threshold_value, max_value, cv2.THRESH_BINARY)
        return processed_image

    def find_template_locations(self, screen: np.ndarray, template: np.ndarray, threshold: float = 0.8) -> List[Tuple[int, int]]:
        """
        在屏幕图像中查找模板图像，返回所有匹配的位置。
        
        :param screen: 当前屏幕的图像（numpy 数组格式）。
        :param template: 模板图像的 numpy 数组。
        :return: 所有找到的模板中心坐标 (x, y) 列表。
        """
        screen_resized = cv2.resize(screen, None, fx=self.scale_factor, fy=self.scale_factor, interpolation=cv2.INTER_LINEAR)
        result = cv2.matchTemplate(screen_resized, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val < threshold:
            raise RuntimeError(f"匹配失败，当前阈值 {max_val} 未达到定义阈值 {threshold}")

        template_matches = []
        y_coords, x_coords = np.where(result >= threshold)
        template_height, template_width = template.shape[:2]
        for x, y in zip(x_coords, y_coords):
            center_x = int((x + template.shape[1] // 2) / self.scale_factor)
            center_y = int((y + template.shape[0] // 2) / self.scale_factor)
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
        根据上下文条件查找图像中的所有匹配位置。

        参数:
            screen (np.ndarray): 要搜索的屏幕图像。
            template (np.ndarray): 要匹配的目标图像模板。
            contexts (List[dict]): 包含上下文模板及其相关信息的字典列表。
            all_matching (bool): 如果为 True，则要求所有上下文匹配。

        返回:
            Union[dict, None]: 如果找到匹配，则返回包含匹配信息的字典；否则返回 None。
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
        根据上下文图像过滤匹配，并返回详细的匹配信息。

        参数:
            screen (np.ndarray): 要搜索的屏幕图像。
            match (Tuple[int, int]): 目标图像的匹配位置坐标 (x, y)。
            contexts (List[dict]): 包含上下文模板及其相关信息的字典列表。
            all_matching (bool): 如果为 True，则要求所有上下文匹配。

        返回:
            Union[dict, None]: 如果找到符合上下文条件的匹配，则返回包含匹配信息的字典；否则返回 None。
        """
        context_matches = []
        successful_matches = set()
        for idx, context in enumerate(contexts):
            template_path = context.get("template")
            offset = context.get("offset", {"x": 0, "y": 0})
            threshold = context.get("threshold", self.threshold)
            context_template_ndarray = self.load_image_file(template_path)
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

        #     context_template_ndarray = self.load_image_file(template_path)
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
    def load_image_file(template_path: str) -> np.ndarray:
        """
        加载模板并处理可能的异常。
        """
        try:
            context_template_ndarray = cv2.imread(template_path)
            return context_template_ndarray
        except Exception:
            raise ValueError(f"Could not read template: {template_path}")

    @staticmethod
    def calculate_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """
        计算两个位置之间的欧几里得距离。
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
        判断两张图片是否重合，通过相似度阈值判断
        :param screenshot_before: 第一张截图
        :param screenshot_after: 第二张截图
        :param options: 处理图片时的选项，包含处理流程的配置
        :param threshold: 相似度阈值，默认为0.9
        :return: 如果两张图片不同返回 True，否则返回 False
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
    def draw_match(image: np.ndarray, match: dict, color: Tuple[int, int, int] = (0, 255, 0), thickness: int = 2) -> np.ndarray:
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

    @staticmethod
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
            image_copy = ImageMatcher.draw_match(image_copy, match, color=color, thickness=thickness)
        return image_copy
    
    @staticmethod
    def filter_nearby_matches(matches: List[dict], min_distance: float = 10) -> List[dict]:
        """
        过滤掉相邻的重复匹配点，仅保留每组相邻点中的一个。
        
        :param matches: 初始的匹配点列表，每个匹配点包含'position'字段。
        :param min_distance: 两个匹配点之间的最小距离。低于该距离的匹配点会被视为重复。
        :return: 过滤后的匹配点列表。
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