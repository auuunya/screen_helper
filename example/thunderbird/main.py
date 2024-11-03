#/usr/bin/env python
# -------: encoding: utf-8 :------

import platform
import json
import os
import random
import string
import time
import pytesseract

from core import ScreenHelper, ScreenCapture, ImageMatcher, \
    MouseController, OCRRecognizer, TextRecognizer, KeyboardController

def send_mail():
    # 设置文件夹路径和截图文件路径
    draw_image = f"draw_window.png"
    
    # 1. 捕获桌面屏幕并保存初始截图
    screen = ScreenCapture()
    screen_desktop_window = screen.capture()
    screen.record_screen_snapshot(screen_desktop_window, f"desktop_window.png")
    
    # 2. 匹配 Thunderbird 图标位置并双击打开
    image_matcher = ImageMatcher()
    thunder_template = image_matcher.load_image_file(f"thunderbird.png")
    locations = image_matcher.find_template_locations(screen_desktop_window, thunder_template)
    filter_location = image_matcher.filter_nearby_matches(locations, 10)
    draw_window = image_matcher.draw_matches(screen_desktop_window, filter_location)
    screen.record_screen_snapshot(draw_window, draw_image)
    
    # 获取匹配位置并执行双击操作
    local_position = filter_location[0].get("position")
    MouseController.move_cursor(local_position[0], local_position[1])
    MouseController.click_at(local_position[0], local_position[1], "double")
    time.sleep(5)
    
    # 3. 捕获 Thunderbird 窗口并保存截图
    screen_thunderbird_window = screen.capture()
    screen.record_screen_snapshot(screen_thunderbird_window, f"thunderbird_window.png")
    
    # 4. 匹配 “写邮件” 按钮并单击
    thunder_template = image_matcher.load_image_file(f"write_mail.png")
    locations = image_matcher.find_template_locations(screen_thunderbird_window, thunder_template)
    filter_location = image_matcher.filter_nearby_matches(locations, 10)
    draw_window = image_matcher.draw_matches(screen_thunderbird_window, filter_location)
    screen.record_screen_snapshot(draw_window, draw_image)
    
    local_position = filter_location[0].get("position")
    MouseController.move_cursor(local_position[0], local_position[1])
    MouseController.click_at(local_position[0], local_position[1], "left")
    time.sleep(2)
    
    # 5. 捕获 “写邮件” 窗口并保存截图
    thunderbird_write_mail_window = screen.capture()
    screen.record_screen_snapshot(thunderbird_write_mail_window, f"thunderbird_write_mail_window.png")
    
    # 6. 定位收件人输入框并输入邮箱地址
    thunder_template = image_matcher.load_image_file(f"shou.png")
    locations = image_matcher.find_template_locations(thunderbird_write_mail_window, thunder_template, 0.7)
    filter_location = image_matcher.filter_nearby_matches(locations, 10)
    draw_window = image_matcher.draw_matches(thunderbird_write_mail_window, filter_location)
    screen.record_screen_snapshot(draw_window, draw_image)
    
    local_position = filter_location[0].get("position")
    MouseController.move_cursor_with_offset(local_position[0], local_position[1], 20, 0)
    cur_pos = MouseController.get_cursor_position()
    MouseController.click_at(cur_pos[0], cur_pos[1], "left")
    KeyboardController.enter_text("test123@163.com")
    
    # 7. 定位主题输入框并输入主题内容
    thunder_template = image_matcher.load_image_file(f"zhuti.png")
    locations = image_matcher.find_template_locations(thunderbird_write_mail_window, thunder_template)
    filter_location = image_matcher.filter_nearby_matches(locations, 10)
    draw_window = image_matcher.draw_matches(thunderbird_write_mail_window, filter_location)
    screen.record_screen_snapshot(draw_window, draw_image)
    
    local_position = filter_location[0].get("position")
    MouseController.move_cursor_with_offset(local_position[0], local_position[1], 20, 0)
    cur_pos1 = MouseController.get_cursor_position()
    MouseController.click_at(cur_pos1[0], cur_pos1[1], "left")
    KeyboardController.enter_text("UIAutomation Test Subject")
    time.sleep(2)
    
    # 8. 定位邮件正文输入框并输入邮件内容
    MouseController.move_cursor_with_offset(cur_pos1[0], cur_pos1[1], 20, 100)
    cur_pos2 = MouseController.get_cursor_position()
    MouseController.click_at(cur_pos2[0], cur_pos2[1], "left")
    KeyboardController.enter_text("This is a test email body.")
    time.sleep(2)
    
    # 9. 复制邮件正文并获取剪贴板内容
    KeyboardController.perform_hotkey_action("ctrl", "a", result_type="none")
    clipboard_content = KeyboardController.perform_hotkey_action("ctrl", "c", result_type="clipboard")
    
    # 10. 捕获准备发送邮件的屏幕并保存截图
    send_mail_screenshot = screen.capture()
    screen.record_screen_snapshot(send_mail_screenshot, f"send_mail_screen.png")
    
    # 11. 定位并点击发送按钮
    thunder_template = image_matcher.load_image_file(f"send.png")
    locations = image_matcher.find_template_locations(send_mail_screenshot, thunder_template)
    filter_location = image_matcher.filter_nearby_matches(locations, 10)
    draw_window = image_matcher.draw_matches(send_mail_screenshot, filter_location)
    screen.record_screen_snapshot(draw_window, draw_image)
    
    local_position = filter_location[0].get("position")
    MouseController.move_cursor(local_position[0], local_position[1])
    MouseController.click_at(local_position[0], local_position[1], "left")

if __name__ == "__main__":
    send_mail()