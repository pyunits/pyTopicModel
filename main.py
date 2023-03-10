#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time  : 2022/8/31 16:59
# @Email: jtyoui@qq.com
from topicModel import TopicModel, preprocess_func, Config
import json
import os
import argparse

config = Config()
parser = argparse.ArgumentParser(description='输入主题模型需要的参数')

config.AbstractColumName = "abstract"
config.TitleColumNane = "title"
config.IDColumName = "ID"

dirs = os.path.dirname(__file__)
config.SourceDir = os.path.join(dirs, "data")
config.DataPath = os.path.join(config.SourceDir, "基金—呼吸.xlsx")

config.StopPath = os.path.join(dirs, "stopwords.txt")
config.ModelDir = os.path.join(config.SourceDir, "model")
config.PreprocessPath = os.path.join(config.SourceDir, "preprocess_words.txt")
config.WordPath = os.path.join(config.SourceDir, "word_frequency.xlsx")
config.LdaPath = os.path.join(config.SourceDir, "doc_lda.xlsx")
config.TopicsRange = (10, 100)
Config.k = 135


# 训练
def train():
    if os.path.exists(config.PreprocessPath):
        with open(config.PreprocessPath, encoding="utf-8") as fp:
            content = json.load(fp)
    else:
        content = preprocess_func(config)
    model = TopicModel(config.TopicsRange, content, config.ModelDir)
    model.choose_topic()
    model.perplexity_visible_model()
    model.coherence_visible_model()


# 预测
def predict():
    with open(config.PreprocessPath, encoding="utf-8") as fp:
        content = json.load(fp)
    model = TopicModel(config.TopicsRange, content, config.ModelDir)
    model.exec_lda(config.K, config.LdaPath)


if __name__ == '__main__':
    train()  # predict()
