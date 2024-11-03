#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_image_matcher.py
@Desc    :   None
'''

# here put the import lib
from core.defs import ScreenHelperDefs
from core.screen_capture import ScreenCapture
from core.image_matcher import ImageMatcher
import os

test_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)), "image")

def test_image_matches():
    # 创建ImageMatcher实例
    matcher = ImageMatcher(scale_factor=1.0, threshold=0.8)
    screen = ScreenCapture()
    s = screen.capture()
    screen.record_screen_snapshot(s, f"{test_dir}/screen_shot.png")
    temp = matcher.load_image_file(f"{test_dir}/template2.png")
    try:
        matches = matcher.find_template_locations(s, temp)
        print("匹配位置:", matches)
        drawr = matcher.draw_matches(s, matches)
        screen.record_screen_snapshot(drawr, f"{test_dir}/draw_template.png")
    except RuntimeError as e:
        print (f"e: {e}")

def test_image_match():
    matcher = ImageMatcher(scale_factor=1.0, threshold=0.8)
    screen = ScreenCapture()
    s = screen.capture()
    screen.record_screen_snapshot(s, f"{test_dir}/screen_shot.png")
    temp = matcher.load_image_file(f"{test_dir}/template2.png")

    c = [
        {
            ScreenHelperDefs.CONTEXT_TEMPLATE: f"{test_dir}/context1.png",
            ScreenHelperDefs.OFFSET: {"x": 50, "y": 500},
        },
        {
            ScreenHelperDefs.CONTEXT_TEMPLATE: f"{test_dir}/context2.png",
            ScreenHelperDefs.OFFSET: {"x": 50, "y": 300},
        },
    ]
    try:
        matches = matcher.find_template_with_contexts(s, temp, c, True)
        print (f"matches: {matches}")
        if matches:
            output_image_all = ImageMatcher.draw_match(s, matches)
            if "context_matches" in matches:
                output_image_context = ImageMatcher.draw_matches(output_image_all, matches["context_matches"])
            screen.record_screen_snapshot(output_image_context, f"{test_dir}/template_match_with_context.png")
        
    except RuntimeError as e:
        print (f"e: {e}")

if __name__ == "__main__":
    test_image_match()