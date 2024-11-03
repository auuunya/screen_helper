#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   config.py
@Desc    :   None
'''

# here put the import lib
import platform

class BaseConfig:
    system_name = platform.system()
    character = "\r\n" if system_name == "Windows" else "\n"
    spacing = "GBK" if system_name == "Windows" else "utf-8"
    scale_factor = 1 if system_name == "Windows" else 2
    threshold = 0.8
    debug = False

    @classmethod
    def enable_debug(cls):
        """
        启用调试模式，将调试标志设置为 True。
        """
        cls.debug = True

    @classmethod
    def disable_debug(cls):
        """
        禁用调试模式，将调试标志设置为 False。
        """
        cls.debug = False

    @classmethod
    def set_scale_factor(cls, factor):
        """
        设置缩放因子
        :param factor: 缩放因子值
        """
        cls.scale_factor = factor

    @classmethod
    def set_threshold(cls, threshold):
        """
        设置匹配阈值
        :param threshold: 匹配的阈值
        """
        cls.threshold = threshold