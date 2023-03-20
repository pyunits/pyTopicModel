#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time  : 2023/3/20 9:50
# @Email: jtyoui@qq.com
from .config import Config
from .model import TopicModel
from .preprocess import preprocess_func
import argparse
import json
import os


def main():
    parser = argparse.ArgumentParser(description='输入主题模型需要的参数', usage="主题模型")
    parser.add_argument("-d", type=str, help="保存结果的文件夹", default="result", required=False)
    parser.add_argument("mode", choices=["train", "predict"], help="选择程序模式")

    train_arg = parser.add_argument_group("训练", "训练模型参数")
    train_arg.add_argument("-p", type=str, help="加载分析的数据路径", default="topic.xlsx", required=False)
    train_arg.add_argument("-a", type=str, help="摘要列名", default="abstract", required=False)
    train_arg.add_argument("-t", type=str, help="标题列名", default="title", required=False)
    train_arg.add_argument("-r", nargs=2, type=int, help="主题数取值范围：至少是1", default=[1, 50], required=False)

    predict_arg = parser.add_argument_group("预测", "预测模型参数")
    predict_arg.add_argument("-k", type=int, help="预测主题数", default=1, required=False)

    args = parser.parse_args()
    exe(args)


config = Config()


def exe(args):
    config.AbstractColumName = args.a
    config.TitleColumNane = args.t
    config.TopicsRange = args.r
    config.K = args.k

    dirs = os.path.abspath(args.d)
    config.DataPath = os.path.abspath(args.p)

    config.StopPath = os.path.join(os.path.dirname(__file__), "stopwords.txt")
    config.ModelDir = os.path.join(dirs, "model")
    config.PreprocessPath = os.path.join(dirs, "preprocess_words.txt")
    config.WordPath = os.path.join(dirs, "word_frequency.xlsx")
    config.PredictPath = os.path.join(dirs, "doc_lda.xlsx")

    if args.mode == 'train':
        print('进入训练模式')
        train()
    elif args.mode == 'predict':
        print('进入测试模式')
        predict()
    else:
        raise Exception("第一个参数错误：选择 train 和 predict")


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
    model.exec_lda(config.K, config.PredictPath)
