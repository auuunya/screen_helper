#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   main.py
@Desc    :   None
'''

# here put the import lib
import uuid
from typing import List, Dict, Any, Callable

class ScreenHelper:
    # 定义为类属性
    action_method_mapping: Dict[str, Callable[..., Any]] = {}
    debug: bool = False
     
    def __init__(self):
        """
        初始化自动化类，用于处理屏幕自动化操作。
        :param scale_factor: 图像缩放因子，控制待匹配图像的大小
        :param threshold: 匹配的阈值，决定图像匹配的灵敏度
        :param debug: 是否启用调试模式，启用时将显示详细的日志信息
        """
        self.processed_actions: Dict[str, Dict[str, Any]] = {}
        self.pending_actions: List[Dict[str, Any]] = []
    
    @classmethod
    def add_action_method(cls, action_type, method=None):
        """
        动态添加新操作类型及其对应的方法。支持单个添加和批量添加。

        :param action_type: 操作类型的字符串，或 {操作类型: 方法} 的字典
        :param method: 需要添加的单个方法，应该接受预期的参数并返回有效结果
        :raises ValueError: 如果 action_type 已经存在于映射表中，抛出异常
        :raises TypeError: 如果传入的方法不符合预期接口，抛出异常
        """
        # 如果传入的是字典类型，则批量添加
        if isinstance(action_type, dict):
            for act_type, meth in action_type.items():
                cls._add_single_action_method(act_type, meth)
        # 如果传入的是单个方法
        else:
            cls._add_single_action_method(action_type, method)

    @classmethod
    def _add_single_action_method(cls, action_type, method):
        if not callable(method):
            raise TypeError(f"The method for action type '{action_type}' must be callable.")
        if action_type in cls.action_method_mapping:
            raise ValueError(f"Action type '{action_type}' is already in the action method mapping.")
        cls.action_method_mapping[action_type] = method


    def generate_execute_id(self):
        """
        生成一个唯一的执行标识符。

        :return: 返回一个随机生成的 UUID 字符串。
        """
        return str(uuid.uuid4())

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
        
    def _execute_action(self, action_type_text: str, options: Dict[str, Any], execute_id: str) -> bool:
        """
        执行指定的操作并记录结果。

        :param action_type_text: 操作的类型
        :param options: 传递给操作的方法参数
        :param execute_id: 当前操作的执行标识符
        """
        method = self.action_method_mapping.get(action_type_text)
        if not method:
            raise ValueError(f"Unknown action type: {action_type_text}")
        if not isinstance(options, dict):
            raise TypeError(f"Options for action '{action_type_text}' should be a dictionary, but got {type(options).__name__}")
        
        try:
            result = method(**options)
            self._add_processed_action_result(
                execute_id=execute_id,
                result={
                    "status": "success",
                    "action": {"action_type_text": action_type_text, "options": options},
                    "result": result
                }
            )
            return True
        except Exception as e:
            error_message = str(e)
            if self.debug:
                raise RuntimeError(f"Error executing action '{action_type_text}': {error_message}")
            return error_message

    def run_single_action(self, action: Dict[str, Any]) -> bool:
        """
        执行单个操作。

        :param action: 包含操作类型和参数的字典
        :return: 执行结果，包含状态和执行标识符
        """
        action_type_text = action.get("action_type_text")
        options = action.get("options", {})
        execute_id = options.get("execution_id", self.generate_execute_id())
        return self._execute_action(action_type_text, options, execute_id)

    def run_action_queue(self, actions: List[Dict[str, Any]], max_retries: int = 3):
        """
        执行操作队列中的所有操作。

        :param actions: 包含多个操作的字典列表
        :param max_retries: 最大重试次数
        :return: 执行结果，包含最终状态和错误信息（如果有的话）
        """
        self.pending_actions = actions.copy()
        retry_counts = {action['action_type_text']: 0 for action in actions}

        while self.pending_actions:
            action = self.pending_actions.pop(0)
            action_type_text = action.get("action_type_text")
            options = action.get("options", {})
            execute_id = options.get("execution_id", self.generate_execute_id())

            success = False
            for attempt in range(max_retries):
                result = self._execute_action(action_type_text, options, execute_id)
                if result is True:
                    success = True
                    retry_counts[action_type_text] = 0
                    break
                else:
                    retry_counts[action_type_text] += 1
                    action["error"] = result

            if not success:
                self.pending_actions.insert(0, action)
                break

        return {
            "processed_actions": self.processed_actions,
            "pending_actions": self.pending_actions
        }