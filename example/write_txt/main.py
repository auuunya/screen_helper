#/usr/bin/env python
# -------: encoding: utf-8 :------

import os
import time
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core import (
    BaseConfig,
    ScreenHelperDefs,
    FileManager,
    ImageMatcher,
    KeyboardController,
    LoggerController,
    MouseController,
    OCRRecognizer,
    Result,
    ScreenCapture,
    TextRecognizer,
    WindowManager,
    ScreenHelper,
    utils
)

def screenshot_record_file(filename):
    screen_capture = ScreenCapture()
    arr = screen_capture.capture()
    screen_capture.record_snapshot(arr, filename)
    return arr

def match_template_and_move(screen, template):
    image_matcher = ImageMatcher()
    screen_arr = utils.load_image_file(screen)
    template_arr = utils.load_image_file(template)
    matches = image_matcher.find_template_locations(screen_arr, template_arr)
    position = matches[0]["position"]
    MouseController.move_cursor(position[0], position[1])

def cursor_click(action="left"):
    cur_pos = MouseController.get_cursor_position()
    MouseController.click_at(cur_pos[0], cur_pos[1], action)

def find_text_pos(screen, target_text, contexts):
    s_arr = utils.load_image_file(screen)
    ocr_engine = OCRRecognizer(ocr_engine="tesseract", lang='eng', config=r'--oem 3 --psm 11 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ& ')
    result = ocr_engine.recognize_text(s_arr)
    textrecognizer = TextRecognizer()
    find_pos = textrecognizer.find_text_position(result, target_text, contexts)
    pos = find_pos["position"]
    MouseController.move_cursor_with_offset(pos[0], pos[1], 0, 50)
    cur_pos = MouseController.get_cursor_position()
    MouseController.click_at(cur_pos[0], cur_pos[1], "left")


def delay_(duration):
    time.sleep(duration)

def main():
    screen_helper = ScreenHelper()
    ScreenHelper.add_action_method(
        "find_image",
        match_template_and_move
    )
    ScreenHelper.add_action_method(
        "take_screenshot",
        screenshot_record_file
    )
    ScreenHelper.add_action_method(
        "click",
        cursor_click
    )
    ScreenHelper.add_action_method(
        "find_text",
        find_text_pos
    )
    ScreenHelper.add_action_method(
        {
            "delay": delay_,
            "type_text": KeyboardController.enter_text
        },
    )
    current_dir = os.path.join(os.getcwd(), "example", "write_txt")
    actions = [
        {
            "action_type_text": "take_screenshot",
            "options": {
                "filename": f"{current_dir}/init_screenshot.png",
            }
        },
        {
            "action_type_text": "find_image",
            "options": {
                "screen": f"{current_dir}/init_screenshot.png",
                "template": f"{current_dir}/new_txt.png",
            }
        },
        {
            "action_type_text": "click",
            "options": {
                "action": "double"
            }
        },
        {
            "action_type_text": "delay",
            "options": {
                "duration": 5
            }
        },
        {
            "action_type_text": "take_screenshot",
            "options": {
                "filename": f"{current_dir}/notepad_window.png",
            }
        },
        {
            "action_type_text": "find_text",
            "options": {
                "screen": f"{current_dir}/notepad_window.png",
                "target_text": "File",
                "contexts": [
                    {
                        "text": "Edit",
                        "offset": {"x": 100, "y": 20}
                    }
                ]
            }
        },
        {
            "action_type_text": "type_text",
            "options": {
                "text": "TEST INPUT Body"
            }
        }

    ]
    try:
        actions_result = screen_helper.run_action_queue(actions)
        print (f"actions_result: {actions_result}")
    except Exception as e:
        raise

if __name__ == "__main__":
    main()