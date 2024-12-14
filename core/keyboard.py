import pyperclip
from typing import Optional, Literal
import pyautogui

class KeyboardController:
    @staticmethod
    def enter_text(text: str, delay: float = 0.05):
        """
        Enter the given text using the keyboard.

        :param text: The text to input.
        :param delay: The delay (in seconds) between each character.
        """
        pyautogui.typewrite(text, interval=delay)

    @staticmethod
    def perform_hotkey_action(
        *keys, 
        result_type: Literal["clipboard", "none"] = "none"
    ) -> Optional[str]:
        """
        Perform a hotkey combination and return the specified result.

        :param keys: The keys to execute as a hotkey combination.
        :param result_type: Specifies the type of result to return. "clipboard" returns the clipboard content, "none" returns nothing.
        :return: If `result_type` is "clipboard", returns the clipboard content; otherwise, returns None.
        """
        pyautogui.hotkey(*keys)

        if result_type == "clipboard":
            pyautogui.sleep(0.1)
            return ClipboardHandler.get_text()
        return None

class ClipboardHandler:
    @staticmethod
    def get_text() -> str:
        """
        Retrieve the current text content of the clipboard.

        :return: The text content from the clipboard.
        """
        try:
            return pyperclip.paste()
        except Exception as e:
            return ""

    @staticmethod
    def set_text(text: str):
        """
        Set the specified text to the clipboard.

        :param text: The text content to copy to the clipboard.
        """
        try:
            pyperclip.copy(text)
        except Exception as e:
            raise ValueError(f"Failed to copy to clipboard: {str(e)}")