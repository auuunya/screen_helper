#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   config.py
@Time    :   2024/10/23 15:32:50
@Author  :   auuu_nya 
@Desc    :   None
'''

# here put the import lib
import platform

system_name = platform.system()
character = "\r\n" if system_name == "Windows" else "\n"
spacing = "GBK" if system_name == "Windows" else "utf-8"

class BaseConfig:
    # 根据操作系统设置缩放因子和阈值
    scale_factor = 1 if system_name == "Windows" else 2
    threshold = 0.8

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