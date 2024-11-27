# ScreenHelper

![Project Status](https://img.shields.io/badge/status-in%20development-orange.svg)

ScreenHelper is an automation tool based on image recognition, designed to provide automated user interface operations through techniques such as screenshotting and image matching. This tool supports text recognition, mouse control, keyboard input, and is suitable for various visual automation tasks, allowing for flexible orchestration.

> **Note**: This project is still in development and may contain unstable features and unimplemented characteristics. Please stay tuned for updates. Due to the current development phase and lack of extensive testing, this project should not be used in production environments.

### Current Version: v0.1.2

- Initial release
- The project is still under development; feedback and suggestions are welcome
- Modify the code structure to add the windows window manager class

## Features

- **Screenshot Capture**: Easily capture screenshots of the entire screen or specific areas.
- **Image Matching**: Locate specified image positions using template images, and add context for more accurate recognition.
- **Text Recognition**: Support finding text within images and the ability to add other OCR options.
- **Mouse and Keyboard Control**: Automate operations by simulating user actions.
- **Flexible Configuration**: Adjustable parameters to meet specific needs.

## Installation

Please ensure that the following third-party libraries are installed:

```bash
pip install numpy opencv-python pyautogui pillow pytesseract
```

## Usage
#### Please check the examples and tests folders for sample scripts on how to use ScreenHelper for automation tasks.

## Acknowledgements
#### Thanks to the following third-party libraries that support this project:
- [NumPy](https://numpy.org/) - For efficient array operations.
- [OpenCV](https://opencv.org/) - For image processing and computer vision.
- [PyAutoGUI](https://pyautogui.readthedocs.io/) - For programmatic control of the mouse and keyboard.
- [Pillow](https://python-pillow.org/) - For image processing.
- [Tesseract](https://github.com/tesseract-ocr/tesseract) - For text recognition.

## Contribution
#### Contributions of any form are welcome! Please raise issues, submit feature requests, or create pull requests.