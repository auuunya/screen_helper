#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import time
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core import TextRec
from core import OCRRecognizer
from core import utils
from core import GraphicToolkit

templates = os.path.join("X:\\tests", "templates")
def test_image_match():
    textrec = TextRec()
    template = GraphicToolkit(f"{templates}/screenshot.png")
    resize_template = template.resize_entity(scale=2)
    ocr_engine = OCRRecognizer(ocr_engine="tesseract", lang='eng', config=r'--oem 3 --psm 6')
    result = ocr_engine.recognize_text(template.get_entity(), resize_template)
    target_text = textrec.generate_text_config(
        "Dismiss"
    )
    target_matches = textrec.find_matching_text_positions(result, target_text)

    context_text_sign = textrec.generate_text_config(
        "Sign",
        offset={"x": 100, "y": 100}
    )
    context_text_device = textrec.generate_text_config(
        "Device",
        offset={"x": 100, "y": 10}
    )
    contexts_matches = textrec.find_position_on_context(
            result,
            target_matches,
            [context_text_sign, context_text_device],
            require_all_matches=False
        )
    if not contexts_matches:
        print (f"Text Match failure!")
        return
    match = contexts_matches[0]
    print (f"match: {match}")
    drawed = utils.draw_shape(
        template.get_entity(), 
        "rectangle", 
        position=(
            int(match["position"][0] - (match["dimensions"][0] / 2)),
            int(match["position"][1] - (match["dimensions"][1] / 2)),
        ),
        size=match["dimensions"],
    )
    context_matches = contexts_matches[0]["context_matches"]
    shapes = []
    positions = []
    sizes = []
    for context_match in context_matches:
        shapes.append('rectangle')
        positions.append(
            (
                int(context_match["position"][0] - (context_match["dimensions"][0] / 2)),
                int(context_match["position"][1] - (context_match["dimensions"][1] / 2))
            )
        )
        sizes.append(context_match["dimensions"])
        drawed = utils.draw_shapes(
            drawed, 
            shapes,
            positions,
            sizes,
            border_color=(0, 0, 255)
        )
    utils.record_snapshot(drawed, f"{templates}/text_rec_drawed.png")

if __name__ == "__main__":
    test_image_match()