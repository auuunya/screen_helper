#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   image_matcher.py
@Time    :   2024/10/23 15:34:50
@Author  :   auuu_nya 
@Desc    :   None
'''

# here put the import lib
import cv2
import numpy as np
from typing import List, Tuple, Dict, Any

class ImageMatcher:

    def __init__(self, scale_factor: float = 1, threshold: float = 0.8):
        """
        初始化图像匹配器
        :param scale_factor: 图像缩放因子，用于调整待匹配图像的大小
        :param threshold: 匹配的阈值，控制匹配的灵敏度
        """
        self.scale_factor = scale_factor
        self.threshold = threshold

    def preprocess_image(self, image: np.ndarray, options: Dict[str, Any] = None) -> np.ndarray:
        """
        动态预处理图像，根据提供的选项调整预处理流程（灰度、模糊、直方图均衡、二值化）
        
        :param image: 输入的图像（numpy 数组格式）
        :param options: 预处理选项，可以控制是否进行灰度转换、模糊处理、直方图均衡、二值化等
        :return: 预处理后的图像
        """
        if options is None:
            options = {}

        processed_image = image
        
        # 灰度转换
        if options.get('gray', False):
            processed_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)

        # 模糊处理
        if options.get('blur', False):
            blur_kernel_size = options.get('blur_kernel', (5, 5))  # 可以动态调整模糊核大小
            processed_image = cv2.GaussianBlur(processed_image, blur_kernel_size, 0)

        # 直方图均衡（仅在灰度图像上执行）
        if options.get('equalize', False):
            if len(processed_image.shape) == 2:  # 确保是灰度图像
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

    def find_images(self, screen: np.ndarray, template: np.ndarray) -> List[Tuple[int, int]]:
        """
        在给定的屏幕图像中查找模板图像，返回所有匹配的位置
        :param screen: 当前屏幕的图像（numpy 数组格式）
        :param template_path: 模板图像的文件路径
        :return: 所有找到的模板中心的坐标 (x, y) 列表
        """
        # template = cv2.imread(template_path)
        # if template is None:
        #     raise FileNotFoundError(f"Template image not found: {template_path}")
        screen_resized = cv2.resize(screen, None, fx=self.scale_factor, fy=self.scale_factor, interpolation=cv2.INTER_LINEAR)
        result = cv2.matchTemplate(screen_resized, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        logging.info(f"match result min_val: {min_val}, max_val: {max_val}, min_loc: {min_loc}, max_loc: {max_loc}")
        if max_val < self.threshold:
            raise RuntimeError(f"匹配失败，当前阈值 {max_val} 未达到定义阈值 {self.threshold}")
        # 获取所有匹配的坐标
        matched_centers = []
        y_coords, x_coords = np.where(result >= self.threshold)

        for (x, y) in zip(x_coords, y_coords):
            center_x = x // self.scale_factor + template.shape[1] // (2 * self.scale_factor)
            center_y = y // self.scale_factor + template.shape[0] // (2 * self.scale_factor)

            matched_centers.append((center_x, center_y))
        return matched_centers

    def filter_matches_by_context(self, screen: np.ndarray, matches: List[Tuple[int, int]], context: np.ndarray, context_threshold: float = 0.8, context_area_size: int = 30) -> List[Tuple[int, int]]:
        """
        根据上下文图像过滤匹配
        :param screen: 当前屏幕的图像
        :param matches: 之前找到的所有匹配位置
        :param context: 上下文图像
        :param context_threshold: 上下文匹配的阈值
        :param context_area_size: 匹配区域的大小
        :return: 经过上下文过滤后的匹配位置列表
        """
        if context is None:
            return matches
        
        filtered_matches = []
        for match in matches:
            x, y = match
            # 在匹配位置提取上下文区域，使用外部传入的上下文区域大小
            context_area = screen[y - context_area_size:y + context_area_size, x - context_area_size:x + context_area_size]
            if self.context_matches(context_area, context, context_threshold):
                filtered_matches.append(match)
        return filtered_matches

    def context_matches(self, area: np.ndarray, context: np.ndarray, threshold: float) -> bool:
        """
        检查上下文区域是否与给定的上下文匹配
        :param area: 匹配区域
        :param context: 上下文图像
        :param threshold: 匹配阈值
        :return: 如果匹配则返回 True，否则返回 False
        """
        result = cv2.matchTemplate(area, context, cv2.TM_CCOEFF_NORMED)
        max_val = np.max(result)
        return max_val >= threshold