from .defs import ScreenHelperDefs
from typing import Tuple
import pyautogui

class MouseController:
    @staticmethod
    def move_cursor(x: int, y: int, duration: float = 0.2):
        """
        移动鼠标到指定坐标
        :param x: 目标 x 坐标
        :param y: 目标 y 坐标
        :param duration: 移动持续时间（秒）
        """
        pyautogui.moveTo(x, y, duration=duration)
    
    @staticmethod
    def move_cursor_with_offset(x: int, y: int, offset_x: int = 0, offset_y: int = 0):
        """
        在指定坐标位置的基础上加上偏移量进行移动
        :param x: 点击的基础 x 坐标
        :param y: 点击的基础 y 坐标
        :param offset_x: x 坐标的偏移量
        :param offset_y: y 坐标的偏移量
        """
        target_x = x + offset_x
        target_y = y + offset_y
        MouseController.move_cursor(target_x, target_y)

    @staticmethod
    def click_at(x: int, y: int, action: str = "left", interval: float = 0.15):
        """
        在指定坐标进行点击
        :param x: 点击的 x 坐标
        :param y: 点击的 y 坐标
        :param action: 点击动作，可以是 "left"、"right" 或 "double"
        """
        if action in [ScreenHelperDefs.LEFT, ScreenHelperDefs.RIGHT, ScreenHelperDefs.MIDDLE]:
            pyautogui.click(x, y, button=action)
        elif action == ScreenHelperDefs.DOUBLE:
            pyautogui.doubleClick(x, y, interval)
        else:
            raise ValueError(f"未知的鼠标操作: {action}")

    @staticmethod
    def get_cursor_position() -> Tuple[int, int]:
        """
        获取当前鼠标位置
        :return: 当前鼠标的 x 和 y 坐标
        """
        return pyautogui.position()

    @staticmethod
    def scroll(delta: int, direction: str):
        """
        滚动鼠标
        :param delta: 滚动的距离（正数向上滚动，负数向下滚动）
        :param direction: 滚动方向，可以是 "up", "down", "left", "right"
        """
        scroll_map = {
            ScreenHelperDefs.UP: delta,
            ScreenHelperDefs.DOWN: -delta,
            ScreenHelperDefs.LEFT: (-delta, True),
            ScreenHelperDefs.RIGHT: (delta, True),
        }
        
        if direction in scroll_map:
            if direction in [ScreenHelperDefs.LEFT, ScreenHelperDefs.RIGHT]:
                pyautogui.hscroll(scroll_map[direction][0])
            else:
                pyautogui.scroll(scroll_map[direction])
        else:
            raise ValueError(f"未知的滚动方向: {direction}")

    @staticmethod
    def drag_cursor(x: int, y: int, duration: float = 0.2, action: str = "left"):
        """
        拖动鼠标到指定坐标
        :param x: 目标 x 坐标
        :param y: 目标 y 坐标
        :param duration: 拖动持续时间（秒）
        :param button: 按下的按钮，默认为 "left" (支持 "left"、"right" 和 "middle")
        """
        if action in [ScreenHelperDefs.LEFT, ScreenHelperDefs.RIGHT, ScreenHelperDefs.MIDDLE]:
            pyautogui.dragTo(x, y, duration=duration, button=action)
        else:
            raise ValueError(f"未知的拖动按钮: {action}")

    @staticmethod
    def drag_cursor_with_offset(x: int, y: int, offset_x: int = 0, offset_y: int = 0, duration: float = 0.2, button: str = "left"):
        """
        从指定坐标基础上加上偏移量进行拖动
        :param x: 起始 x 坐标
        :param y: 起始 y 坐标
        :param offset_x: x 坐标的偏移量
        :param offset_y: y 坐标的偏移量
        :param duration: 拖动持续时间（秒）
        :param button: 按下的按钮，默认为 "left" (支持 "left"、"right" 和 "middle")
        """
        target_x = x + offset_x
        target_y = y + offset_y
        MouseController.drag_cursor(target_x, target_y, duration=duration, button=button)