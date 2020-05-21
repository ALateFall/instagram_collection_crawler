import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


class Spider():

    def __init__(self):
        self.url_login = 'https://www.instagram.com/accounts/login/?hl=en&source=auth_switcher'
        self.url_head = 'https://www.instagram.com/?hl=en'
        self.url_head_cn = 'https://www.instagram.com/?hl=zh-cn'

        self.session = requests.Session()

        self.proxies = {
            "http": "http://127.0.0.1:1080",
            "https": "http://127.0.0.1:1080",
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        }

    # 使用selenium+webdriver自动化登录，并返回cookie的值给requests进行模拟登录
    def get_cookies(self):

        # 设置chrome为无头模式
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)

        # 访问目标页面，等待页面加载完成
        driver.get(self.url_login)
        while True:
            time.sleep(0.1)
            try:
                driver.find_element_by_name('username')
                break
            except:
                pass

        # 填入账号密码并点击登录
        driver.find_element_by_name('username').send_keys("network_spider_ltfall")
        driver.find_element_by_name('password').send_keys('networkspider')
        driver.find_element_by_xpath('//button[@class="sqdOP  L3NKy   y3zKF     "]').click()

        # 等待跳转
        while driver.current_url != 'https://www.instagram.com/?hl=en':
            time.sleep(0.1)

        # 返回cookie的值
        cookies = driver.get_cookies()
        cookies = {i["name"]: i["value"] for i in cookies}
        return cookies

    def login(self):

        cookies = self.get_cookies()
        response = self.session.get(self.url_head_cn, headers=self.headers, proxies=self.proxies, cookies=cookies)
        print(response.text)


s = Spider()
s.login()
