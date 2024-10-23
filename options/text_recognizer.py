#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   text_recognizer.py
@Time    :   2024/10/23 15:37:24
@Author  :   auuu_nya 
@Desc    :   None
'''

# here put the import lib
import math
import json
from typing import List, Tuple, Dict, Any

import numpy as np
import pytesseract
class TextRecognizer:
    @staticmethod
    def extract_text(image: np.ndarray, lang: str = 'chi_sim+eng', custom_config: str = None) -> Dict[str, Any]:
        """
        从图像中提取文本，并返回 OCR 识别结果的字典。
        
        :param image: 输入图像 (numpy 数组)
        :param lang: 使用的语言代码 (默认为中文和英语)
        :param custom_config: 自定义配置，用于 Tesseract OCR (默认为 '--oem 3 --psm 6')
        :return: OCR 识别结果的字典
        custom_config:
            --oem 
                0: 采用最旧的单一模式（Legacy Tesseract + LSTM）。
                1: 采用 LSTM 引擎（默认为此模式）。
                2: 采用 Legacy Tesseract 引擎。
                3: 组合模式，使用 Legacy 和 LSTM 引擎。
            --psm
                0: 自动模式（默认模式）。
                1: 自动分割，但不进行 OCR。
                2: 执行完全自动化的页面分割，试图识别页面内容。
                3: 假设图像中只有一个列文本。
                4: 假设图像中有多个列文本。
                5: 假设图像中有多个列文本，但不需要进行自动化处理。
                6: 假设图像中有一行文本（适用于一行文本的情况）。
                7: 假设图像中只有单行文本。
                8: 识别单列文本，但不需要自动分割。
                9: 假设文本为水平格式。
                10: 假设文本为垂直格式。
                11: 假设文本为单词水平格式。
                12: 假设文本为单词垂直格式。
                13: 假设图像中只有单个字符。
            -l
                eng
                chi_sim
                chi_sim+eng
            -c
                tessedit_char_whitelist: 指定允许的字符集。
                tessedit_char_blacklist: 指定不允许的字符集。
                tessedit_pageseg_mode: 设置页面分割模式，控制图像中文本的布局。
                textord_min_linespace: 设置行间距的最小值。
                textord_space_size: 设置字符之间的间距。
                tessedit_enable_dict: 启用字典检查（默认启用）。
                tessedit_no_reject: 禁用拒绝的选择，强制输出结果。
                classify_bln_numeric_mode: 开启数字模式，优化数字识别。

                tessedit_ocr_engine_mode: 设置 OCR 引擎模式（OEM）。
                tessedit_page_seg_mode: 设置页面分割模式（PSM）。
                tessedit_use_new_state_cost: 使用新状态成本。
                tessedit_read_binary_image: 读取二进制图像。
                tessedit_debug_file: 指定调试输出文件。

                tessedit_create_hocr: 创建 hOCR 输出。
                hocr_font_size: 在 hOCR 输出中设置字体大小。
                tessedit_create_tsv: 创建 TSV 输出。
                savebox: 保存识别到的文本框信息。

                textord_heights: 控制文本行的高度。
                textord_heights_max: 最大行高。
                textord_heights_min: 最小行高。
                textord_heights_delta: 行高变化量。
                textord_kerning: 开启或禁用字间距调整。

                user_words: 用户自定义单词列表。
                user_patterns: 用户自定义模式列表。
                tessedit_create_pdf: 创建 PDF 输出。
                tessedit_write_images: 写入处理后的图像。
        """
        # 如果未提供自定义配置，则使用默认值
        if custom_config is None:
            custom_config = r'--oem 3 --psm 6'
        
        return pytesseract.image_to_data(image, lang=lang, config=custom_config, output_type=pytesseract.Output.DICT)

    @staticmethod
    def find_text_position(image: np.ndarray, 
                           target_text: str, 
                           lang: str = 'chi_sim+eng', 
                           custom_config: str = None, 
                           context_texts: List[str] = None, 
                           threshold: float = 10
                           ) -> List[Tuple[int, int, int, int]]:
        """
        查找图像中指定文本的位置，并通过多个上下文文本进行过滤
        
        :param image: 输入的图像
        :param target_text: 要查找的目标文本
        :param lang: OCR 语言代码，默认为中文和英语
        :param custom_config: 自定义配置，用于 Tesseract OCR
        :param context_texts: 上下文文本列表，用于辅助识别
        :param threshold: 允许的上下文距离阈值
        :return: 文本位置的坐标列表 (x, y, w, h)
        """
        positions = []
        target_lower = target_text.lower()
        data = TextRecognizer.extract_text(image, lang=lang, custom_config=custom_config)
        print (f"TextRecognizer extract data: {data}")
        # 查找目标文本
        for i, word in enumerate(data['text']):
            if target_lower in word.lower():
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                positions.append((x, y, w, h))

        # 如果找到多个位置，基于多个上下文进行进一步筛选
        if len(positions) > 1 and context_texts:
            filtered_positions = []
            for pos in positions:
                x, y, w, h = pos
                if any(TextRecognizer._is_context_near(data, context.lower(), x, y, w, h, threshold) for context in context_texts):
                    filtered_positions.append(pos)
            return filtered_positions

        return positions

    @staticmethod
    def _is_context_near(data: dict, context_text: str, x: int, y: int, width: int, height: int, threshold: float) -> bool:
        """
        检查某个上下文文本是否在指定坐标附近
        
        :param data: OCR 识别结果的字典
        :param context_text: 上下文文本
        :param x: 当前文本块的 x 坐标
        :param y: 当前文本块的 y 坐标
        :param width: 当前文本块的宽度
        :param height: 当前文本块的高度
        :param threshold: 允许的距离阈值
        :return: 如果上下文文本在指定坐标附近则返回 True，否则返回 False
        """
        if not context_text:
            return False
        context_lower = context_text.lower()
        current_center = (x + 0.5 * width, y + 0.5 * height)

        for i, word in enumerate(data['text']):
            if context_lower in word.lower():
                cx, cy = data['left'][i], data['top'][i]
                word_width, word_height = data['width'][i], data['height'][i]
                context_center = (cx + 0.5 * word_width, cy + 0.5 * word_height)
                distance = math.sqrt((current_center[0] - context_center[0]) ** 2 + (current_center[1] - context_center[1]) ** 2)
                if distance < threshold:
                    return True
        return False