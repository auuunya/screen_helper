from .defs import ScreenHelperDefs
from typing import Tuple
import pyautogui

class MouseController:
    """
    A controller class for managing mouse actions such as moving, clicking, scrolling, and dragging.
    """

    @staticmethod
    def move_cursor(x: int, y: int, duration: float = 0.2):
        """
        Move the mouse cursor to the specified coordinates.
        :param x: Target x-coordinate.
        :param y: Target y-coordinate.
        :param duration: Duration of the movement (in seconds).
        """
        pyautogui.moveTo(x, y, duration=duration)
    
    @staticmethod
    def move_cursor_with_offset(x: int, y: int, offset_x: int = 0, offset_y: int = 0):
        """
        Move the mouse cursor to the specified coordinates with an added offset.
        :param x: Base x-coordinate.
        :param y: Base y-coordinate.
        :param offset_x: Offset added to the x-coordinate.
        :param offset_y: Offset added to the y-coordinate.
        """
        target_x = x + offset_x
        target_y = y + offset_y
        MouseController.move_cursor(target_x, target_y)

    @staticmethod
    def click_at(x: int, y: int, action: str = "left", interval: float = 0.15):
        """
        Perform a click action at the specified coordinates.
        :param x: x-coordinate to click.
        :param y: y-coordinate to click.
        :param action: Type of click action; can be "left", "right", or "double".
        :param interval: Interval between clicks for a double-click (in seconds).
        """
        if action in [ScreenHelperDefs.LEFT, ScreenHelperDefs.RIGHT, ScreenHelperDefs.MIDDLE]:
            pyautogui.click(x, y, button=action)
        elif action == ScreenHelperDefs.DOUBLE:
            pyautogui.doubleClick(x, y, interval)
        else:
            raise ValueError(f"Unknown mouse action: {action}")

    @staticmethod
    def get_cursor_position() -> Tuple[int, int]:
        """
        Get the current position of the mouse cursor.
        :return: The current x and y coordinates of the mouse cursor.
        """
        return pyautogui.position()

    @staticmethod
    def scroll(delta: int, direction: str):
        """
        Scroll the mouse wheel.
        :param delta: Distance to scroll (positive for up, negative for down).
        :param direction: Direction of the scroll, can be "up", "down", "left", or "right".
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
            raise ValueError(f"Unknown scroll direction: {direction}")

    @staticmethod
    def drag_cursor(x: int, y: int, duration: float = 0.2, action: str = "left"):
        """
        Drag the mouse cursor to the specified coordinates.
        :param x: Target x-coordinate.
        :param y: Target y-coordinate.
        :param duration: Duration of the drag action (in seconds).
        :param action: Button to use for dragging, defaults to "left" (supports "left", "right", and "middle").
        """
        if action in [ScreenHelperDefs.LEFT, ScreenHelperDefs.RIGHT, ScreenHelperDefs.MIDDLE]:
            pyautogui.dragTo(x, y, duration=duration, button=action)
        else:
            raise ValueError(f"Unknown drag button: {action}")

    @staticmethod
    def drag_cursor_with_offset(x: int, y: int, offset_x: int = 0, offset_y: int = 0, duration: float = 0.2, button: str = "left"):
        """
        Drag the mouse cursor to the specified coordinates with an added offset.
        :param x: Starting x-coordinate.
        :param y: Starting y-coordinate.
        :param offset_x: Offset added to the x-coordinate.
        :param offset_y: Offset added to the y-coordinate.
        :param duration: Duration of the drag action (in seconds).
        :param button: Button to use for dragging, defaults to "left" (supports "left", "right", and "middle").
        """
        target_x = x + offset_x
        target_y = y + offset_y
        MouseController.drag_cursor(target_x, target_y, duration=duration, action=button)
