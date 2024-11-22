import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def save_cookies():
    # 设置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--start-maximized")  # 启动时窗口最大化

    # 如果需要无头模式，可以取消注释以下行
    # chrome_options.add_argument("--headless")

    # 启动浏览器
    driver = webdriver.Chrome(options=chrome_options)

    # 访问微博登录页面
    driver.get('https://m.weibo.cn/login')

    # 等待手动登录
    input("请在浏览器中完成微博登录，登录完成后按 Enter 键继续...")

    # 等待页面加载
    time.sleep(5)

    # 保存Cookies
    cookies = driver.get_cookies()
    with open('weibo_cookies.json', 'w', encoding='utf-8') as f:
        json.dump(cookies, f)

    print("Cookies已保存。")

    driver.quit()
