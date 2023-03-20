#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time  : 2023/3/20 9:49
# @Email: jtyoui@qq.com
from setuptools import setup, find_packages
import os

dirs = os.path.abspath(os.path.dirname(__file__))

with open(dirs + os.sep + 'README.md', encoding='utf-8') as f:
    long_text = f.read()

with open('requirements.txt', encoding='utf-8') as f:
    install_requires = f.read().strip().splitlines()

setup(
    name="topic",
    version="1.0.0",
    description="主题识别模型",
    long_description=long_text,
    long_description_content_type="text/markdown",
    url="https://github.com/pyunits/pyunit-prime",
    author="张伟",
    author_email="jtyoui@qq.com",
    license='MIT Licence',
    packages=find_packages(),
    platforms='any',
    package_data={"topicModel": ['*.py', '*.txt']},
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    zip_safe=False,
    entry_points={"console_scripts": ["topic = topicModel.cli:main"]}
)
