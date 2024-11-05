from setuptools import setup, find_packages

setup(
    name="stream-module",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "opencv-python",
        "streamlink"
    ],
    author="seongjae6751",
    author_email="seongjae1679@gmail.com",
    description="A package to capture frames from YouTube live streams and process drone video data.",
    url="https://github.com/seongjae6751/stream-module.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
