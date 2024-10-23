#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   clipboard_manager.py
@Time    :   2024/10/23 15:36:52
@Author  :   auuu_nya 
@Desc    :   None
'''

# here put the import lib
import pyperclip

class ClipboardManager:
    @staticmethod
    def get_content() -> str:
        """
        获取当前剪贴板的内容
        :return: 剪贴板中的文本内容
        """
        try:
            return pyperclip.paste()
        except Exception as e:
            return ""

    @staticmethod
    def set_content(text: str):
        """
        将指定文本设置到剪贴板
        :param text: 需要复制到剪贴板的文本内容
        """
        try:
            pyperclip.copy(text)
        except Exception as e:
            raise ValueError(f"Could not copy {str(e)}")
