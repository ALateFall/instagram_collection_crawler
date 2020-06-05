import requests
import json
from lxml import etree
from urllib.parse import quote
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import random
from fake_useragent import UserAgent
from requests.cookies import cookiejar_from_dict

headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
}

class s():
    def __init__(self):
        self.session = requests.Session()

    def get_cookies(self):
        # 输出提示语句
        print('正在得到cookies，请稍等···')

        # 设置chrome为无头模式
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)

        url_login = 'https://www.instagram.com/accounts/login/?hl=en&source=auth_switcher'
        accounts = eval(open('accounts', 'r').read())  # 读取目录下的accounts文件，里面装有账号信息，是一个列表
        choose = random.randint(0, 9)
        # driver = webdriver.Chrome()

        # driver = webdriver.Chrome()

        # 访问目标页面，等待页面加载完成
        driver.get(url_login)
        while True:
            time.sleep(0.1)
            try:
                driver.find_element_by_name('username')
                break
            except:
                pass

        # 填入账号密码并点击登录
        username = accounts[choose]['username']
        password = accounts[choose]['password']
        driver.find_element_by_name('username').send_keys(username)
        driver.find_element_by_name('password').send_keys(password)
        driver.find_element_by_xpath('//button[@class="sqdOP  L3NKy   y3zKF     "]').click()
        choose += 1
        choose %= 10

        # 等待跳转
        time.sleep(5)

        # 返回cookie的值
        cookies = driver.get_cookies()
        cookies = {i["name"]: i["value"] for i in cookies}

        # 输出提示语句
        print('成功得到cookies···')

        return cookies

    def login(self):
        cookie = self.get_cookies()
        print(cookie)
        response = self.session.get('https://www.instagram.com', cookies=cookie)
        self.session.cookies = cookiejar_from_dict(cookie)


ss = s()
ss.login()