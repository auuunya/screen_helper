#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   window_matcher.py
@Desc    :   None
'''

# here put the import lib
import win32gui
import win32api
import win32con
import re
import time


class WindowManager:
    def __init__(self):
        self.hwnd = None

    def find_window_by_partial_title(self, partial_title):
        self.partial_title = partial_title
        self.hwnd = None
        try:
            win32gui.EnumWindows(self._window_enum_callback, None)
        except Exception as e:
            raise ValueError((f"调用 EnumWindows 发生异常: {e}, 错误码: {win32api.GetLastError()}")) 
        return self.hwnd

    def _window_enum_callback(self, hwnd, _):
        if not win32gui.IsWindow(hwnd):
            return True
        window_title = win32gui.GetWindowText(hwnd)
        if re.search(self.partial_title, window_title, re.IGNORECASE):
            self.hwnd = hwnd
            # print(f"找到匹配窗口: {window_title}, 句柄: {hwnd}")
            return
        win32gui.EnumChildWindows(hwnd, self._child_window_enum_callback, None)
    
    def _child_window_enum_callback(self, hwnd, _):
        child_window_title = win32gui.GetWindowText(hwnd)
        if re.search(self.partial_title, child_window_title, re.IGNORECASE):
            self.hwnd = hwnd
            # print(f"找到子窗口: {child_window_title}, 句柄: {hwnd}")
            return False

    def get_window_rect(self):
        if self.hwnd:
            return win32gui.GetWindowRect(self.hwnd)
        return None

    def bring_window_to_foreground(self):
        if self.hwnd:
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
            time.sleep(0.1)
            win32gui.SetForegroundWindow(self.hwnd)

    def get_window_at_mouse_click():
        x, y = win32api.GetCursorPos()
        hwnd = win32gui.WindowFromPoint((x, y))
        return hwnd