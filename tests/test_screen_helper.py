#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import time
import os
import glob
import sys
import uuid
from typing import Tuple, Dict, Optional

import numpy as np
from core.logger import LoggerController
from core.screen_capture import ScreenCapture
from core.image_matcher import ImageMatcher
from core.mouse_controller import MouseController
from core.keyboard_controller import KeyboardController, ClipboardHandler
from core.text_recognizer import TextRecognizer
from core.config import BaseConfig
from core.result import Result
from core.screen_helper import ScreenHelper
from core.utils import load_image_file

class Execute:
    def __init__(self, scale_factor: float = None, threshold: float = None, debug: bool = False):
        """
        初始化自动化类，用于处理屏幕自动化操作。
        :param scale_factor: 图像缩放因子，控制待匹配图像的大小
        :param threshold: 匹配的阈值，决定图像匹配的灵敏度
        :param debug: 是否启用调试模式，启用时将显示详细的日志信息
        """
        # 使用 BaseConfig 的默认值，但允许通过构造函数覆盖
        self.scale_factor = scale_factor if scale_factor is not None else BaseConfig.scale_factor
        self.threshold = threshold if threshold is not None else BaseConfig.threshold
        self.debug = debug
        
        # 初始化其他组件
        LoggerController.setup_logger("ScreenHelper", debug=self.debug)  # 日志记录器
        self.screen_helper = ScreenHelper()
        self.screen_capture = ScreenCapture()  # 捕获屏幕截图的实例
        self.image_matcher = ImageMatcher(self.scale_factor, self.threshold)  # 图像匹配器实例
        self.mouse = MouseController()  # 控制鼠标的实例
        self.keyboard = KeyboardController()  # 控制键盘的实例
        self.clipboard = ClipboardHandler()  # 管理剪贴板的实例
        self.text_recognizer = TextRecognizer()  # 文本识别器实例
        self.clipboard_contents: Dict[str, str] = {}  # 存储剪贴板内容的字典
        
        # 初始化
        self.current_coordinates = None
        self.screen_helper.add_action_method(
            {
            'screenshot': self._take_screenshot,
            'find_image': self._find_image,
            'find_text': self._find_text,
            'mouse': self._mouse,
            'send_text': self._type_text,
            'send_hotkey': self._send_hotkey,
            'delay': self._delay,
            'file_management': self._file_manage,
            'exit': self._exit,
        })
    
    def _take_screenshot(self, **params):
        """
        执行截图操作并保存到指定路径。
        :param file_path: 保存截图的文件路径
        :param region: 可选，指定截取的区域 (格式为: (left, top, right, bottom))
        """
        screenshot_file = params.get("screenshot_file")
        region = params.get("region")
        try:
            screenshot = self.screen_capture.capture(region)  # 捕获当前屏幕截图或指定区域
            self.screen_capture.save_screenshot(screenshot, screenshot_file)  # 保存截图
            return Result(success=True, data=screenshot_file)  # 返回成功结果
        except Exception as e:
            return Result(success=False, error=str(e))
    
    # TODO: 匹配多个问题未解决
    def _find_image(self, **params):
        """
        查找并点击模板图像在屏幕上的位置。

        :param src_image: 源图像文件路径，用于捕获当前屏幕内容。
        :param target_image: 目标模板图像文件路径，需要在屏幕上查找的图像。
        :param target_context_image: 可选的上下文图像文件路径，用于进一步过滤匹配结果。
        :param context_threshold: 可选的上下文匹配阈值，默认为类的 threshold 属性。
        :param context_area_size: 可选的上下文区域大小，用于过滤匹配，默认为 30 像素。

        :return: 返回找到的第一个匹配位置的坐标 (x, y)。

        :raises RuntimeError: 如果未能找到目标图像，则抛出异常。
        """
        src_image = params.get("src_image")
        target_image = params.get("target_image")
        target_context_image = params.get("target_context_image")
        preprocess_options = params.get("preprocess_options", {})
        screen = load_image_file(src_image)
        target_template = load_image_file(target_image)
        if preprocess_options:
            screen = self.image_matcher.preprocess_input_image(screen, preprocess_options)
            target_template = self.image_matcher.preprocess_input_image(target_template, preprocess_options)
        if target_context_image:
            _target_context = load_image_file(target_context_image)
            matches = self.image_matcher.find_template_with_contexts(
                screen,
                target_template,
                _target_context,
            )
        else:
            matches = self.image_matcher.find_template_locations(screen, target_template)  # 查找模板图像
        if matches:
            self.current_coordinates = matches[0]['position']  if isinstance(matches, list) else matches['position']
            return Result(success=True, data=self.current_coordinates)
        else:
            return Result(success=False, error=f"The target image {target_image} has not been found in {src_image}")
    
    def _mouse(self, **params):
        """
        执行鼠标操作，包括移动、点击和滚动。
        :param operation: 要执行的鼠标操作类型，可能的值有 "move"、"move_with_offset"、"click"、"scroll"。
        :param position: 要移动到的坐标 (x, y)，仅在 operation 为 "move" 或 "move_with_offset" 时使用。
        :param offset: 偏移量，包含两个值 (offset_x, offset_y)，仅在 operation 为 "move_with_offset" 时使用。
        :param mouse_click_action: 点击动作类型，可以是 "left"、"right" 或 "double"，仅在 operation 为 "click" 时使用。
        :param delta: 滚动距离，正值表示向上滚动，负值表示向下滚动，仅在 operation 为 "scroll" 时使用。
        """
        operation = params.get("operation")
        position = params.get("position", self.current_coordinates) 
        offset = params.get("offset")
        mouse_click_action = params.get("mouse_click_action")
        delta = params.get("delta", 0)
        if operation == "move":
            self.mouse.move_cursor(position[0], position[1])
        elif operation == "move_with_offset":
            self.mouse.move_cursor_with_offset(position[0], position[1], offset[0], offset[1])
        elif operation == "click":
            self.mouse.click_at(position[0], position[1], mouse_click_action)
        elif operation == "scroll":
            self.mouse.scroll(delta)
        else:
            return Result(success = False, error = f"Unknown mouse action: {operation}")
        self.current_coordinates = tuple(self.mouse.get_cursor_position())
        return Result(success = True)

    def _type_text(self, **params):
        """
        文本输入
        :param text: 要输入的文本内容
        """
        text = params.get("text")
        try:
            self.keyboard.type_text(text)
        except Exception as e:
            return Result(success=False, error=str(e))

    def _send_hotkey(self, **params):
        """
        快捷键输入
        :param hot_keys: 快捷键内容
        :param identifier: 快捷键标识
        :return: 执行结果
        """
        hot_keys = tuple(key.lower() for key in params.get("hot_keys", []))
        execute_identifier = params.get("execute_identifier")
        try:
            result_type = "clipboard" if hot_keys in (("ctrl", "v"), ("ctrl", "c")) else "none"
            result = self.keyboard.perform_hotkey_action(*hot_keys, result_type=result_type)
            time.sleep(0.3)
            if hot_keys == ("ctrl", "x"):
                result = self.clipboard.get_text()
        except Exception as e:
            return Result(success=False, error=str(e))
        if execute_identifier and result is not None:
            self.screen_helper._add_processed_action_result(execute_id = execute_identifier, result = {"result": {"hotkey_result": result}})
        return Result(success=True)

    def _delay(self, **params): 
        """
        延迟
        :param duration: 要延迟多少秒
        """
        duration = params.get("duration", 1)
        time.sleep(duration)
        return Result(success=True)

    def _file_manage(self, **params):
        pass

    # TODO: 识别效果不是很理想
    def _find_text(self, **params):
        """
        查找并点击图像中指定的文本。
        
        :param src_image: 源图片
        :param target_text: 要查找的文本
        :param target_context_text: 上下文文本
        :param threshold: 允许的偏移阈值
        :param lang: OCR 语言代码，默认为英语
        :param custom_config: 自定义配置，用于 Tesseract OCR
        """
        src_image = params.get("src_image")
        text = params.get("target_text")
        context_text = params.get("target_context_text")
        threshold = params.get("threshold")
        preprocess_options = params.get("preprocess_options", {})
        lang = params.get("lang", 'chi_sim+eng')  # 默认为中文和英语
        custom_config = params.get("custom_config")  # 自定义配置
        screen = load_image_file(src_image)
        if preprocess_options:
            screen = self.image_matcher.preprocess_input_image(screen, preprocess_options)
        if context_text:
            positions = self.text_recognizer.find_text_position(screen, text, lang, custom_config, context_text, threshold)
        else:
            positions = self.text_recognizer.find_all_text_positions(screen, text, lang, custom_config)
        if positions:
            self.current_coordinates = positions[0]['position']  # 假设你只关心第一个匹配的位置
        else:
            return Result(success=False, error=f"The text {text} has not been found in {src_image}")
        return Result(success=True, data=self.current_coordinates)

    def _exit(self):
        """
        退出程序
        """
        sys.exit(0)
    
    def can_scroll_down(self, **params) -> bool:
        """
        判断当前页面是否可以继续向下滚动。
        
        :param tolerance: 用于比较滚动前后截图的相似度阈值（范围 0 到 1），默认为 0.95。
        :return: 如果可以滚动返回 True，否则返回 False。
        """
        tolerance = params.get("tolerance", 0.95)
        screenshot_before = self.screen_capture.capture()
        self.mouse.scroll()  # 执行向下滚动
        time.sleep(1)  # 等待滚动完成
        screenshot_after = self.screen_capture.capture()
        similarity = self.image_matcher.compare_images(screenshot_before, screenshot_after)
        return similarity < tolerance