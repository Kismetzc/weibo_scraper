import logging
import pandas as pd

def setup_logger(log_file='logs/weibo_scraper.log'):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 防止重复添加处理器
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

def combined_csv(input_file1, input_file2, output_file):
    df1 = pd.read_csv(input_file1, encoding='utf-8')
    df2 = pd.read_csv(input_file2, encoding='utf-8')
    df_combined = pd.concat([df1, df2], ignore_index=True)
    df_combined.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"合并完成，已保存到 {output_file}")
