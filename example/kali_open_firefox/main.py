#/usr/bin/env python
# -------: encoding: utf-8 :------

import os
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core import BaseConfig, ScreenCapture, ImageMatcher, utils, MouseController
def open_firefox():
    # 设置文件夹路径和截图文件路径
    draw_image = f"draw_window.png"
    BaseConfig.set_scale_factor(2)
    BaseConfig.set_threshold(0.7)
    # 1. 捕获桌面屏幕并保存初始截图
    screen = ScreenCapture()
    screen_desktop_window = screen.capture()
    utils.record_snapshot(screen_desktop_window, f"desktop_window.png")
    
    # 2. 匹配 Firefox 图标位置并双击打开
    image_matcher = ImageMatcher(BaseConfig.scale_factor, BaseConfig.threshold)
    thunder_template = utils.load_image_file(f"firefox_icon.png")
    processed_template = image_matcher.preprocess_input_image(
        thunder_template, 
            {
            }                                                    
        )
    processed_window = image_matcher.preprocess_input_image(
        screen_desktop_window, 
            {
                "blur": True
            }
        )
    locations = image_matcher.find_template_locations(processed_window, processed_template)
    draw_window = utils.draw_matches(screen_desktop_window, locations)
    utils.record_snapshot(draw_window, draw_image)

    # 获取匹配位置并执行双击操作
    local_position = locations[0].get("position")
    MouseController.move_cursor(local_position[0], local_position[1])
    MouseController.click_at(local_position[0], local_position[1], "left")
    time.sleep(5)
    
if __name__ == "__main__":
    open_firefox()