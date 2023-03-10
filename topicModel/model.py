#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time  : 2022/8/31 15:58
# @Email: jtyoui@qq.com
import os
import time
from tqdm import tqdm
import pandas as pd
from gensim import corpora, models
from .tool import cal_perplexity
from gensim.models.coherencemodel import CoherenceModel
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


class TopicModel:
    def __init__(self, topics_range: (int, int), content: list, model_dir: str):
        """ 初始化主题模型

        :param topics_range: 主题数量的范围
        :param content: 预处理数据
        :param model_dir: 保存模型的文件夹路径
        """
        text = []
        uuid = []
        for line in content:
            text.append(line["text"])
            uuid.append(line["id"])
        self.text = text
        self.id = uuid
        dictionary = corpora.Dictionary(text)
        corpus = [dictionary.doc2bow(c) for c in text]
        self.topics_range = topics_range
        self.dictionary = dictionary
        self.corpus = corpus
        self.model_dir = model_dir

        self.models = []
        if not os.path.exists(model_dir):
            os.mkdir(model_dir)

        # 选择模型
        self.model = models.LdaMulticore

        self.log = open(os.path.dirname(self.model_dir) + "/log.txt", "a", encoding="utf-8")

        self.line = []
        with open(os.path.dirname(self.model_dir) + "/log.txt", "r", encoding="utf-8") as fp:
            for i in fp:
                self.line.append(i.strip())

    def get_score(self, x) -> float:
        for line in self.line:
            if line.startswith(x):
                return float(line[len(x) + 1:])

        return -1

    # 构建不同主题数的模型，并暂时保存，以便后续选择最优主题数
    def choose_topic(self):
        for i in range(self.topics_range[0], self.topics_range[1] + 1):
            print(f"开始训练第{i}模型")
            path = f"{self.model_dir}/lda_{i}.model"
            if os.path.exists(path):
                model = self.model.load(path)
            else:
                start = time.time()
                model = self.model(self.corpus,
                                   id2word=self.dictionary,
                                   num_topics=i,
                                   passes=20,
                                   iterations=500,
                                   minimum_probability=0.0,
                                   random_state=100,
                                   chunksize=1000)
                model.save(path)
                self.log.write(f'目前的topic个数:{i},花费时间：{time.time() - start}\n')
                self.log.flush()
            self.models.append(model)
        print("训练模型完毕！")

    # 困惑度作图。越小越好，一般选择转折点
    def perplexity_visible_model(self):
        x_list = []
        y_list = []
        for i, lda in enumerate(self.models, self.topics_range[0]):
            line = f"第{i}个困惑度得分"
            score = self.get_score(line)
            if score == -1:
                score = cal_perplexity(lda, i, self.corpus, self.dictionary)
                log = f"{line}:{score}\n"
                self.log.write(log)
                self.log.flush()
            x_list.append(i)
            y_list.append(score)
            log = f"{line}:{score}\n"
            print(log)
        plt.plot(x_list, y_list, color='k')
        plt.xlabel('主题数量(K)')
        plt.ylabel('困惑度得分')
        plt.legend('困惑度数值', loc='best')
        plt.savefig(os.path.dirname(self.model_dir) + "/困惑度图.jpg")

    # 一致性作图。越大越好。主题一致性是衡量给定主题模型的人类可解释性的有用度量
    def coherence_visible_model(self):
        plt.cla()
        x_list = []
        y_list = []
        for i, m in enumerate(self.models, self.topics_range[0]):
            line = f"第{i}个模型的C_V一致性为"
            score = self.get_score(line)
            if score == -1:
                cv = CoherenceModel(model=m,
                                    texts=self.text,
                                    dictionary=self.dictionary,
                                    coherence='u_mass')
                score = cv.get_coherence()
                log = f"{line}:{score}\n"
                self.log.write(log)
                self.log.flush()
            log = f"{line}:{score}\n"
            print(log)
            x_list.append(i)
            y_list.append(score)
        plt.plot(x_list, y_list, color='k')
        plt.xlabel('主题数量(K)')
        plt.ylabel('一致性得分')
        plt.legend('一致性数值', loc='best')
        plt.savefig(os.path.dirname(self.model_dir) + "/一致性图cv.jpg")

    def exec_lda(self, k: int, out_path: str):
        """ 执行选择主题模型的个数(K)

        :param k:  主题个数
        :param out_path: 保存Excel信息的路径
        :return:
        """
        path = f"{self.model_dir}/lda_{k}.model"

        assert os.path.exists(path), "模型文件不存在，请先训练模型"

        lda = self.model.load(path)
        sheet1, sheet2 = [], []

        for index in range(k):
            topics = lda.show_topic(index, topn=20)  # ***可修改，展示主题的前多少个词***
            t = '、'.join('%.3f* %s' % (v, k) for k, v in topics)
            w = [word for word, _ in topics]
            sheet1.append({"序号": index, "主题": t, "单词": w})

        topics = lda.get_document_topics(self.corpus, per_word_topics=True)

        for i, (doc_topics, word_topics, _) in enumerate(tqdm(topics, desc="打印主题")):
            m = {f"topic_{j}": frequency for j, frequency in doc_topics}
            max_info = max(doc_topics, key=lambda x: x[1])
            m["主题"] = f"topic_{max_info[0]}"
            m["概率"] = max_info[1]
            m["单词"] = self.text[i]
            m["id"] = self.id[i]
            sheet2.append(m)

        with pd.ExcelWriter(out_path) as xlsx:
            pd.DataFrame(sheet2).to_excel(xlsx, index=False, sheet_name="主题统计")
            pd.DataFrame(sheet1).to_excel(xlsx, index=False, sheet_name="主题频率")
