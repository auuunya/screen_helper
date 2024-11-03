#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   defs.py
@Desc    :   None
'''

# here put the import lib
class ScreenHelperDefs:

    CV_THRESHOLD = 0.8


    ACTION_TYPE_TEXT = "action_type_text"
    OPTIONS = "options"
    METHOD = "method"
    BUTTON = "button"
    OFFSET = "offset"
    MOVE_OFFSET = "move_offset"
    EXECUTION_IDENTIFIER = "execution_identifier"
    DIRECTION = "direction"

    CONTEXT_TEMPLATE = "template"
    CONTEXT_POSITION = "position"
    CONTEXT_THRESHOLD = "threshold"
    CONTEXT_OFFSET = "offset"

    # action_type 定义
    ACTION_TAKE_SCREENSHOT = "take_screenshot"
    ACTION_FIND_IMAGE = "find_image"
    ACTION_FIND_TEXT = "find_text"
    ACTION_PERFORM_MOUSE_ACTION = "perform_mouse_action"
    ACTION_SEND_TEXT = "send_text"
    ACTION_SEND_HOTKEY = "send_hotkey"
    ACTION_APPLY_DELAY = "apply_delay"
    ACTION_MANAGE_FILE = "manage_file"
    ACTION_HANDLE_WINDOW = "handle_window"
    ACTION_EXIT_APPLICATION = "exit_application"

    # mouse 定义
    MOVE = "move"
    CLICK = "click"
    DOUBLE = "double"
    DRAG = "drag"
    DROP = "drop"
    SCROLL = "scroll"
    
    # Direction 定义
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"

    # Hotkey 定义
    CTRL = "ctrl"
    ALT = "alt"
    SHIFT = "shift"
    ENTER = "enter"
    ESC = "esc"
    TAB = "tab"
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"

    # window 定义
    OPEN = "open"
    CLOSE = "close"
    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"
    RESTORE = "restore"
    SWITCH = "switch"

    # 文本定义
    SEND_TEXT = "send_text"
    FIND_TEXT = "find_text"
    COPY_TEXT = "copy_text"
    PASTE_TEXT = "paste_text"
    CLEAR_TEXT = "clear_text"