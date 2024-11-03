#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_image_matcher.py
@Desc    :   None
'''

# here put the import lib
from core import ScreenCapture
from core import TextRecognizer
from core import OCRRecognizer
import os
test_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)), "image")

def test_text_matches():
    # 创建ImageMatcher实例
    texter = TextRecognizer()
    screen = ScreenCapture()
    s = screen.capture()
    screen.record_screen_snapshot(s, f"{test_dir}/screen_shot.png")
    ocr_engine = OCRRecognizer(ocr_engine="tesseract", lang='eng', config=r'--oem 3 --psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ& ')
    result = ocr_engine.recognize_text(s)
    matches = texter.find_all_text_positions(result, "turnon")
    output_image_all = TextRecognizer.draw_matches(s, matches)
    screen.record_screen_snapshot(output_image_all, f"{test_dir}/temp.png")

def test_image_match():
    texter = TextRecognizer()
    screen = ScreenCapture()
    s = screen.capture()
    screen.record_screen_snapshot(s, f"{test_dir}/screen_shot.png")
    ocr_engine = OCRRecognizer(ocr_engine="tesseract", lang='eng', config=r'--oem 3 --psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ& ')
    result = ocr_engine.recognize_text(s)
    contexts = [
        {
            "text": "Devicesecurity",
            "offset": {
                "x": 100,
                "y": 300
            }
        },
        {
            "text": "App",
            "offset": {
                "x": 100,
                "y": 300
            }
        },
    ]
    matches = texter.find_text_position(result, "turnon", contexts)
    # print (f"matches: {matches}")
    if matches:
        output_image_all = TextRecognizer.draw_match(s, matches)
        if "context_matches" in matches:
            output_image_context = TextRecognizer.draw_matches(output_image_all, matches["context_matches"])
        screen.record_screen_snapshot(output_image_context, f"{test_dir}/text_match_context.png")

if __name__ == "__main__":
    test_image_match()