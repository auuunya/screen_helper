#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   mouse_controller.py
@Time    :   2024/10/23 15:35:48
@Author  :   auuu_nya 
@Desc    :   None
'''

# here put the import lib
from typing import Tuple
import pyautogui

class MouseController:
    @staticmethod
    def move_to(x: int, y: int, duration: float = 0.2):
        """
        移动鼠标到指定坐标
        :param x: 目标 x 坐标
        :param y: 目标 y 坐标
        :param duration: 移动持续时间（秒）
        """
        pyautogui.moveTo(x, y, duration=duration)
    
    @staticmethod
    def move_to_with_offset(x: int, y: int, offset_x: int = 0, offset_y: int = 0):
        """
        在指定坐标位置的基础上加上偏移量进行移动
        :param x: 点击的基础 x 坐标
        :param y: 点击的基础 y 坐标
        :param offset_x: x 坐标的偏移量
        :param offset_y: y 坐标的偏移量
        """
        target_x = x + offset_x
        target_y = y + offset_y
        MouseController.move_to(target_x, target_y)

    @staticmethod
    def click(x: int, y: int, action: str = "left"):
        """
        在指定坐标进行点击
        :param x: 点击的 x 坐标
        :param y: 点击的 y 坐标
        :param action: 点击动作，可以是 "left"、"right" 或 "double"
        """
        if action == "left":
            pyautogui.click(x, y)
        elif action == "right":
            pyautogui.rightClick(x, y)
        elif action == "double":
            pyautogui.doubleClick(x, y, interval=0.15)
        else:
            raise ValueError(f"未知的鼠标操作: {action}")

    @staticmethod
    def get_current_position() -> Tuple[int, int]:
        """
        获取当前鼠标位置
        :return: 当前鼠标的 x 和 y 坐标
        """
        return pyautogui.position()

    @staticmethod
    def scroll(delta: int):
        """
        滚动鼠标
        :param delta: 滚动的距离（正数向上滚动，负数向下滚动）
        """
        pyautogui.scroll(delta)
    @staticmethod
    def horizontal_scroll(delta: int):
        """
        横向滚动鼠标
        :param delta: 滚动的距离（正数向右滚动，负数向左滚动）
        """
        pyautogui.hscroll(delta)