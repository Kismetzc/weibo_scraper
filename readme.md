以下readme由Github自动生成
## 项目简介

本项目旨在爬取《再见爱人4》六位嘉宾各一条热门微博的评论，生成词云图，使用Python编写，主要依赖于`pandas`、`jieba`、`matplotlib`和`wordcloud`等库。通过读取CSV文件中的文本数据，进行分词处理，过滤停用词，统计词频，并最终生成词云图。

## 依赖库

请确保已安装以下Python库：

- pandas
- jieba
- matplotlib
- wordcloud

可以使用以下命令安装所需库：

```bash
pip install pandas jieba matplotlib wordcloud
```

## 使用方法

1. **准备输入文件**：将需要处理的文本数据保存为CSV文件，确保文件中包含名为`text_raw`的列，该列存储需要生成词云的文本数据。

2. **准备停用词**：在指定目录下放置停用词文件，每个文件包含一行一个停用词。

3. **运行脚本**：使用以下命令运行脚本，生成词云图。

```bash
python wordcloud_generate.py --input_csv <输入CSV文件路径> --output_image <输出图片路径> --stopwords_dir <停用词目录> --custom_stopwords <自定义停用词> --font_path <字体文件路径>
```

示例：

```bash
python wordcloud_generate.py --input_csv data/input.csv --output_image output/wordcloud.png --stopwords_dir stopwords/ --custom_stopwords "的,了,和" --font_path fonts/simhei.ttf
```

## 参数说明

- `--input_csv`：输入的CSV文件路径，包含需要处理的文本数据。
- `--output_image`：输出的词云图片路径。
- `--stopwords_dir`：停用词目录，包含多个停用词文件。
- `--custom_stopwords`：自定义停用词，多个停用词用逗号分隔。
- `--font_path`：字体文件路径，用于生成词云图的字体。

## 示例

以下是一个简单的示例，展示如何使用本项目生成词云图：

```python
import pandas as pd
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import os
import logging
from utils import setup_logger

# 省略代码...

# 生成词云
generate_wordcloud('data/input.csv', 'output/wordcloud.png', 'stopwords/', ['的', '了', '和'], 'fonts/simhei.ttf')
```

## 许可证

本项目使用MIT许可证，详情请参阅`LICENSE`文件。