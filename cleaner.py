import pandas as pd
import logging
from utils import setup_logger

def clean_comments(input_file, output_file, condition_keywords, logger=None):
    if logger is None:
        logger = setup_logger()

    logger.info(f"开始清洗数据：输入文件={input_file}, 输出文件={output_file}")
    print(f"开始清洗数据：输入文件={input_file}, 输出文件={output_file}")

    # 读取原始CSV文件
    try:
        df = pd.read_csv(input_file, encoding='utf-8')
    except Exception as e:
        logger.error(f"读取CSV文件时出错: {e}")
        print(f"读取CSV文件时出错: {e}")
        return

    # 条件1：text_raw字段包含任意一个关键词
    condition_keywords_series = df['text_raw'].astype(str).str.contains('|'.join(condition_keywords), case=False, na=False)

    # 条件2：text_raw字段为空
    condition_empty_series = df['text_raw'].isnull() | (df['text_raw'].astype(str).str.strip() == '')

    # 合并两个条件，删除满足任意一个条件的行
    df_cleaned = df[~(condition_keywords_series | condition_empty_series)]

    # 输出清洗后的数据到新的CSV文件
    try:
        df_cleaned.to_csv(output_file, index=False, encoding='utf-8-sig')
        logger.info(f"数据清洗完成，已保存到 {output_file}")
        print(f"数据清洗完成，已保存到 {output_file}")
    except Exception as e:
        logger.error(f"写入CSV文件时出错: {e}")
        print(f"写入CSV文件时出错: {e}")
