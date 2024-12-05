# This class contains constants used throughout the automation framework for various actions, window states, 
# mouse operations, text interactions, and key bindings. These constants provide a central place to manage 
# the definitions of common actions and identifiers that are used in the framework to perform automation tasks.
# 
# Constants are organized into categories for easier reference:
# - General action types like screenshot capture and text input.
# - Mouse actions such as click, drag, and scroll.
# - Directional commands for movement.
# - Hotkey definitions like CTRL, ALT, SHIFT, and others.
# - Window management actions like open, close, maximize, and minimize.
# - Text manipulation commands such as send, find, copy, paste, and clear text.

class ScreenHelperDefs:
    # General threshold for image matching
    CV_THRESHOLD = 0.8
    
    # General keys for options and configurations
    ACTION_TYPE_TEXT = "action_type_text"
    OPTIONS = "options"
    METHOD = "method"
    BUTTON = "button"
    OFFSET = "offset"
    MOVE_OFFSET = "move_offset"
    EXECUTION_IDENTIFIER = "execution_identifier"
    DIRECTION = "direction"

    # Context definitions for actions
    CONTEXT_TEMPLATE = "template"
    CONTEXT_POSITION = "position"
    CONTEXT_THRESHOLD = "threshold"
    CONTEXT_OFFSET = "offset"

    # Action types
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

    # Mouse action types
    MOVE = "move"
    CLICK = "click"
    DOUBLE = "double"
    DRAG = "drag"
    DROP = "drop"
    SCROLL = "scroll"
    
    # Direction definitions
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"

    # Hotkey definitions
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

    # Window state definitions
    OPEN = "open"
    CLOSE = "close"
    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"
    RESTORE = "restore"
    SWITCH = "switch"

    # Text interaction definitions
    SEND_TEXT = "send_text"
    FIND_TEXT = "find_text"
    COPY_TEXT = "copy_text"
    PASTE_TEXT = "paste_text"
    CLEAR_TEXT = "clear_text"
