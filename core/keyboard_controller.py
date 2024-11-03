import pyautogui
import pyperclip
from typing import Optional, Literal

class KeyboardController:
    @staticmethod
    def enter_text(text: str, delay: float = 0.05):
        """
        输入给定的文本
        :param text: 要输入的文本内容
        :param delay: 每个字符之间的输入延迟（秒）
        """
        pyautogui.typewrite(text, interval=delay)

    @staticmethod
    def perform_hotkey_action(
        *keys, 
        result_type: Literal["clipboard", "none"] = "none"
    ) -> Optional[str]:
        """
        执行快捷键组合，并返回指定类型的结果。
        :param keys: 要执行的快捷键组合
        :param result_type: 指定要返回的结果类型，"clipboard" 表示返回剪贴板内容，"none" 表示不返回任何内容
        :return: 如果 `result_type` 为 "clipboard"，返回剪贴板内容；否则返回 None
        """
        pyautogui.hotkey(*keys)
        
        if result_type == "clipboard":
            pyautogui.sleep(0.1)  # 等待剪贴板更新
            return ClipboardHandler.get_text()
        return None

class ClipboardHandler:
    @staticmethod
    def get_text() -> str:
        """
        获取当前剪贴板的文本内容
        :return: 剪贴板中的文本内容
        """
        try:
            return pyperclip.paste()
        except Exception as e:
            return ""

    @staticmethod
    def set_text(text: str):
        """
        设置指定文本到剪贴板
        :param text: 要复制到剪贴板的文本内容
        """
        try:
            pyperclip.copy(text)
        except Exception as e:
            raise ValueError(f"无法复制到剪贴板: {str(e)}")