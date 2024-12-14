import pytesseract
from typing import Any, Dict, Union
import numpy as np
from pytesseract import Output

class BaseOCR:
    """
    Abstract base class for Optical Character Recognition (OCR) implementations. 
    Provides methods for recognizing text and formatting the results.
    """

    def recognize_text(self, image: np.ndarray, resized_image: np.ndarray = None) -> Union[Dict[str, Any], str]:
        """
        Recognize text content in an image.
        
        :param image: The image to be processed, in NumPy array format.
        :param resized_image: The resized image (if any), defaults to None.
        :return: Recognition result, which can be a dictionary or a string, depending on the implementation.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")

    def format_result(self, raw_result: Any) -> Dict[str, Any]:
        """
        Format the raw OCR result into a dictionary format.
        
        :param raw_result: The raw result returned by the OCR engine.
        :return: A formatted result as a dictionary.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")


class TesseractOCR(BaseOCR):
    """
    Tesseract OCR implementation of the BaseOCR class. 
    Allows text recognition using Tesseract with configurable options.
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize the TesseractOCR with optional configuration parameters.
        
        :param kwargs: Configuration parameters for Tesseract OCR, such as `lang`, `config`, etc.
        """
        self.kwargs = kwargs

    def recognize_text(self, original_image: np.ndarray, resized_image: np.ndarray = None) -> Dict[str, Any]:
        """
        Use Tesseract to recognize text from the given image.
        
        :param original_image: The original image to be processed.
        :param resized_image: The resized image (if any), defaults to None.
        :return: The formatted OCR recognition result as a dictionary.
        """
        if 'output_type' not in self.kwargs:
            self.kwargs['output_type'] = Output.DICT

        # If resized_image is not provided, use the original image for OCR
        if resized_image is None:
            raw_result = pytesseract.image_to_data(original_image, **self.kwargs)
        else:
            scale_factor = self._compute_scale_factor(original_image, resized_image)
            raw_result = pytesseract.image_to_data(resized_image, **self.kwargs)

            # Adjust coordinates if resizing was done
            raw_result = self._adjust_coordinates_to_original(raw_result, scale_factor)
        
        return self.format_result(raw_result)

    def _compute_scale_factor(self, original_image: np.ndarray, resized_image: np.ndarray) -> float:
        """Compute the scale factor between the original and resized image."""
        original_height, original_width = original_image.shape[:2]
        resized_height, resized_width = resized_image.shape[:2]
        return resized_width / original_width

    def _adjust_coordinates_to_original(self, raw_result: Any, scale_factor: float) -> Any:
        """Adjust the coordinates of OCR results based on the scale factor."""
        for i in range(len(raw_result['text'])):
            raw_result['left'][i] = int(raw_result['left'][i] / scale_factor)
            raw_result['top'][i] = int(raw_result['top'][i] / scale_factor)
            raw_result['width'][i] = int(raw_result['width'][i] / scale_factor)
            raw_result['height'][i] = int(raw_result['height'][i] / scale_factor)
        return raw_result

    def format_result(self, raw_result: Any) -> Dict[str, Any]:
        """
        Format the raw result returned by Tesseract into a dictionary format.
        
        :param raw_result: The raw result returned by the OCR engine.
        :return: A formatted result as a dictionary.
        """
        return {
            **raw_result,
        }


class OCRFactory:
    """
    A factory class for creating OCR engine instances.
    Supports multiple OCR engines with extensibility for additional engines.
    """
    _ocr_engines = {
        "tesseract": TesseractOCR,
        # Additional OCR engines can be added here.
    }

    @staticmethod
    def create_ocr_engine(ocr_engine: str = 'tesseract', **kwargs: Any) -> BaseOCR:
        """
        Create an instance of the specified OCR engine.
        
        :param ocr_engine: The name of the OCR engine, defaults to 'tesseract'.
        :param kwargs: Additional parameters for the OCR engine.
        :return: An instance of the specified OCR engine.
        :raises ValueError: If the specified OCR engine is not supported.
        """
        if ocr_engine not in OCRFactory._ocr_engines:
            raise ValueError(f"Unsupported OCR engine: {ocr_engine}")
        return OCRFactory._ocr_engines[ocr_engine](**kwargs)


class OCRRecognizer:
    """
    A high-level recognizer class for handling OCR tasks using a specified OCR engine.
    """

    def __init__(self, ocr_engine: str = 'tesseract', **kwargs: Any) -> None:
        """
        Initialize the OCR recognizer with the specified OCR engine.
        
        :param ocr_engine: The name of the OCR engine, defaults to 'tesseract'.
        :param kwargs: Additional parameters for the OCR engine.
        """
        self.ocr = OCRFactory.create_ocr_engine(ocr_engine, **kwargs)

    def recognize_text(self, original_image: np.ndarray, resized_image: np.ndarray = None) -> Dict[str, Any]:
        """
        Recognize text from the given image using the configured OCR engine.
        
        :param original_image: The original image to be processed.
        :param resized_image: The resized image (if any), defaults to None.
        :return: The OCR recognition result as a dictionary.
        """
        return self.ocr.recognize_text(original_image, resized_image)
