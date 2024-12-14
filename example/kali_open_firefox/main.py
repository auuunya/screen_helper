#/usr/bin/env python
# -------: encoding: utf-8 :------

import os
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core import ScreenCapture, ImageMatcher, utils, MouseController
def open_firefox():
    draw_image = f"draw_window.png"
    scale_factor = 2
    threshold = 0.7
    screen = ScreenCapture()
    screen_desktop_window = screen.capture()
    utils.record_snapshot(screen_desktop_window, f"desktop_window.png")
    image_matcher = ImageMatcher()
    thunder_template = utils.load_entity_file(f"firefox_icon.png")
    processed_template = image_matcher.preprocess_entity(
        thunder_template, 
            {
            }                                                    
        )
    processed_window = image_matcher.preprocess_entity(
        screen_desktop_window, 
            {
                "blur": True
            }
        )
    locations = image_matcher.find_template_locations(
        screen_desktop_window,
        thunder_template,
        processed_window, 
        processed_template,
        threshold=threshold
    )
    draw_window = utils.draw_matches(screen_desktop_window, locations)
    utils.record_snapshot(draw_window, draw_image)
    local_position = locations[0].get("position")
    MouseController.move_cursor(local_position[0], local_position[1])
    MouseController.click_at(local_position[0], local_position[1], "left")
    time.sleep(5)
    
if __name__ == "__main__":
    open_firefox()