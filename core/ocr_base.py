from typing import Dict, Any, Union
import numpy as np
import pytesseract
from pytesseract import Output

class BaseOCR:
    def recognize_text(self, image: np.ndarray) -> Union[Dict[str, Any], str]:
        """识别图像中的文本内容。
        
        :param image: 需要识别的图像，格式为 NumPy 数组
        :return: 识别结果，可以是字典或者字符串，具体取决于实现
        """
        raise NotImplementedError("This method should be overridden by subclasses.")

    def format_result(self, raw_result: Any) -> Dict[str, Any]:
        """格式化识别结果为字典格式。
        
        :param raw_result: OCR 引擎返回的原始结果
        :return: 格式化后的结果，字典格式
        """
        raise NotImplementedError("This method should be overridden by subclasses.")


class TesseractOCR(BaseOCR):
    def __init__(self, **kwargs: Any) -> None:
        """TesseractOCR 初始化，接受参数用于配置 Tesseract OCR。
        
        :param kwargs: Tesseract OCR 的配置参数，例如 `lang`, `config` 等
        """
        self.kwargs = kwargs

    def recognize_text(self, image: np.ndarray) -> Dict[str, Any]:
        """使用 Tesseract 识别图像中的文本。
        
        :param image: 要识别的图像，NumPy 数组格式
        :return: 格式化后的 OCR 识别结果，字典格式
        """
        if 'output_type' not in self.kwargs:
            self.kwargs['output_type'] = Output.DICT
        raw_result = pytesseract.image_to_data(image, **self.kwargs)
        return self.format_result(raw_result)

    def format_result(self, raw_result: Any) -> Dict[str, Any]:
        """格式化 Tesseract 返回的原始结果为字典格式。
        
        :param raw_result: OCR 引擎返回的原始结果
        :return: 格式化后的结果，字典格式
        """
        return {
            **raw_result,
        }


class OCRFactory:
    _ocr_engines = {
        "tesseract": TesseractOCR,
        # add other OCR engine
    }

    @staticmethod
    def create_ocr_engine(ocr_engine: str = 'tesseract', **kwargs: Any) -> BaseOCR:
        """创建 OCR 引擎实例。
        
        :param ocr_engine: OCR 引擎名称，默认为 'tesseract'
        :param kwargs: OCR 引擎的额外参数
        :return: OCR 引擎的实例
        :raises ValueError: 如果指定的 OCR 引擎不受支持
        """
        if ocr_engine not in OCRFactory._ocr_engines:
            raise ValueError(f"Unsupported OCR engine: {ocr_engine}")
        return OCRFactory._ocr_engines[ocr_engine](**kwargs)


class OCRRecognizer:
    def __init__(self, ocr_engine: str = 'tesseract', **kwargs: Any) -> None:
        """OCR 识别器的初始化方法。
        
        :param ocr_engine: OCR 引擎名称，默认为 'tesseract'
        :param kwargs: OCR 引擎的额外参数
        """
        self.ocr = OCRFactory.create_ocr_engine(ocr_engine, **kwargs)

    def recognize_text(self, image: np.ndarray) -> Dict[str, Any]:
        """使用 OCR 引擎识别图像中的文本。
        
        :param image: 要识别的图像，NumPy 数组格式
        :return: OCR 识别结果，字典格式
        """
        return self.ocr.recognize_text(image)
