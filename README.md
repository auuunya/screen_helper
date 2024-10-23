# ScreenHelper

![Project Status](https://img.shields.io/badge/status-in%20development-orange.svg)

ScreenHelper 是一个基于图像识别的自动化工具，旨在通过截图和图像匹配等技术，提供用户界面的自动化操作。该工具支持文本识别、鼠标控制、键盘输入等功能，适用于各种自动化任务。

> **注意**: 该项目仍在开发中，可能会有不稳定的功能和未实现的特性。请随时关注更新。

### v0.1.0

- 首次发布
- 项目仍在开发中，欢迎提出问题和建议。


## 特性

- **屏幕截图**: 轻松捕获屏幕或指定区域的截图。
- **图像匹配**: 通过模板图像查找指定图像位置。
- **文本识别**: 支持在图像中查找文本内容。
- **鼠标和键盘控制**: 通过模拟用户操作进行自动化。
- **灵活的配置**: 可调整参数以满足特定需求。

## 安装

请确保已安装以下第三方库：

```bash
pip install numpy opencv-python pyautogui pillow
```

# 使用方法

## 初始化

```python
from screen_helper import ScreenHelper
screen_helper = ScreenHelper(scale_factor=1.0, threshold=0.8, debug=True)
```

## 示例

```python
screen_helper = ScreenHelper()
# 运行一个单独的操作
action = {
    'type': 'screenshot',
    'params': {
        'screenshot_file': 'screenshot.png',
    }
}
result = screen_helper.run_single_action(action)
print(result)

# 运行队列任务
screenshots_dir = os.path.join(os.getcwd(), "/screenshots")
templates_dir = os.path.join(os.getcwd(), "/templates")
screen_helper.set_scale_factor(2)
screen_helper.enable_debug()
screen_helper.create_screenshot_directory("screenshots")
actions = [
    {
        "type": "screenshot",
        "params": {
            "screenshot_file": f"{screenshots_dir}/bdark_screenshot.png",
        }
    },
    {
        "type": "find_image",
        "params": {
            "src_image": f"{screenshots_dir}/bdark_screenshot.png",
            "target_image": f"{templates_dir}/bdark_window_title.png"
        }
    },
    {
        "type": "mouse",
        "params": {
            "operation": "move",
        }
    },
    {
        "type": "mouse",
        "params": {
            "operation": "click",
            "mouse_click_action": "left"
        }
    }, 
    {
        "type": "mouse",
        "params": {
            "operation": "click",
            "mouse_click_action": "double"
        }
    },
    {
        "type": "send_text",
        "params": {
            "text": "Test ScreenHelper"
        }
    },
    {
        "type": "send_hotkey",
        "params": {
            "execute_identifier": "copy_username",
            "hot_keys": ("ctrl", "c")
        }
    },
]
try:
    screen_helper.run_action_queue(actions)
    username = screen_helper.get_execute_result("copy_username", "result.copy_name")
    print (f"username: {username})
except Exception as exce:
      raise (f"自动化操作出错: {str(exce)}")
```

# 感谢

感谢以下第三方库为本项目提供支持：
- [NumPy](https://numpy.org/) - 用于高效的数组操作。
- [OpenCV](https://opencv.org/) - 用于图像处理和计算机视觉。
- [PyAutoGUI](https://pyautogui.readthedocs.io/) - 用于程序化地控制鼠标和键盘。
- [Pillow](https://python-pillow.org/) - 用于图像处理

# 贡献

欢迎任何形式的贡献！请提出问题、提交功能请求或直接提交拉取请求。
