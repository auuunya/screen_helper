#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   main.py
@Time    :   2024/10/23 15:39:34
@Author  :   auuu_nya 
@Desc    :   None
'''

# here put the import lib
import time
import os
import glob
import sys
import uuid
from typing import List, Tuple, Dict, Any, Optional

import numpy as np
from options.logger import LoggerController
from options.screen_capture import ScreenCapture
from options.image_matcher import ImageMatcher
from options.mouse_controller import MouseController
from options.keyboard_controller import KeyboardController
from options.clipboard_manager import ClipboardManager
from options.text_recognizer import TextRecognizer
from options.config import BaseConfig
from options.result import Result

class ScreenHelper:
    # 定义为类属性
    action_method_mapping = {}
    debug = False
     
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
        self.screen_capture = ScreenCapture()  # 捕获屏幕截图的实例
        self.image_matcher = ImageMatcher(self.scale_factor, self.threshold)  # 图像匹配器实例
        self.mouse = MouseController()  # 控制鼠标的实例
        self.keyboard = KeyboardController()  # 控制键盘的实例
        self.clipboard = ClipboardManager()  # 管理剪贴板的实例
        self.text_recognizer = TextRecognizer()  # 文本识别器实例
        self.clipboard_contents: Dict[str, str] = {}  # 存储剪贴板内容的字典
        
        # storage manager
        self.current_coordinates: Optional[Tuple[int, int]] = None
        self.processed_actions: Dict[str, Dict[str, Any]] = {}
        self.pending_actions: List[Dict[str, Any]] = []

        # 初始化方法映射表
        self.action_method_mapping = {
            'screenshot': self._take_screenshot,
            'find_image': self._find_image,
            'find_text': self._find_text,
            'mouse': self._mouse,
            'send_text': self._type_text,
            'send_hotkey': self._send_hotkey,
            'delay': self._delay,
            'file_management': self._file_manage,
            'exit': self._exit,
        }
    
    @classmethod
    def add_action_method(cls, action_type: str, method):
        """
        动态添加新操作类型及其对应的方法。

        :param action_type: 操作类型的字符串
        :param method: 需要添加的方法，应该接受预期的参数并返回有效结果
        :raises ValueError: 如果 action_type 已经存在于映射表中，抛出异常
        :raises TypeError: 如果传入的方法不符合预期接口，抛出异常
        
        示例:
            def custom_method(self, param1, param2):
                import numpy as np  # 在方法内部引入包
                result = np.array([param1, param2])
                return result
        """
        # 检查方法是否为可调用对象
        if not callable(method):
            raise TypeError(f"The method for action type '{action_type}' must be callable.")
        
        cls.action_method_mapping[action_type] = method

   
    @classmethod
    def enable_debug(cls):
        """
        启用调试模式，将 `ScreenHelper` 的调试标志设置为 True。
        """
        cls.debug = True
    @classmethod
    def disable_debug(cls):
        """
        禁用调试模式，将 `ScreenHelper` 的调试标志设置为 False。
        """
        cls.debug = False

    def generate_execute_id(self):
        """
        生成一个唯一的执行标识符。

        :return: 返回一个随机生成的 UUID 字符串。
        """
        return str(uuid.uuid4())

    def create_screenshot_directory(self, dirs):
        """
        创建截图保存目录
        :params dirs: 传入目录
        """
        try:
            if os.path.exists(dirs):
                # 删除文件夹内所有文件
                for file in glob.glob(os.path.join(dirs, "*")):
                    try:
                        os.remove(file)
                    except Exception as e:
                        pass
            else:
                os.makedirs(dirs)
        except Exception as e:
            raise ValueError(f"生成截图目录出错: {str(e)}")

    def _add_processed_action_result(self, execute_id: str, result: Dict[str, Any]):
        """
        向 `processed_actions` 添加或更新执行结果。

        :param execute_id: 执行标识符
        :param result: 需要添加的执行结果，格式为字典
        """
        self.processed_actions.setdefault(execute_id, {}).update(result)
        
    def _add_value_to_processed_action(self, execute_id: str, key: str, value: Any):
        """
        向 `processed_actions` 中的指定键添加值。如果该键已存在并且是字典，将进行更新。

        :param execute_id: 执行标识符
        :param key: 要更新的键
        :param value: 要添加的值
        :raises KeyError: 如果 `execute_id` 不存在，抛出异常
        """
        if execute_id in self.processed_actions:
            entry = self.processed_actions[execute_id]
            if key in entry:
                if isinstance(entry[key], dict) and isinstance(value, dict):
                    entry[key].update(value) 
                else:
                    entry[key] = value 
            else:
                entry[key] = value
        else:
            raise KeyError(f"execute '{execute_id}' not found in processed actions")
        
    def get_execute_result(self, execute_id: str, key: str = None):
        """
        获取执行结果。如果指定了 key，则返回相应的嵌套值。

        :param execute_id: 执行标识符
        :param key: 可选参数，指定要获取的结果键，支持嵌套访问，用 `.` 分隔
        :return: 返回指定键的值，或者整个执行结果条目
        :raises KeyError: 如果 `execute_id` 或者指定的键不存在，抛出异常
        """
        if execute_id in self.processed_actions:
            entry = self.processed_actions[execute_id]
            if key:
                keys = key.split('.')
                value = entry
                for k in keys:
                    if isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        raise KeyError(f"execute '{execute_id}' not find '{key}'")
                return value
            return entry
        raise KeyError(f"execute '{execute_id}' not found in processed actions")
        
    def set_scale_factor(self, scale_factor: float):
        """
        设置图像缩放因子，并更新 BaseConfig。
        :param scale_factor: 新的图像缩放因子
        """
        self.scale_factor = scale_factor
        BaseConfig.scale_factor = scale_factor
        self.image_matcher.scale_factor = scale_factor

    def set_threshold(self, threshold: float):
        """
        设置匹配的阈值，并更新 BaseConfig。
        :param threshold: 新的匹配阈值
        """
        self.threshold = threshold
        BaseConfig.threshold = threshold
        self.image_matcher.threshold = threshold

    def _execute_action(self, action_type: str, params: Dict[str, Any], execute_id: str):
        """
        执行指定的操作并记录结果。

        :param action_type: 操作的类型
        :param params: 传递给操作的方法参数
        :param execute_id: 当前操作的执行标识符
        """
        method = self.action_method_mapping.get(action_type)
        if not method:
            raise ValueError(f"Unknown action type: {action_type}")
        method(**params)
        self._add_processed_action_result(
            execute_id=execute_id,
            result={"action": {"type": action_type, "params": params}, "coordinates": self.current_coordinates}
        )

    def run_single_action(self, action: Dict[str, Any]) -> Result:
        """
        执行单个操作。

        :param action: 包含操作类型和参数的字典
        :return: 执行结果，包含状态和执行标识符
        """
        action_type = action['type']
        params = action.get('params', {})
        execute_id = params.get("execute_identifier", self.generate_execute_id())

        try:
            self._execute_action(action_type, params, execute_id)
        except Exception as e:
            return Result(success=False, error=str(e))
        return Result(success=True)

    def run_action_queue(self, actions: List[Dict[str, Any]]):
        """
        执行操作队列中的所有操作。

        :param actions: 包含多个操作的字典列表
        :return: 执行结果，包含最终状态和错误信息（如果有的话）
        """
        self.pending_actions = actions.copy()
        while self.pending_actions:
            action = self.pending_actions.pop(0)
            action_type = action['type']
            params = action.get('params', {})
            execute_id = params.get("execute_identifier", self.generate_execute_id())

            LoggerController.log_info(
                f"""
        ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        action_type= '{action_type}'
        action_params= '{params}'
        ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                """
            )

            self.processed_actions.setdefault(execute_id, {})

            try:
                self._execute_action(action_type, params, execute_id)
            except Exception as e:
                self.pending_actions.insert(0, action)
                return Result(success=False, error=str(e))
        return Result(success=True)

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
        context_threshold = params.get("context_threshold", self.threshold)
        context_area_size = params.get("context_area_size", 30)
        preprocess_options = params.get("preprocess_options", {})
        screen = self.screen_capture.load_image_file(src_image)
        target_template = self.screen_capture.load_image_file(target_image)
        if preprocess_options:
            screen = self.image_matcher.preprocess_image(screen, preprocess_options)
            target_template = self.image_matcher.preprocess_image(target_template, preprocess_options)
        matches = self.image_matcher.find_images(screen, target_template)  # 查找模板图像
        if target_context_image:
            _target_context = self.screen_capture.load_image_file(target_context_image)
            filter_matches = self.image_matcher.filter_matches_by_context(
                screen,
                matches,
                _target_context,
                context_threshold or self.threshold,
                context_area_size
            )
        if matches:
            self.current_coordinates = matches[0]  # 假设你只关心第一个匹配的位置
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
            self.mouse.move_to(position[0], position[1])
        elif operation == "move_with_offset":
            self.mouse.move_to_with_offset(position[0], position[1], offset[0], offset[1])
        elif operation == "click":
            self.mouse.click(position[0], position[1], mouse_click_action)
        elif operation == "scroll":
            self.mouse.scroll(delta)
        else:
            return Result(success = False, error = f"Unknown mouse action: {operation}")
        self.current_coordinates = tuple(self.mouse.get_current_position())
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
            result = self.keyboard.send_hotkey(*hot_keys)
            time.sleep(0.3)
            if hot_keys == ("ctrl", "c"):
                result = self.clipboard.get_content()
            elif hot_keys == ("ctrl", "x"):
                result = self.clipboard.get_content()
            elif hot_keys == ("ctrl", "v"):
                result = self.clipboard.get_content()
            else:
                result = None
        except Exception as e:
            return Result(success=False, error=str(e))
        if execute_identifier and result is not None:
            self._add_processed_action_result(execute_id = execute_identifier, result = {"result": {"hotkey_result": result}})
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
        screen = self.screen_capture.load_image_file(src_image)
        if preprocess_options:
            screen = self.image_matcher.preprocess_image(screen, preprocess_options)
        if context_text:
            positions = self.text_recognizer.find_text_position(screen, text, lang, custom_config, context_text, threshold)
        else:
            positions = self.text_recognizer.find_text_position(screen, text, lang, custom_config)
        if positions:
            self.current_coordinates = positions[0]  # 假设你只关心第一个匹配的位置
        else:
            return Result(success=False, error=f"The text {text} has not been found in {src_image}")
        return Result(success=True, data=self.current_coordinates)

    def _exit(self):
        """
        退出程序
        """
        sys.exit(0)
    
    def can_scroll_down(self):
        """
        查看是否可滚动
        TODO: 未完成
        """
        screenshot_before = self.screen_capture.capture()
        self.scroll_down()
        time.sleep(1)
        screenshot_after = self.screen_capture.capture()
        return not np.array_equal(np.array(screenshot_before), np.array(screenshot_after))
