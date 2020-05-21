import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


session = requests.Session()

proxies = {
    "http": "http://127.0.0.1:1080",
    "https": "http://127.0.0.1:1080",
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
}


def get_cookies():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    # driver = webdriver.Chrome()
    driver.get('https://www.instagram.com/accounts/login/?hl=en&source=auth_switcher')
    # driver.get('https://www.instagram.com/?hl=zh-cn')
    while True:
        time.sleep(0.1)
        try:
            driver.find_element_by_name('username')
            break
        except:
            pass
    driver.find_element_by_name('username').send_keys("network_spider_ltfall")
    driver.find_element_by_name('password').send_keys('networkspider')
    driver.find_element_by_xpath('//button[@class="sqdOP  L3NKy   y3zKF     "]').click()
    while driver.current_url != 'https://www.instagram.com/?hl=en':
        time.sleep(0.1)
    cookies = driver.get_cookies()
    cookies = {i["name"]: i["value"] for i in cookies}
    return cookies


cookies = get_cookies()
response = session.get('https://www.instagram.com/?hl=zh-cn', proxies=proxies, headers=headers, cookies=cookies)
