# ScreenHelper

![Project Status](https://img.shields.io/badge/status-in%20development-orange.svg)

ScreenHelper 是一个基于图像识别的自动化工具，旨在通过截图和图像匹配等技术，提供用户界面的自动化操作。该工具支持文本识别、鼠标控制、键盘输入等功能，适用于各种视觉自动化任务,可灵活编排。

> **注意**: 该项目仍在开发中，可能会有不稳定的功能和未实现的特性。请随时关注更新。由于当前仍在开发周期，且未经过大量测试，此项目不能在生产环境中使用。

### 当前版本: v0.1.1

- 首次发布
- 项目仍在开发中，欢迎提出问题和建议。

## 特性

- **屏幕截图**: 轻松捕获屏幕或指定区域的截图。
- **图像匹配**: 通过模板图像查找指定图像位置,也可添加上下文使识别更准确。
- **文本识别**: 支持在图像中查找文本内容，可自行添加其他ocr。
- **鼠标和键盘控制**: 通过模拟用户操作进行自动化。
- **灵活的配置**: 可调整参数以满足特定需求。

## 安装

请确保已安装以下第三方库：

```bash
pip install numpy opencv-python pyautogui pillow pytesseract
```

## 使用方法
#### 请查看 examples 与 tests 文件夹中的示例脚本，了解如何使用 ScreenHelper 进行自动化任务。

## 感谢
#### 感谢以下第三方库为本项目提供支持：

- [NumPy](https://numpy.org/) - 用于高效的数组操作。
- [OpenCV](https://opencv.org/) - 用于图像处理和计算机视觉。
- [PyAutoGUI](https://pyautogui.readthedocs.io/) - 用于程序化地控制鼠标和键盘。
- [Pillow](https://python-pillow.org/) - 用于图像处理。
- [Tesseract](https://github.com/tesseract-ocr/tesseract) - 用于文本识别


## 贡献
#### 欢迎任何形式的贡献！请提出问题、提交功能请求或直接提交拉取请求.