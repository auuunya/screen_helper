import re
from typing import List, Dict, Optional, Callable, Tuple
import ctypes
from ctypes import wintypes
class WindowsManagerCtypes:
    # 定义 Windows API 中使用的数据类型和常量
    user32 = ctypes.windll.user32
    
    SWP_NOSIZE = 1
    SWP_NOMOVE = 2
    SWP_NOZORDER = 4
    SWP_NOREDRAW = 8
    SWP_NOACTIVATE = 16
    SWP_FRAMECHANGED = 32
    SWP_SHOWWINDOW = 64
    SWP_HIDEWINDOW = 128
    SWP_NOCOPYBITS = 256
    SWP_NOOWNERZORDER = 512
    SWP_NOSENDCHANGING = 1024
    SWP_DRAWFRAME = SWP_FRAMECHANGED
    SWP_NOREPOSITION = SWP_NOOWNERZORDER
    SWP_DEFERERASE = 8192
    SWP_ASYNCWINDOWPOS = 16384

    SW_HIDE = 0
    SW_SHOWNORMAL = 1
    SW_NORMAL = 1
    SW_SHOWMINIMIZED = 2
    SW_SHOWMAXIMIZED = 3
    SW_MAXIMIZE = 3
    SW_SHOWNOACTIVATE = 4
    SW_SHOW = 5
    SW_MINIMIZE = 6
    SW_SHOWMINNOACTIVE = 7
    SW_SHOWNA = 8
    SW_RESTORE = 9
    SW_SHOWDEFAULT = 10
    SW_FORCEMINIMIZE = 11
    SW_MAX = 11

    HWND_TOP = 0
    HWND_BOTTOM = 1
    HWND_TOPMOST = -1
    HWND_NOTOPMOST = -2

    def valid_hwnd(func: Callable) -> Callable:
        """
        装饰器：检查窗口句柄是否有效
        :param func: 被装饰的方法
        """
        def wrapper(self, *args, **kwargs):
            hwnd = args[0] if len(args) > 0 else kwargs.get("hwnd")
            if hwnd is None or not self.user32.IsWindow(hwnd):
                raise ValueError(f"无效的窗口句柄: {hwnd}")
            return func(self, *args, **kwargs)
        return wrapper
    def _all_window(self) -> List[int]:
        """
        获取所有顶层窗口句柄
        :return: 包含所有顶层窗口句柄的列表
        """
        hwnd_list: List[int] = []

        @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        def enum_windows_proc(hwnd, lParam):
            if self.user32.IsWindow(hwnd) and self.user32.IsWindowVisible(hwnd):
                hwnd_list.append(hwnd)
            return True

        self.user32.EnumWindows(enum_windows_proc, 0)
        return hwnd_list

    @valid_hwnd
    def _all_child_window(self, hwnd: int) -> List[int]:
        """
        获取指定父窗口的所有子窗口句柄
        :param hwnd: 父窗口句柄
        :return: 包含子窗口句柄的列表
        """
        hwnd_list: List[int] = []
        @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        def enum_child_windows_proc(hwnd, lParam):
            hwnd_list.append(hwnd)
            return True
        self.user32.EnumChildWindows(hwnd, enum_child_windows_proc, 0)
        return hwnd_list

    @valid_hwnd
    def _window_title(self, hwnd: int) -> str:
        """
        获取窗口标题
        :param hwnd: 窗口句柄
        :return: 窗口标题字符串
        """
        length = self.user32.GetWindowTextLengthW(hwnd)
        buffer = ctypes.create_unicode_buffer(length + 1)
        self.user32.GetWindowTextW(hwnd, buffer, length + 1)
        return buffer.value
    @valid_hwnd
    def _window_class_name(self, hwnd: int) -> str:
        """
        获取窗口类名
        :param hwnd: 窗口句柄
        :return: 窗口类名字符串
        """
        buffer = ctypes.create_unicode_buffer(256)
        self.user32.GetClassNameW(hwnd, buffer, 256)
        return buffer.value

    @valid_hwnd
    def _get_window_rect(self, hwnd: int) -> Tuple[int, int, int, int]:
        """
        获取窗口矩形位置
        :param hwnd: 窗口句柄
        :return: 窗口的 (left, top, right, bottom) 元组
        """
        rect = wintypes.RECT()
        self.user32.GetWindowRect(hwnd, ctypes.byref(rect))
        return rect.left, rect.top, rect.right, rect.bottom

    @valid_hwnd
    def _is_window_visible(self, hwnd: int) -> bool:
        """
        检查窗口是否可见
        :param hwnd: 窗口句柄
        :return: True 或 False
        """
        return bool(self.user32.IsWindowVisible(hwnd))

    @valid_hwnd
    def _is_window_enabled(self, hwnd: int) -> bool:
        """
        检查窗口是否启用
        :param hwnd: 窗口句柄
        :return: True 或 False
        """
        return bool(self.user32.IsWindowEnabled(hwnd))
    @valid_hwnd
    def set_window_state(self, hwnd: int, state: str) -> None:
        """
        更改窗口状态（最大化、最小化或还原）
        :param hwnd: 窗口句柄
        :param state: 窗口状态，可选值：
                    - "maximize": 最大化窗口
                    - "minimize": 最小化窗口
                    - "restore": 还原窗口
        """
        states = {
            "maximize": self.SW_MAXIMIZE,
            "minimize": self.SW_MINIMIZE,
            "restore": self.SW_RESTORE,
        }
        if state not in states:
            raise ValueError(f"无效的窗口状态: {state}. 有效值为: {', '.join(states.keys())}")
        result = self.user32.ShowWindow(hwnd, states[state])
        if not result:
            raise ValueError(f"ShowWindow 调用失败，错误代码: {ctypes.GetLastError()}")
        
    @valid_hwnd
    def set_window_topmost(self, hwnd: int, topmost: bool = True) -> None:
        """
        设置窗口置顶或取消置顶
        :param hwnd: 窗口句柄
        :param topmost: True 表示置顶，False 表示取消置顶
        """
        result = self.user32.SetForegroundWindow(hwnd)
        if not result:
            raise ValueError(f"SetForegroundWindow 调用失败，错误代码: {ctypes.GetLastError()}")
        # TODO: 使用时一直报1400错误，预想是参数错误
        # flag = self.HWND_TOPMOST if topmost else self.HWND_NOTOPMOST
        # result = self.user32.SetWindowPos(
        #     hwnd,
        #     flag,
        #     0, 0, 0, 0,
        #     self.SWP_SHOWWINDOW | self.SWP_NOSIZE| self.SWP_NOMOVE
        # )
        # if not result:
        #     raise ValueError(f"SetWindowPos 调用失败，错误代码: {ctypes.GetLastError()}")

    @valid_hwnd
    def set_window_visibility(self, hwnd: int, visible: bool = True) -> None:
        """
        显示或隐藏窗口
        :param hwnd: 窗口句柄
        :param visible: True 表示显示，False 表示隐藏
        """
        flag = self.SW_SHOW if visible else self.SW_HIDE
        result = self.user32.ShowWindow(hwnd, flag)
        if not result:
            raise ValueError(f"ShowWindow 调用失败，错误代码: {ctypes.GetLastError()}")

    def get_window_details(self) -> List[Dict]:
        """
        获取所有顶层窗口的详细信息，包括子窗口信息
        :return: 包含窗口详细信息的字典列表
        """
        hwnd_list = self._all_window()
        window_info_list = []
        for hwnd in hwnd_list:
            title = self._window_title(hwnd)
            class_name = self._window_class_name(hwnd)
            rect = self._get_window_rect(hwnd)
            visible = self._is_window_visible(hwnd)
            enabled = self._is_window_enabled(hwnd)
            window_info = {
                "hwnd": hwnd,
                "title": title,
                "class_name": class_name,
                "rect": {
                    "left": rect[0],
                    "top": rect[1],
                    "right": rect[2],
                    "bottom": rect[3],
                    "width": rect[2] - rect[0],
                    "height": rect[3] - rect[1],
                },
                "visible": visible,
                "enabled": enabled,
            }
            window_info_list.append(window_info)
        return window_info_list
    
    def get_child_window_details(self, hwnd: int) -> Dict:
        """
        获取所有子窗口的详细信息
        :return: 窗口包含窗口详细信息的字典列表
        """
        child_windows = self._all_child_window(hwnd)
        child_info_list = []
        for child_hwnd in child_windows:
            child_title = self._window_title(child_hwnd)
            child_class_name = self._window_class_name(child_hwnd)
            child_rect = self._get_window_rect(child_hwnd)
            child_info_list.append({
                "hwnd": child_hwnd,
                "title": child_title,
                "class_name": child_class_name,
                "rect": {
                    "left": child_rect[0],
                    "top": child_rect[1],
                    "right": child_rect[2],
                    "bottom": child_rect[3],
                    "width": child_rect[2] - child_rect[0],
                    "height": child_rect[3] - child_rect[1],
                },
            })
        return {"hwnd": hwnd, "child_window": child_info_list}
    
    def find_window_by_title(self, title: str, window_list: List[Dict], match_mode: str = "exact", ignore_case: bool = False) -> Optional[Dict]:
        """
        从传递的窗口列表中根据标题查找窗口信息
        支持：精确匹配、模糊匹配、正则表达式匹配，并可选择忽略大小写
        :param title: 窗口标题
        :param window_list: 包含窗口详细信息的列表
        :param match_mode: 匹配模式，可选值：
                            - "exact": 精确匹配（默认）
                            - "contains": 标题包含匹配
                            - "regex": 正则表达式匹配
        :param ignore_case: 是否忽略大小写（默认为 False）
        :return: 符合标题的窗口详细信息字典，如果未找到则返回 None
        """
        def matches(text: str, pattern: str) -> bool:
            """
            内部匹配逻辑，根据 match_mode 和 ignore_case 设置进行匹配
            """
            if ignore_case:
                text = text.lower()
                pattern = pattern.lower()

            if match_mode == "exact":
                return text == pattern
            elif match_mode == "contains":
                return pattern in text
            elif match_mode == "regex":
                try:
                    return re.search(pattern, text) is not None
                except re.error:
                    raise ValueError(f"无效的正则表达式: {pattern}")
            else:
                raise ValueError(f"无效的匹配模式: {match_mode}")

        for window in window_list:
            if matches(window["title"], title):
                return window
        return None
