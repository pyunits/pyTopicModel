#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time  : 2023/3/10 11:19
# @Email: jtyoui@qq.com

class Config:
    TopicsRange: (int, int)  # 主题范围
    PreprocessPath: str  # 预测文件路径
    AbstractColumName: str  # 摘要列名
    TitleColumNane: str  # 标题列名
    DataPath: str  # 加载数据源的文本路径
    StopPath: str  # 停用词文件路径
    ModelDir: str  # 模型保存的路径
    WordPath: str  # 词频文件路径
    PredictPath: str  # 预测出来结果保存的路径
    K: int  # 主题数
