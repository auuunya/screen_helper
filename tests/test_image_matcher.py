#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.image_matcher import ImageMatcher
from core.toolkit import GraphicToolkit
from core import utils

template_dir = os.path.join("X:\\tests", "templates")
def test_image_matches():
    scale_factor = 1
    image_matche_manager = ImageMatcher()
    root = GraphicToolkit(f"{template_dir}/screenshot.png")
    resize_root = root.resize_entity(scale=scale_factor)
    template = GraphicToolkit(f"{template_dir}/template.png")
    resize_template = template.resize_entity(scale=scale_factor)
    locations = image_matche_manager.find_template_locations(
        original_image=root.get_entity(),
        original_template=template.get_entity(),
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
        context_template = GraphicToolkit(temp)
        context_template_resize = context_template.resize_entity(scale=scale_factor)
        ctx_matches = image_matche_manager.find_template_locations(
            original_image=root.get_entity(),
            original_template=context_template.get_entity(),
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
    for match in matches:
        drawed = utils.draw_shape(
            root.get_entity(), 
            "rectangle", 
            position=(
                int(match["position"][0] - (match["dimensions"][0] / 2)),
                int(match["position"][1] - (match["dimensions"][1] / 2)),
            ),
            size=match["dimensions"],
        )
        context_matches = matches[0]["context_matches"]
        if context_matches:
            drawed = utils.draw_shapes(
                drawed, 
                ['rectangle'] * sum(len(group) for group in context_matches),
                [
                    (int(match["position"][0] - (match["dimensions"][0] / 2)), 
                    int(match["position"][1] - (match["dimensions"][1] / 2)))
                    for match_group in context_matches for match in match_group
                ],
                [
                    match["dimensions"] for match_group in context_matches for match in match_group
                ],
                border_color=(0, 0, 255)
            )
            utils.record_snapshot(drawed, f"{template_dir}/image_matcher_drawed.png")
if __name__ == "__main__":
    test_image_matches()