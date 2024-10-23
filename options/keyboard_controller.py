#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   keyboard_controller.py
@Time    :   2024/10/23 15:36:29
@Author  :   auuu_nya 
@Desc    :   None
'''

# here put the import lib
import pyautogui

class KeyboardController:
    @staticmethod
    def type_text(text: str, interval: float = 0.05):
        """
        输入指定的文本
        :param text: 要输入的文本
        """
        pyautogui.typewrite(text, interval=0.05)

    @staticmethod
    def send_hotkey(*keys):
        """
        发送指定的快捷键
        :param keys: 要发送的快捷键
        """
        pyautogui.hotkey(*keys)