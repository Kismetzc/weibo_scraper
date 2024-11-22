import time
import csv
import logging
import random
import json
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.action_chains import ActionChains

from utils import setup_logger


class WeiboScraper:
    def __init__(self, cookies_file='cookies/weibo_cookies.json', log_file='logs/weibo_scraper.log'):
        self.logger = setup_logger(log_file)
        self.cookies_file = cookies_file
        self.driver = self.initialize_driver()
        self.load_cookies()

    def initialize_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument(f"user-agent={self.get_random_user_agent()}")
        chrome_options.add_experimental_option('detach', True)

        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def get_random_user_agent(self):
        USER_AGENTS = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1',
            # 添加更多 User-Agent
        ]
        return random.choice(USER_AGENTS)

    def load_cookies(self):
        try:
            self.driver.get('https://m.weibo.cn')  # 访问一个页面以便添加 Cookies
            with open(self.cookies_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            self.driver.refresh()
            self.logger.info("加载 Cookies 并刷新页面。")
        except Exception as e:
            self.logger.error(f"加载 Cookies 失败: {e}")
            print(f"加载 Cookies 失败: {e}")
            sys.exit()

    def simulate_user_behavior(self):
        try:
            # 获取页面的宽度和高度
            page_width = self.driver.execute_script("return document.body.scrollWidth")
            page_height = self.driver.execute_script("return document.body.scrollHeight")

            # 计算相对于页面中间的偏移量，确保不会超出范围
            move_x_offset = int(page_width * random.uniform(-0.05, 0.05))
            move_y_offset = int(page_height * random.uniform(-0.05, 0.05))

            # 模拟鼠标移动到相对于页面中间的位置
            action = ActionChains(self.driver)
            body = self.driver.find_element(By.TAG_NAME, 'body')
            action.move_to_element_with_offset(body, page_width // 2 + move_x_offset,
                                               page_height // 2 + move_y_offset).perform()
            time.sleep(random.uniform(1, 3))

            # 随机滚动页面的部分区域
            scroll_position = int(page_height * random.uniform(0.4, 0.6))  # 聚焦中间部分
            self.driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(random.uniform(2, 5))

        except Exception as e:
            self.logger.error(f"模拟用户行为时发生错误: {e}")
            # print(f"模拟用户行为时发生错误: {e}")

    def get_total_comments(self):
        try:
            total_comments_elem = self.driver.find_element(By.XPATH,
                                                           '//div[contains(@class, "tab-item") and contains(@class, "cur")]/i[2]')
            total_comments_text = total_comments_elem.text.strip()
            total_comments = int(total_comments_text.replace(',', '')) if total_comments_text.replace(',',
                                                                                                      '').isdigit() else 0
            self.logger.info(f"总评论数: {total_comments}")
            print(f"总评论数: {total_comments}")
            return total_comments
        except NoSuchElementException:
            self.logger.error("未找到总评论数元素，请检查是否已成功登录。")
            print("未找到总评论数元素，请检查是否已成功登录。")
            sys.exit()

    def scrape_comments(self, weibo_url, output_csv):
        self.driver.get(weibo_url)
        self.logger.info(f"打开微博页面成功: {weibo_url}")
        print(f"微博页面已打开: {weibo_url}")
        time.sleep(5)  # 等待页面加载

        total_comments = self.get_total_comments()
        if total_comments == 0:
            self.logger.info("评论数为0，无需继续爬取。")
            print("评论数为0，无需继续爬取。")
            return

        # 初始化CSV文件
        with open(output_csv, mode='w', encoding='utf-8-sig', newline='') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(['comment_id', 'user_name', 'text_raw', 'source', 'like_counts', 'created_at'])

        # 加载所有评论
        max_scrolls = 10000
        scrolls = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        NEARLY_LOADED_THRESHOLD = 10
        CONSECUTIVE_NO_INCREASE_LIMIT = 30
        MAX_SCROLLS_THRESHOLD = int(max_scrolls * 0.8)
        consecutive_no_increase_count = 0

        while scrolls < max_scrolls:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1, 5))

            # 模拟用户行为
            # self.simulate_user_behavior()

            comments = self.driver.find_elements(By.XPATH,
                                                 '//div[contains(@class, "card m-avatar-box lite-page-list")]')
            loaded_comments = len(comments)
            self.logger.info(f"已加载评论数: {loaded_comments}")
            print(f"已加载评论数: {loaded_comments}")

            if loaded_comments >= total_comments:
                self.logger.info("已加载全部评论。")
                break

            # 判断是否接近全部加载完成
            if abs(loaded_comments - total_comments) <= NEARLY_LOADED_THRESHOLD:
                self.logger.info("已接近全部加载完成评论。")
                break

            # 判断是否连续多次已加载评论数未明显增加且已接近最大滚动次数
            if scrolls >= MAX_SCROLLS_THRESHOLD:
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    consecutive_no_increase_count += 1
                else:
                    consecutive_no_increase_count = 0
                last_height = new_height
                time.sleep(random.uniform(1, 5))

                if consecutive_no_increase_count >= CONSECUTIVE_NO_INCREASE_LIMIT:
                    self.logger.info("已接近最大滚动次数且页面高度连续多次未变化，可能已基本加载完成。")
                    break

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                self.logger.info("页面高度未变化，可能已到达页面底部。")
                break
            last_height = new_height
            scrolls += 1
            self.logger.info(f"已执行滚动 {scrolls} 次。")

        self.logger.info(f"完成滚动，共执行了 {scrolls} 次。")
        print(f"完成滚动，共执行了 {scrolls} 次。")

        comments = self.driver.find_elements(By.XPATH, '//div[contains(@class, "card m-avatar-box lite-page-list")]')
        self.logger.info(f"共检测到 {len(comments)} 条评论。")
        print(f"共检测到 {len(comments)} 条评论。")

        if len(comments) == 0:
            self.logger.info("未检测到任何评论。")
            print("未检测到任何评论。")
            return

        # 提取评论数据
        for idx, comment in enumerate(comments, start=1):
            try:
                # 每爬取一定数量的评论后，增加长时间等待
                if idx % 500 == 0:
                    self.logger.info(f"已爬取 {idx} 条评论，暂停等待。")
                    time.sleep(random.uniform(1, 10))

                # 使用评论的次序编号作为 comment_id
                comment_id = str(idx)

                # 提取用户名
                user_name_elem = comment.find_element(By.XPATH, './/h4[contains(@class, "m-text-cut")]')
                user_name = user_name_elem.text.strip()

                # 提取评论内容
                text_raw_elem = comment.find_element(By.XPATH, './/h3')
                text_raw = text_raw_elem.text.strip()

                # 提取评论时间和来源
                info_div = comment.find_element(By.XPATH,
                                                './/div[contains(@class, "m-box-center-a") and contains(@class, "time")]')
                info_text = info_div.text.strip()
                if "来自" in info_text:
                    parts = info_text.split("来自")
                    created_at = parts[0].strip()
                    source = parts[1].strip()
                else:
                    created_at = info_text.strip()
                    source = ""

                # 加上 '24-' 前缀
                created_at = f"24-{created_at}"

                # 提取点赞数
                try:
                    like_count_elem = comment.find_element(By.XPATH,
                                                           './/aside[i[contains(@class, "lite-iconf-like")]]/em')
                    like_counts_text = like_count_elem.text.strip()
                    like_counts = int(like_counts_text.replace(',', '')) if like_counts_text.replace(',',
                                                                                                     '').isdigit() else 0
                except NoSuchElementException:
                    like_counts = 0

                # 写入 CSV 文件
                with open(output_csv, mode='a', encoding='utf-8-sig', newline='') as f:
                    csv_writer = csv.writer(f)
                    csv_writer.writerow([comment_id, user_name, text_raw, source, like_counts, created_at])

                self.logger.info(f"已爬取评论 {idx}: ID={comment_id}, 用户={user_name}, 评论={text_raw}, 赞数={like_counts}")
                print(f"已爬取评论 {idx}: ID={comment_id}, 用户={user_name}, 评论={text_raw}, 赞数={like_counts}")

            except NoSuchElementException as e:
                self.logger.error(f"解析评论 {idx} 时出错: {e}")
                print(f"解析评论 {idx} 时出错: {e}")
                continue
            except StaleElementReferenceException as e:
                self.logger.error(f"解析评论 {idx} 时出错: {e}")
                print(f"解析评论 {idx} 时出错: {e}")
                continue
            except Exception as e:
                self.logger.error(f"解析评论 {idx} 时发生未知错误: {e}")
                print(f"解析评论 {idx} 时发生未知错误: {e}")
                continue

        self.logger.info("所有评论爬取完成。")
        print("所有评论爬取完成。")
