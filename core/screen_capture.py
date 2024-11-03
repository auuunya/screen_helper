from typing import Tuple, Optional
import os
import glob

import numpy as np
import mss
import cv2

class ScreenCapture:
    def __init__(self):
        """
        初始化屏幕捕获类，创建 mss.mss 实例以进行屏幕截图
        """
        self.sct = mss.mss()

    def create_directory(self, dirs):
        """
        创建截图保存目录
        :params dirs: 传入目录
        """
        try:
            if os.path.exists(dirs):
                for file in glob.glob(os.path.join(dirs, "*")):
                    try:
                        os.remove(file)
                    except OSError as e:
                        print(f"Error deleting file {file}: {e}")
            else:
                os.makedirs(dirs)
        except OSError as e:
            raise ValueError(f"生成截图目录出错: {str(e)}")

    def capture(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """
        捕获当前屏幕截图
        :param region: 可选，指定截取的区域 (格式为: (left, top, right, bottom))
        :return: 截取的屏幕图像，以 numpy 数组格式返回
        """
        if region:
            monitor = {
                "top": region[1],
                "left": region[0],
                "width": region[2] - region[0],
                "height": region[3] - region[1]
            }
        else:
            monitor = self.sct.monitors[1]
        screenshot = self.sct.grab(monitor)
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)
    
    def record_screen_snapshot(self, screenshot: np.ndarray, screenshot_file: Optional[str] = "screenshot.png"):
        """
        保存当前屏幕截图到指定路径
        :param screenshot: 要保存的屏幕截图 (numpy 数组格式)
        :param file_path: 截图保存路径 (包含文件名及扩展名)，默认为 "screenshot.png"
        """
        try:
            cv2.imwrite(screenshot_file, screenshot)
        except cv2.error as e:
            raise ValueError(f"截屏保存出错: {str(e)}")
