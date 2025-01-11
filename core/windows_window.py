from typing import List, Dict, Optional, Tuple, Union, Any
import ctypes
from ctypes import wintypes
from core.utils import match_text

import ctypes
from ctypes import wintypes

class WindowManager:
    user32 = ctypes.windll.user32

    def valid_hwnd(func):
        """
        Decorator: Checks if the window handle is valid
        :param func: The method to be decorated
        """
        def wrapper(self, *args, **kwargs):
            window_id = args[0] if len(args) > 0 else kwargs.get("window_id")
            if window_id is None or not self.user32.IsWindow(window_id):
                raise ValueError(f"Invalid window handle: {window_id}")
            return func(self, *args, **kwargs)
        return wrapper

    def _all_window(self) -> List[wintypes.HWND]:
        """
        Get all top-level window handles
        :return: List containing all top-level window handles
        """
        window_id_list: List[wintypes.HWND] = []

        @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        def enum_windows_proc(window_id, lParam):
            if self.user32.IsWindow(window_id) and self.user32.IsWindowVisible(window_id):
                window_id_list.append(window_id)
            return True

        self.user32.EnumWindows(enum_windows_proc, 0)
        return window_id_list

    @valid_hwnd
    def _all_child_window(self, window_id: wintypes.HWND) -> List[wintypes.HWND]:
        """
        Get all child window handles of a specified parent window
        :param hwnd: Parent window handle
        :return: List containing child window handles
        """
        window_id_list: List[wintypes.HWND] = []
        @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        def enum_child_windows_proc(window_id, lParam):
            window_id_list.append(window_id)
            return True
        self.user32.EnumChildWindows(window_id, enum_child_windows_proc, 0)
        return window_id_list

    @valid_hwnd
    def _window_title(self, window_id: wintypes.HWND) -> str:
        """
        Get the window title
        :param window_id: Window handle
        :return: Window title string
        """
        length = self.user32.GetWindowTextLengthW(window_id)
        buffer = ctypes.create_unicode_buffer(length + 1)
        self.user32.GetWindowTextW(window_id, buffer, length + 1)
        return buffer.value

    @valid_hwnd
    def _window_class_name(self, window_id: wintypes.HWND) -> str:
        """
        Get the window class name
        :param window_id: Window handle
        :return: Window class name string
        """
        buffer = ctypes.create_unicode_buffer(256)
        self.user32.GetClassNameW(window_id, buffer, 256)
        return buffer.value

    @valid_hwnd
    def _get_window_region(self, window_id: wintypes.HWND) -> Tuple[int, int, int, int]:
        """
        Get the window's rectangle position
        :param window_id: Window handle
        :return: Tuple (left, top, right, bottom, width, height)
        """
        class RECT(ctypes.Structure):
            _fields_ = [
                ("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)
            ]
        region = RECT()
        if not self.user32.GetWindowRect(window_id, ctypes.byref(region)):
            raise ValueError(f"GetWindowRect call failed, error code: {ctypes.GetLastError()}")
        width = region.right - region.left
        height = region.bottom - region.top
        return region.left, region.top, width, height

    @valid_hwnd
    def _is_window_visible(self, window_id: wintypes.HWND) -> bool:
        """
        Check if the window is visible
        :param window_id: Window handle
        :return: True or False
        """
        return bool(self.user32.IsWindowVisible(window_id))

    @valid_hwnd
    def _is_window_enabled(self, window_id: wintypes.HWND) -> bool:
        """
        Check if the window is enabled
        :param window_id: Window handle
        :return: True or False
        """
        return bool(self.user32.IsWindowEnabled(window_id))

    @valid_hwnd
    def set_window_state(self, window_id: wintypes.HWND, state: Union[str, int]) -> None:
        """
        Change the window state (minimize, restore, maximize, etc.)
        :param window_id: Window handle
        :param state: Window state, possible values:
                    - 'minimized' or 0: Minimize the window
                    - 'normal' or 1: Normal window (not maximized)
                    - 'maximized' or 2: Maximize the window
                    - 'restore': Restore the window
        """
        SW_MINIMIZE = 6
        SW_NORMAL = 1
        SW_MAXIMIZE = 3
        SW_RESTORE = 9
        state_map = {
            0: "minimized",
            1: "normal",
            2: "maximized",
            "minimized": "minimized",
            "normal": "normal",
            "maximized": "maximized",
            "restore": "restore"
        }
        if state not in state_map:
            raise ValueError(f"Invalid window state: {state}. Valid values are: {list(state_map.keys())}")
        normalized_state = state_map[state]
        state_to_winapi = {
            "minimized": SW_MINIMIZE,
            "normal": SW_NORMAL,
            "maximized": SW_MAXIMIZE,
            "restore": SW_RESTORE,
        }
        result = self.user32.ShowWindow(window_id, state_to_winapi[normalized_state])
        if not result:
            raise ValueError(f"ShowWindow call failed, error code: {ctypes.GetLastError()}")

    @valid_hwnd
    def set_window_topmost(self, window_id: wintypes.HWND, topmost: bool = True) -> None:
        """
        Set the window to be topmost or not, allowing other windows to overlap
        :param window_id: Window handle
        :param topmost: True to make topmost, False to remove topmost
        """
        HWND_TOP = 0
        HWND_BOTTOM = 1
        SWP_NOSIZE = 0x0001
        SWP_NOMOVE = 0x0002
        SWP_SHOWWINDOW = 0x0040
        
        def send_set_window_pos(flag: int) -> None:
            result = self.user32.SetWindowPos(
                window_id,
                flag,
                0, 0, 0, 0,
                SWP_NOSIZE | SWP_NOMOVE | SWP_SHOWWINDOW
            )
            if not result:
                raise ValueError(f"SetWindowPos call failed, error code: {ctypes.GetLastError()}")
        
        if topmost:
            result = self.user32.SetForegroundWindow(window_id)
            if not result:
                raise ValueError(f"SetForegroundWindow call failed, error code: {ctypes.GetLastError()}")
            send_set_window_pos(HWND_TOP)
        else:
            send_set_window_pos(HWND_BOTTOM)

    @valid_hwnd
    def set_window_visibility(self, window_id: wintypes.HWND, visible: bool = True) -> None:
        """
        Show or hide a window
        :param window_id: Window handle
        :param visible: True to show, False to hide
        """
        SW_SHOWNORMAL = 1
        SW_MINIMIZE = 6
        SW_RESTORE = 9

        if visible:
            result = self.user32.ShowWindow(window_id, SW_RESTORE)
            if not result:
                raise ValueError(f"ShowWindow (SW_RESTORE) call failed, error code: {ctypes.GetLastError()}")
            result = self.user32.ShowWindow(window_id, SW_SHOWNORMAL)
            if not result:
                raise ValueError(f"ShowWindow (SW_SHOWNORMAL) call failed, error code: {ctypes.GetLastError()}")
        else:
            result = self.user32.ShowWindow(window_id, SW_MINIMIZE)
            if not result:
                raise ValueError(f"ShowWindow (SW_MINIMIZE) call failed, error code: {ctypes.GetLastError()}")

    def _get_window_info(self, window_id: wintypes.HWND) -> Dict[str, Any]:
        """
        Get detailed information of a single window
        :param window_id: Window handle
        :return: Dictionary containing window details
        """
        title = self._window_title(window_id)
        class_name = self._window_class_name(window_id)
        region = self._get_window_region(window_id)
        visible = self._is_window_visible(window_id)
        enabled = self._is_window_enabled(window_id)
        return {
            "window_id": window_id,
            "title": title,
            "class_name": class_name,
            "region": region,
            "visible": visible,
            "enabled": enabled,
        }

    def window_details(self, window_id: wintypes.HWND) -> Dict[str, Any]:
        """
        Get detailed information of a single window
        :param window_id: Window handle
        :return: Dictionary containing window details
        """
        return self._get_window_info(window_id)

    def get_window_details(self) -> List[Dict[str, Any]]:
        """
        Get detailed information of all top-level windows, including child window information
        :return: List of dictionaries containing window details
        """
        window_id_list = self._all_window()
        return [self.window_details(window_id) for window_id in window_id_list]

    def get_child_window_details(self, 
                                 window_id: wintypes.HWND
                                 ) -> Dict[str, Any]:
        """
        Get detailed information of all child windows
        :param window_id: Parent window handle
        :return: Dictionary containing parent and child window details
        """
        child_windows = self._all_child_window(window_id)
        child_info_list = [self._get_window_info(child_window_id) for child_window_id in child_windows]
        return {"window_id": window_id, "child_window": child_info_list}

    def is_window_match(self,
        window_obj: Union[dict, list], 
        title: str,
        match_mode: str = "exact",
        ignore_case: bool = False
    ) -> bool:
        """
        Compare window_obj with title and return the match result
        If window_obj is a single window, directly compare;
        If window_obj is a list of windows, iterate through the list to find the matching window.
        """
        if isinstance(window_obj, dict):
            return match_text(window_obj["title"], title, match_mode, ignore_case)
        elif isinstance(window_obj, list):
            return self.find_matching_window(window_obj, title, match_mode, ignore_case)
        else:
            raise ValueError("window_obj must be a single window dictionary or a list of window dictionaries")

    def find_matching_window(self, 
        all_window: List[Dict[str, Any]], 
        title: str,
        match_mode: str = "exact",
        ignore_case: bool = False
    ) -> Optional[Dict[str, Optional[Any]]]:
        """
        Find a window by title
        :param all_window: List of all windows
        :param title: Title to match
        :param match_mode: Matching mode ('exact', 'contains', etc.)
        :param ignore_case: Whether to ignore case in the comparison
        :return: Matched window dictionary or None
        """
        for window in all_window:
            if match_text(window["title"], title, match_mode, ignore_case):
                return window
        return None

    def close(self) -> None:
        """
        Placeholder method for closing or cleaning up resources (if needed)
        """
        pass
    @valid_hwnd
    def close_window(self, window_id):
        """
        windows close window for window_id
        """
        WM_CLOSE = 0x0010
        result = self.user32.PostMessageW(window_id, WM_CLOSE, 0, 0)
        if not result:
            raise RuntimeError(f"无法关闭窗口: {window_id}")
        return True
    
    def display_cursor(self, display = False):
        """windows display cursor

        Args:
            display (bool, optional): true - hidden, false - show. Defaults to False.
        """
        self.user32.ShowCursor(display)