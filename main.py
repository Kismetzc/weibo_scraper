# main.py

from scraper import WeiboScraper
from cleaner import clean_comments
from wordcloud_generate import generate_wordcloud
from save_weibo_cookies import save_cookies
import pandas as pd

def main():
    # 定义微博URLs，key为人名，value为微博URL列表
    weibo_urls = {
        "hsy": ["https://m.weibo.cn/detail/5089355749920273"],
        "ml": ["https://m.weibo.cn/detail/4453872984387000"],
        "gx": ["https://m.weibo.cn/detail/5076048028634673"],
        "lhl": ["https://m.weibo.cn/detail/5046948576626988"],
        "ls": ["https://m.weibo.cn/detail/5090857215333059"],
        "yz": ["https://m.weibo.cn/detail/5089370893981301"],
    }

    # 定义数据和文件路径
    data_dir = 'new_data'
    raw_dir = f"{data_dir}/raw"
    cleaned_dir = f"{data_dir}/cleaned"
    wordclouds_dir = f"{data_dir}/wordclouds"
    stopwords_dir = 'stopwords'  # 停用词目录路径
    font_path = 'fonts/SimHei.ttf'  # 中文字体文件路径

    # 创建必要的目录
    import os
    for directory in [raw_dir, cleaned_dir, wordclouds_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # 检查是否存在cookies文件，如果不存在则运行保存cookies的函数
    cookies_file = 'cookies/weibo_cookies.json'
    if not os.path.exists(cookies_file):
        print("未找到cookies文件，开始保存微博cookies...")
        save_cookies()
        print("微博cookies保存完成。")

    # 初始化爬虫
    scraper = WeiboScraper(
        cookies_file='cookies/weibo_cookies.json',
        log_file='logs/weibo_scraper.log'
    )

    for name, urls in weibo_urls.items():
        for idx, url in enumerate(urls, start=1):
            # 定义输出的CSV文件路径，以人名命名
            output_csv = f"{raw_dir}/comments_{name}_raw.csv"
            print(f"开始爬取 {name} 的微博: {url}")
            scraper.scrape_comments(url, output_csv)

    # # 关闭浏览器
    # scraper.close_driver()

    # 定义过滤关键词
    condition_keywords = ['中国', 'CN', '祖国', '国家', '统一', '台湾', '只有一个', '针', '老师', '武艺','期待']

    # 数据清洗
    for name, urls in weibo_urls.items():
        for idx, url in enumerate(urls, start=1):
            raw_csv = f"{raw_dir}/comments_{name}_raw.csv"
            cleaned_csv = f"{cleaned_dir}/comments_{name}_cleaned.csv"
            print(f"开始清洗 {name} 的数据: {raw_csv}")
            clean_comments(
                input_file=raw_csv,
                output_file=cleaned_csv,
                condition_keywords=condition_keywords
            )

    # 生成词云
    custom_stopwords = ["微博", "视频", "图片", "评论"]
    for name in weibo_urls.keys():
        cleaned_csv = f"{cleaned_dir}/comments_{name}_cleaned.csv"
        output_image = f"{wordclouds_dir}/wordcloud_{name}.png"
        print(f"开始生成 {name} 的词云: {output_image}")
        generate_wordcloud(
            input_csv=cleaned_csv,
            output_image=output_image,
            stopwords_dir=stopwords_dir,
            custom_stopwords=custom_stopwords,
            font_path=font_path
        )

    print("所有流程已完成。")

if __name__ == "__main__":
    main()
