#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.image_matcher import ImageMatcher
from core import utils

template_dir = os.path.join("X:\\tests", "templates")
def test_image_matches():
    scale_factor = 1
    image_matche_manager = ImageMatcher()
    root = utils.load_entity_file(f"{template_dir}/screenshot.png")
    resize_root = utils.resize_entity(root, scale=scale_factor)
    template = utils.load_entity_file(f"{template_dir}/template.png")
    resize_template = utils.resize_entity(template, scale=scale_factor)
    locations = image_matche_manager.find_template_locations(
        original_image=root,
        original_template=template,
        resized_image=resize_root,
        resized_template=resize_template,
        threshold=0.8
    )
    ctx_list = []
    ctx_file_list = [
        {
            "template": f"{template_dir}/ctx1.png",
            "offset": {
                "x": 30,
                "y": 280
            }
        },
        {
            "template": f"{template_dir}/ctx2.png",
            "offset": {
                "x": 700,
                "y": 500
            }
        }
    ]
    for ctx_file in ctx_file_list:
        temp = ctx_file.get("template")
        offset = ctx_file.get("offset")
        context_template = utils.load_entity_file(temp)
        context_template_resize = utils.resize_entity(context_template, scale=scale_factor)
        ctx_matches = image_matche_manager.find_template_locations(
            original_image=root,
            original_template=context_template,
            resized_image=resize_root,
            resized_template=context_template_resize,
            threshold=0.8
        )
        _ = [ctx.update({"offset": offset}) for ctx in ctx_matches]
        ctx_list.append(ctx_matches)
    matches = image_matche_manager.match_template_with_contexts(
        locations,
        ctx_list,
        all_matching=True
    )
    print (f"matches: {matches}")
    drawed = utils.draw_matches(root, matches)
    context_matches = matches[0]["context_matches"]
    if context_matches:
        context_matches_draw = utils.draw_matches(drawed, [item for sublist in context_matches for item in sublist], (0,0,255))
        utils.record_snapshot(context_matches_draw, f"{template_dir}/image_matcher_drawed.png")
if __name__ == "__main__":
    test_image_matches()