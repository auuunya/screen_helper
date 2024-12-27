import Xlib
import Xlib.display
import Xlib.X
import Xlib.protocol
from typing import List, Dict, Optional, Tuple, Union
from utils import match_title

"""
Xlib-based Window Manager

This module provides functionality to manage and manipulate windows in a Linux environment using Xlib. It includes 
methods for querying window properties, changing window states, and interacting with the X server.
"""

def send_client_message_event(
    display, 
    window, 
    client_type, 
    data, 
    root=None, 
    event_mask=Xlib.X.SubstructureRedirectMask | Xlib.X.SubstructureNotifyMask
):
    """
    General method for sending ClientMessage events.

    :param display: Xlib Display object.
    :param window: Target window object.
    :param client_type: Atom type representing the event type (e.g., _NET_WM_STATE).
    :param data: A list of integers representing the event data. Must have a maximum length of 5.
    :param root: Root window object. Defaults to display.screen().root.
    :param event_mask: Event mask, defaults to SubstructureRedirectMask | SubstructureNotifyMask.
    """
    if len(data) > 5:
        raise ValueError("Data length cannot exceed 5.")
    data = (data + [0] * (5 - len(data)))[:5]  # Pad to 5 integers.
    event = Xlib.protocol.event.ClientMessage(
        window=window,
        client_type=client_type,
        data=(32, data)  # Data format is 32-bit integers.
    )
    if root is None:
        root = display.screen().root
    root.send_event(event, event_mask=event_mask)
    display.flush()

class WindowManager:
    def __init__(self):
        """
        Initialize the WindowManager with access to the X server display and root window.
        """
        self.display = Xlib.display.Display()
        self.root = self.display.screen().root

    def valid_window(func):
        """
        Decorator: Checks if a window ID is valid before executing the decorated method.

        :param func: The method to decorate.
        """
        def wrapper(self, *args, **kwargs):
            window_id = args[0] if len(args) > 0 else kwargs.get("window_id")
            if window_id is None:
                raise ValueError("Invalid window ID: None")
            try:
                window = self.display.create_resource_object("window", window_id)
                window.get_attributes()
            except:
                raise ValueError(f"Invalid window ID: {window_id}")
            return func(self, *args, **kwargs)
        return wrapper

    def _root(self) -> List[int]:
        """
        Retrieve all windows and child windows associated with the root window.

        :return: A list of all window IDs.
        """
        window_objs = self.root.query_tree().children
        return [window.id for window in window_objs]

    def _all_window(self) -> List[int]:
        """
        Retrieve all application window handles.

        :return: A list of window IDs for all client windows.
        """
        _net_client_list = self.display.get_atom('_NET_CLIENT_LIST')
        client_list = self.root.get_full_property(
            _net_client_list,
            Xlib.X.AnyPropertyType,
        ).value
        return client_list

    @valid_window
    def _all_child_window(self, window_id: int) -> List[int]:
        """
        Retrieve all child windows for a given parent window.

        :param window_id: The parent window handle.
        :return: A list of child window handles.
        """
        window = self.display.create_resource_object("window", window_id)
        child_window_objs = window.query_tree().children
        return [window.id for window in child_window_objs]

    @valid_window
    def _window_title(self, window_id: int) -> str:
        """
        Retrieve the title of a specified window.

        :param window_id: The window handle.
        :return: The window title as a string.
        """
        window = self.display.create_resource_object("window", window_id)
        title = window.get_full_property(self.display.intern_atom('_NET_WM_NAME'), 0)
        return title.value if title else ""

    @valid_window
    def _window_class_name(self, window_id: int) -> str:
        """
        Retrieve the class name of a specified window.

        :param window_id: The window handle.
        :return: The window class name as a string.
        """
        window = self.display.create_resource_object("window", window_id)
        cls = window.get_full_property(self.display.intern_atom('WM_CLASS'), Xlib.X.AnyPropertyType)
        if cls:
            class_name = cls.value[0] if cls.value else ""
            return class_name
        else:
            return ""

    @valid_window
    def _get_window_rect(self, window_id: int) -> Tuple[int, int, int, int]:
        """
        Retrieve the geometry information of a specified window.

        :param window_id: The window handle.
        :return: A tuple containing (x, y, height, width).
        """
        window = self.display.create_resource_object("window", window_id)
        geom = window.get_geometry()
        (x, y) = (geom.x, geom.y)
        while True:
            parent = window.query_tree().parent
            pgeom = parent.get_geometry()
            x += pgeom.x
            y += pgeom.y
            if parent.id == self.root.id:
                break
            window = parent
        return x, y, geom.height, geom.width

    @valid_window
    def _is_window_visible(self, window_id: int) -> bool:
        """
        Check if a specified window is visible.

        :param window_id: The window handle.
        :return: True if the window is visible, False otherwise.
        """
        window = self.display.create_resource_object("window", window_id)
        attributes = window.get_attributes()
        return attributes.map_state == Xlib.X.IsViewable


    @valid_window
    def set_window_state(self, window_id: int, state: Union[str, int]) -> None:
        """
        Change the state of a window (maximize, minimize, or restore).
        :param window_id: Window handle.
        :param state: Window state, valid values include:
                    - 'minimized' or 0: Minimize the window.
                    - 'normal' or 1: Normal window (not maximized).
                    - 'maximized' or 2: Maximize the window.
                    - 'restore': Restore the window.
        """

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
            raise ValueError(f"Invalid window state: {state}. Valid value: {list(state_map.keys())}")
        normalized_state = state_map[state]

        _net_wm_state_max_vert = self.display.intern_atom("_NET_WM_STATE_MAXIMIZED_VERT", False)
        _net_wm_state_max_horz = self.display.intern_atom("_NET_WM_STATE_MAXIMIZED_HORZ", False)
        _net_wm_state_hidden = self.display.intern_atom("_NET_WM_STATE_HIDDEN", False)
        _net_wm_state = self.display.intern_atom("_NET_WM_STATE", False)

        window = self.display.create_resource_object("window", window_id)
        
        if normalized_state in ["maximized", "normal"]:
            # First check whether it is minimized (hidden state), and if so, restore
            wm_state = window.get_full_property(_net_wm_state, Xlib.X.AnyPropertyType)
            if wm_state and _net_wm_state_hidden in wm_state.value:
                send_client_message_event(
                    self.display,
                    window, 
                    client_type=self.display.intern_atom("_NET_WM_STATE", False),
                    data=[0, _net_wm_state_max_vert, _net_wm_state_max_horz],
                    root=self.root
                )

        if normalized_state == "maximized":
            send_client_message_event(
                self.display, 
                window, 
                client_type=self.display.intern_atom("_NET_WM_STATE", False),
                data=[1, _net_wm_state_max_vert, _net_wm_state_max_horz], 
                root=self.root
            )
        elif normalized_state == "minimized":
            send_client_message_event(
                self.display, 
                window, 
                client_type=self.display.intern_atom("_NET_WM_STATE", False),
                data=[1, _net_wm_state_hidden], 
                root=self.root
            )
        elif normalized_state == "restore":
            # Remove on recovery _NET_WM_STATE_HIDDEN
            send_client_message_event(
                self.display, 
                window, 
                client_type=self.display.intern_atom("_NET_WM_STATE", False),
                data=[0, _net_wm_state_hidden], 
                root=self.root
            )
        elif normalized_state == "normal":
            # Make sure to remove the maximized state
            send_client_message_event(
                self.display, 
                window, 
                client_type=self.display.intern_atom("_NET_WM_STATE", False),
                data=[0, _net_wm_state_max_vert, _net_wm_state_max_horz], 
                root=self.root
            )
        else:
            raise ValueError(f"Unknown window state: {normalized_state}")
        
    @valid_window
    def set_window_topmost(self, window_id: int, topmost: bool = True) -> None:
        """
        Set the window as topmost or cancel the topmost status, allowing other windows to overlap.
        :param window_id: Window handle.
        :param topmost: True to set the window as topmost, False to cancel topmost.
        """
        window = self.display.create_resource_object("window", window_id)
        if topmost:
            window.configure(stack_mode=Xlib.X.Above)
        else:
            window.configure(stack_mode=Xlib.X.Below)
        self.display.flush()
        # TODO: plan B
        # _net_wm_state_above = self.display.intern_atom('_NET_WM_STATE_ABOVE', False)
        # if topmost:
        #     send_state_event(self.root, self.display, window, 1, _net_wm_state_above)
        # else:
        #     send_state_event(self.root, self.display, window, 0, _net_wm_state_above)

    @valid_window
    def set_window_visibility(self, window_id: int, visible: bool = True) -> None:
        """
        Set the visibility of the window.
        Show or hide the window.
        :param window_id: Window handle.
        :param visible: True to show the window, False to hide the window.
        """

        _net_wm_state_hidden = self.display.intern_atom('_NET_WM_STATE_HIDDEN', False)
        window = self.display.create_resource_object('window', window_id)
        event_mask = Xlib.X.SubstructureRedirectMask | Xlib.X.SubstructureNotifyMask
        if visible:
            send_client_message_event(
                self.display, 
                window, 
                client_type=self.display.intern_atom("_NET_WM_STATE", False),
                data=[0, _net_wm_state_hidden], 
                root=self.root,
                event_mask=event_mask
            )
            send_client_message_event(
                self.display, 
                window, 
                client_type=self.display.intern_atom("_NET_ACTIVE_WINDOW", False),
                data=[1, Xlib.X.CurrentTime, 0, 0, 0],
                root=self.root,
                event_mask=event_mask
            )
            window.map()
        else:
            send_client_message_event(
                self.display, 
                window, 
                client_type=self.display.intern_atom("_NET_WM_STATE", False),
                data=[1, _net_wm_state_hidden], 
                root=self.root,
                event_mask=event_mask
            )
            window.unmap()
        self.display.flush()

    def _get_window_info(self, window_id: int) -> Dict[str, any]:
        """
        Get detailed information about a single window.
        """
        title = self._window_title(window_id)
        class_name = self._window_class_name(window_id)
        region = self._get_window_rect(window_id)
        visible = self._is_window_visible(window_id)
        return {
            "window_id": window_id,
            "title": title,
            "class_name": class_name,
            "region": region,
            "visible": visible,
            "enabled": "",
        }

    def window_details(self, window_id: int) -> Dict[str, any]:
        """
        Get detailed information about a single window.
        :param window_id: Window handle.
        :return: A dictionary containing detailed information about the window.
        """
        return self._get_window_info(window_id)
        

    def get_window_details(self) -> List[Dict[str, any]]:
        """
        Retrieve detailed information about all top-level windows, including sub-windows.
        :return: A list of dictionaries containing detailed window information.
        """
        window_id_list = self._all_window()
        return [self.window_details(window_id) for window_id in window_id_list]
    
    def get_child_window_details(self, window_id: int) -> Dict[str, any]:
        """
        Retrieve detailed information about all child windows.
        :param window_id: Parent window handle.
        :return: A dictionary containing detailed information about the parent and its child windows.
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
        Compare `window_obj` with `title` to determine if they match.
        If `window_obj` is a single window, compare directly;
        If `window_obj` is a list of windows, iterate through the list to find a matching window.
        """
        if isinstance(window_obj, dict):
            return match_title(window_obj["title"], title, match_mode, ignore_case)
        elif isinstance(window_obj, list):
            return self.find_matching_window(window_obj, title, match_mode, ignore_case)
        else:
            raise ValueError("window_obj 必须是单个窗口字典或窗口字典列表")
        
    def find_matching_window(self, 
                             all_window: List[Dict[str, any]], 
                             title: str, 
                             match_mode: str = "exact", 
                             ignore_case: bool = False
                             ) -> Optional[Dict[str, any]]:
        """
        Find a window by its title.
        :param all_window: List of all window dictionaries.
        :param title: Title to match.
        :param match_mode: Matching mode ('exact', 'contains', etc.).
        :param ignore_case: Whether to ignore case in the comparison.
        :return: A dictionary representing the matched window, or None if no match is found.
        """
        for window in all_window:
            if match_title(window["title"], title, match_mode, ignore_case):
                return window
        return None

    def close(self) -> None:
        """
        Close the connection to the X server.
        """
        self.display.close()
    @valid_window
    def close_window(self, window_id):
        """
        linux close window for window_id
        """
        window = self.display.create_resource_object('window', window_id)
        window.destroy()
        self.display.sync()
        return True

    def display_cursor(self, display = False):
        """linux display cursor

        Args:
            display (bool, optional): true - hidden, false - show. Defaults to False.
        """
        event_mask = Xlib.X.EnterWindowMask if display else Xlib.X.LeaveWindowMask
        self.root.change_attributes(event_mask=event_mask)
        self.display.sync()
