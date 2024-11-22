import logging


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
