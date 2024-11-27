import platform
class BaseConfig:
    system_name = platform.system()
    character = "\r\n" if system_name == "Windows" else "\n"
    spacing = "GBK" if system_name == "Windows" else "utf-8"
    scale_factor = 1 if system_name == "Windows" else 2
    debug = False
    threshold = 0.8

    @classmethod
    def state_debug(cls, enable: bool = False):
        """
        启用调试模式，将调试标志设置为 True。
        """
        cls.debug = enable

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

