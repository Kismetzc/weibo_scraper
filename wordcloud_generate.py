import pandas as pd
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import os
import logging
from utils import setup_logger


def load_stopwords(stopwords_dir, custom_stopwords, logger=None):
    stopwords = set()
    if logger is None:
        logger = setup_logger()

    # 遍历 stopwords 目录下的所有 .txt 文件
    if os.path.exists(stopwords_dir) and os.path.isdir(stopwords_dir):
        for filename in os.listdir(stopwords_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(stopwords_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line in f:
                            stopword = line.strip()
                            if stopword:
                                stopwords.add(stopword)
                    logger.info(f"加载停用词文件: {filepath}")
                    print(f"加载停用词文件: {filepath}")
                except Exception as e:
                    logger.error(f"加载停用词文件 {filepath} 时出错: {e}")
                    print(f"加载停用词文件 {filepath} 时出错: {e}")
    else:
        logger.warning(f"停用词目录不存在或不是目录: {stopwords_dir}")
        print(f"停用词目录不存在或不是目录: {stopwords_dir}")

    # 添加自定义停用词
    stopwords.update(set(custom_stopwords))
    logger.info(f"已加载停用词，共计 {len(stopwords)} 个停用词。")
    print(f"已加载停用词，共计 {len(stopwords)} 个停用词。")
    return stopwords


def process_text(text_series, stopwords, logger=None):
    words = []
    if logger is None:
        logger = setup_logger()
    for text in text_series:
        if pd.isna(text):
            continue
        # 使用精确模式进行分词
        seg_list = jieba.cut(str(text), cut_all=False)
        for word in seg_list:
            word = word.strip()
            if word and word not in stopwords and len(word) > 1:
                words.append(word)
    logger.info(f"分词完成，共提取 {len(words)} 个词。")
    print(f"分词完成，共提取 {len(words)} 个词。")
    return words


def generate_wordcloud_from_frequencies(frequencies, font_path, output_image, logger=None):
    if logger is None:
        logger = setup_logger()
    wc = WordCloud(
        font_path=font_path,
        width=800,
        height=600,
        background_color='white',
        max_words=200,
        max_font_size=100,
        random_state=42,
        collocations=False
    ).generate_from_frequencies(frequencies)

    # 显示词云
    plt.figure(figsize=(10, 8), facecolor='white')
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.show()

    # 保存词云到文件
    wc.to_file(output_image)
    logger.info(f"词云已保存到 {output_image}")
    print(f"词云已保存到 {output_image}")


def generate_wordcloud(input_csv, output_image, stopwords_dir, custom_stopwords, font_path, logger=None):
    if logger is None:
        logger = setup_logger()

    logger.info(f"开始生成词云：输入文件={input_csv}, 输出文件={output_image}")
    print(f"开始生成词云：输入文件={input_csv}, 输出文件={output_image}")

    # 读取清洗后的CSV文件
    try:
        df = pd.read_csv(input_csv, encoding='utf-8-sig')
    except Exception as e:
        logger.error(f"读取CSV文件时出错: {e}")
        print(f"读取CSV文件时出错: {e}")
        return

    # 加载停用词
    stopwords = load_stopwords(stopwords_dir, custom_stopwords, logger)

    # 分词处理
    words = process_text(df['text_raw'], stopwords, logger)

    # 统计词频
    word_counter = Counter(words)

    # 生成词云
    generate_wordcloud_from_frequencies(word_counter, font_path, output_image, logger)
