#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   screen_capture.py
@Time    :   2024/10/23 15:33:28
@Author  :   auuu_nya 
@Desc    :   None
'''

# here put the import lib
from typing import Tuple, Optional

import numpy as np
import mss
import cv2

class ScreenCapture:
    def __init__(self):
        """
        初始化屏幕捕获类，创建 mss.mss 实例以进行屏幕截图
        """
        self.sct = mss.mss()

    def capture(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """
        捕获当前屏幕截图
        :param region: 可选，指定截取的区域 (格式为: (left, top, right, bottom))
        :return: 截取的屏幕图像，以 numpy 数组格式返回
        """
        if region:
            {"top": region[1], "left": region[0], "width": region[2]-region[0], "height": region[3]-region[1]}
        else:
            monitor = self.sct.monitors[1]
        screenshot = self.sct.grab(monitor)
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)
    
    def save_screenshot(self, screenshot: np.ndarray, screenshot_file: str = "screenshot.png"):
        """
        保存当前屏幕截图到指定路径
        :param screenshot: 要保存的屏幕截图 (numpy 数组格式)
        :param file_path: 截图保存路径 (包含文件名及扩展名)，默认为 "screenshot.png"
        """
        try:
            cv2.imwrite(screenshot_file, screenshot)
        except Exception as exce:
            raise (f"截屏保存出错: {str(exce)}")
    
    def load_image_file(self, image_file: Optional[str]) -> np.ndarray:
        """
        加载图像文件并返回图像的 NumPy 数组表示。
        
        :param image_file: 图像文件的路径，如果为 None 则抛出 FileNotFoundError 异常
        :return: 加载的图像，作为 NumPy 数组
        :raises FileNotFoundError: 如果图像路径为 None 或图像加载失败
        """
        if image_file is None:
            raise FileNotFoundError(f"Image not found: {image_file}")
        
        image = cv2.imread(image_file)
        if image is None:
            raise FileNotFoundError(f"Failed to load image: {image_file}")
        
        return image