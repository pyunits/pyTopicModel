#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time  : 2022/8/31 15:21
# @Email: jtyoui@qq.com
import json
from typing import List
import pandas as pd
from collections import Counter
from .tool import word_cut
from .config import Config


def read_title_abstract(config: Config) -> list:
    """ 读取文本摘要和标题

    :param config: 配置文件
    :return: 返回数组：[标题.摘要,标题.摘要,标题.摘要]
    """
    df = pd.read_excel(config.DataPath)
    df.reset_index(inplace=True)
    ls = []
    for _, line in df.iterrows():
        title = line[config.TitleColumNane]
        abstract = line[config.AbstractColumName]
        if pd.isna(title):
            title = ""
        if pd.isna(abstract):
            abstract = ""
        ls.append({"text": title + " " + abstract, "id": line["index"]})
    return ls


def read_stop_table(stop_path: str) -> dict:
    """ 读取停用词
    :param stop_path: 停用词文件路径
    :return: 停用词信息
    """
    m = {}
    with open(stop_path, encoding="utf-8") as fp:
        for line in fp:
            m[line.strip()] = False
    return m


def save_word_count(word_path: str, word_count: List[tuple]):
    """ 保存词频信息,保存成Excel，[index,单词,词频]

    :param word_path: 词频文本保存路径
    :param word_count: 词频信息
    """
    ls = []

    for index, (key, value) in enumerate(word_count):
        ls.append({"单词": key, "词频": value})

    df = pd.DataFrame(ls)
    # 如果df为空，就不保存
    if df.empty:
        return

    # 当df的大小超过 65535 时，就保存65535行
    row = 65535
    if df.shape[0] > row:
        df = df.loc[:row, :]

    df.to_excel(word_path, index=False)


def preprocess_func(config: Config, stop_num: int = 3) -> list:
    """ 预处理文本函数
    :param stop_num: 停用词个数,默认是3
    :param config: 配置文件
    :return: 切词
    """
    text = read_title_abstract(config)
    m = read_stop_table(config.StopPath)
    cut = word_cut(text, m)
    words = [t for c in cut for t in c["text"]]
    count = Counter(words)
    preprocess = []

    for key, value in count.items():
        if value < stop_num and m.get(key, True):
            m[key] = False

    save_word_count(config.WordPath, count.most_common())

    for content in cut:
        values = [value for value in content["text"] if m.get(value, True)]
        preprocess.append({"text": values, "id": content["id"]})

    with open(config.PreprocessPath, "w", encoding="utf-8") as wp:
        json.dump(preprocess, wp, ensure_ascii=False, indent="\t")
    return preprocess
