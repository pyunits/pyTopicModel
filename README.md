# pyTopicModel

使用Gensim框架，根据摘要（abstract）和标题（title）来实现主题算法

## 1、下载

    git clone https://github.com/pyunits/pyunits-topicmodel.git

## 2、使用

```text
> python .\main.py -h

usage: 主题模型

输入主题模型需要的参数

positional arguments:
  {train,predict}  选择程序模式

optional arguments:
  -h, --help       show this help message and exit
  -p P             加载分析的数据路径
  -a A             摘要列名
  -t T             标题列名
  -d D             保存结果的文件夹
  -r R R           主题数取值范围：至少是1
  -k K             预测主题数
```

### 3、训练模型

     python .\main.py train -p 专利-医学其他领域.xlsx -a abo -t tio -d data -r 10 67

### 4、预测LDA

    python .\main.py predict -p 专利-医学其他领域.xlsx -a abo -t tio -d data -k 40