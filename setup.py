from setuptools import setup, find_packages

setup(
    name='screen_helper',
    version='0.2.0',
    description='An automation tool based on image recognition',
    author='auuunya',
    author_email='zyy.im@outlook.com',
    url='https://github.com/auuunya/screen_helper',
    packages=find_packages(),
    install_requires=[
        'numpy', 'pyperclip', "opencv-python", "pyautogui", "mss", "pytesseract"
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
