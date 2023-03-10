#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time  : 2022/8/31 16:02
# @Email: jtyoui@qq.com
import math
import jieba
import nltk
import nltk.stem as ns
from tqdm import tqdm
from nltk.corpus import stopwords


def language_is_chinese(text: str) -> bool:
    """ 判断是否包含中文
    :param text: 文本
    :return: 返回 english 和 chinese
    """
    for ch in text:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


def word_cut(contents: list, stop_word: dict) -> list:
    """ 切词

    :param contents: 预处理文本
    :param stop_word: 停用词
    :return: 切词后的数组
    """
    words = []

    english_stop = stopwords.words("english")
    chinese_stop = stopwords.words("chinese")

    stop_map = {stop: False for stop in english_stop + chinese_stop}
    stop_map.update(stop_word)

    for content in tqdm(contents, desc="开始处理文本数据，包括切词和除去停用词"):
        words_list, filter_word, word_tags = [], [], []
        text = content["text"]
        language = language_is_chinese(text)

        if language:
            sent_list = jieba.cut(text, use_paddle=False, cut_all=False)
            words_list.extend(list(sent_list))
        else:
            sent_list = nltk.sent_tokenize(text.lower())
            for sent in sent_list:
                word_list = nltk.word_tokenize(text=sent)
                value = [word for word in word_list]
                words_list.extend(value)

        # 去掉停用词
        for word in words_list:
            if stop_map.get(word, True) and len(word) > 2 and (not word.isdigit()):
                if not word[0].isalnum():
                    word = word[1:]
                filter_word.append(word)

        # 还原词形
        morphology = ns.WordNetLemmatizer()
        word_tag = nltk.pos_tag(filter_word)

        replace = {}
        for word, tag in word_tag:
            if tag in ['NNS', 'NNPS']:
                lemma = morphology.lemmatize(word, pos='n')  # 将名词还原为单数形式
            elif tag in ['VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:
                lemma = morphology.lemmatize(word, pos='v')  # 将动词还原为原型形式
            else:
                continue  # 没有就跳过
            replace[word] = lemma
        value = [replace.get(word, word) for word in filter_word]
        words.append({"text": value, "id": content["id"]})

    return words


def cal_perplexity(model, num_topics, corpus, dictionary):
    prob_doc_sum = 0.0
    topic_word_list = []
    for topic_id in range(num_topics):
        topic_word = model.show_topic(topic_id, len(dictionary.keys()))
        dic = {}
        for word, probability in topic_word:
            dic[word] = probability
        topic_word_list.append(dic)
    doc_topics_ist = []
    for doc in corpus:
        doc_topics_ist.append(model.get_document_topics(doc, minimum_probability=0))

    test_word_num = 0
    for i in range(len(corpus)):
        prob_doc = 0.0
        doc = corpus[i]
        doc_word_num = 0
        for word_id, num in doc:
            prob_word = 0.0
            doc_word_num += num
            word = dictionary[word_id]
            for topic_id in range(num_topics):
                prob_topic = doc_topics_ist[i][topic_id][1]
                prob_topic_word = topic_word_list[topic_id][word]
                prob_word += prob_topic * prob_topic_word
            prob_doc += math.log(prob_word)  # p(d) = sum(log(p(w)))
        prob_doc_sum += prob_doc
        test_word_num += doc_word_num
    prep = math.exp(-prob_doc_sum / test_word_num)  # perplexity = exp(-sum(p(d)/sum(Nd))
    return prep
