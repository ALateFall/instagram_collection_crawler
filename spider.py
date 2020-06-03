import traceback
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from lxml import etree
import json
from urllib.parse import quote
import random
from fake_useragent import UserAgent



class Spider():

    def __init__(self):

        self.url_login = 'https://www.instagram.com/accounts/login/?hl=en&source=auth_switcher'
        self.url_head = 'https://www.instagram.com/?hl=en'
        self.url_head_cn = 'https://www.instagram.com/?hl=zh-cn'
        self.url_tag = 'https://www.instagram.com/explore/tags/networksecurity/'
        self.url_json_ls_nocursor = 'https://www.instagram.com/graphql/query/?query_hash=7dabc71d3e758b1ec19ffb85639e427b&variables='
        self.url_json_noshortcode = 'https://www.instagram.com/graphql/query/?query_hash=55a3c4bad29e4e20c20ff4cdfd80f5b4&variables='
        self.nodes_ls = []
        self.shortcodes_ls = []
        self.username_ls = []
        self.accounts = eval(open('accounts', 'r').read())  # 读取目录下的accounts文件，里面装有账号信息，是一个列表
        self.choose = random.randint(0, 10)

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

        # 输出提示语句
        print('正在得到cookies，请稍等···')


        # 设置chrome为无头模式
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)


        # driver = webdriver.Chrome()

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
        username = self.accounts[self.choose]['username']
        password = self.accounts[self.choose]['password']
        driver.find_element_by_name('username').send_keys(username)
        driver.find_element_by_name('password').send_keys(password)
        driver.find_element_by_xpath('//button[@class="sqdOP  L3NKy   y3zKF     "]').click()
        self.choose += 1
        self.choose %= 11


        # 等待跳转
        time.sleep(5)

        # 返回cookie的值
        cookies = driver.get_cookies()
        cookies = {i["name"]: i["value"] for i in cookies}

        # 输出提示语句
        print('成功得到cookies···')

        return cookies

    # 使用requests库发起带cookies的登录
    def login(self, cookies):

        # 输出提示语句
        print('正在使用cookies登录···')

        # 登录
        ua = UserAgent()
        user_agent = ua.random
        self.headers['User-Agent'] = user_agent
        self.session.get(self.url_head_cn, proxies=self.proxies, cookies=cookies, headers=self.headers)

        # 输出提示语句
        print('登录完成···')

    # 得到网页js生成的用户的用户名以及ajax的第一个after参数
    # 返回一个字典，字典包含第一个cursor以及js生成的nodes
    def get_username_first(self):

        # 输出提示语句
        print('正在得到网页js包裹的数据···')

        # 得到网页原始的js包裹的字符串
        response = self.session.get(self.url_tag, proxies=self.proxies)
        html = etree.HTML(response.text)
        text_result = html.xpath('//script[@type="text/javascript"]//text()')

        # 从中提取出json数据并得到字典
        ret = ""
        for i in text_result:
            if i.startswith('window._sharedData ='):
                ret = i
                break
        ret = ret.lstrip("window._sharedData = ")
        ret = ret.rstrip(';')
        ret = json.loads(ret)

        # 从中获取cursor的值
        cursor = ret["entry_data"]["TagPage"][0]["graphql"]["hashtag"]["edge_hashtag_to_media"]["page_info"][
            "end_cursor"]

        # 从中获取前面的用户的id信息
        # 先得到一个列表,里面存放nodes的json数据
        ls_user = ret["entry_data"]["TagPage"][0]["graphql"]["hashtag"]["edge_hashtag_to_media"]["edges"]

        my_dic = {"cursor": cursor, "ls_user": ls_user}

        # 输出提示语句
        print('成功得到js包裹的数据···')

        return my_dic

    def get_username_after(self, cursor):

        url = self.url_json_ls_nocursor + '{"tag_name":"networksecurity","first":10,"after":"' + cursor + '"}'
        response = self.session.get(url, proxies=self.proxies)

        ret = json.loads(response.text)

        # 从json字符串中得到下一个cursor
        cursor = ret['data']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']

        # 从json字符串中得到用户id信息
        # 得到一个列表，存放着nodes的json数据
        ls_user = ret['data']['hashtag']['edge_hashtag_to_media']['edges']

        my_dic = {"cursor": cursor, "ls_user": ls_user}
        return my_dic

    def get_user_info(self):
        pass

    # 处理字典信息，将用户的node信息赋值给类属性，返回cursor的值
    def process_dic(self, my_dic):

        nodes_ls = my_dic['ls_user']
        self.process_nodes(nodes_ls)
        return my_dic['cursor']

    # 将nodes信息处理
    def process_nodes(self, nodes):

        for node in nodes:
            self.shortcodes_ls.append(node['node']['shortcode'])

    # 进行帖子信息的抓取
    def get_all_info(self):

        for shortcode in self.shortcodes_ls:
            str_url = '{'+'"shortcode":"' + shortcode + '"}'
            str_url = quote(str_url)
            url = self.url_json_noshortcode + str_url
            dic_temp = self.get_page_info(url)
            if dic_temp == {}:
                pass
            else:
                print(dic_temp)

    # 和上面的get_all_info是连着的，每一步的动作
    def get_page_info(self, url):

        userinfo_dict = {}

        try:
            time.sleep(1)
            response = self.session.get(url, proxies=self.proxies)
            ret = json.loads(response.text)

            # 发布的图片信息：图片文件、发布时间、点赞数、评论数

            # 图片的url
            pic_url = ret['data']['shortcode_media']['display_url']
            userinfo_dict['pic_url'] = pic_url

            # 图片的发布时间
            take_time = ret['data']['shortcode_media']['taken_at_timestamp']
            pic_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(take_time))
            userinfo_dict['pic_time'] = pic_time

            # 图片的点赞数
            pic_like = ret['data']['shortcode_media']['edge_media_preview_like']['count']
            userinfo_dict['pic_like'] = pic_like

            # 图片的评论数
            pic_comment = ret['data']['shortcode_media']['edge_media_to_comment']['count']
            userinfo_dict['pic_comment'] = pic_comment
        except Exception as e:
            # traceback.print_exc()
            print('速率过快，尝试重新登录···')
            self.session.close()
            cookie = self.get_cookies()
            self.login(cookie)
            time.sleep(3)
            print('再次尝试')
            # print('the current url is: '+url)

        return userinfo_dict

    def start(self):

        cookie = self.get_cookies()
        self.login(cookie)

        # max = eval(input('请输入一个爬取的数字，爬取的总数将不小于这个数字。'))
        # time.sleep(1)
        max = 2000
        dic_temp = self.get_username_first()
        cursor_temp = self.process_dic(dic_temp)
        # print(cursor_temp)

        # 输出提示语句
        print('开始得到nodes数据···')

        if len(self.shortcodes_ls) >= max:
            pass
        else:
            while True:
                dic_temp = self.get_username_after(cursor_temp)
                cursor_temp = self.process_dic(dic_temp)
                # print(cursor_temp)
                if len(self.shortcodes_ls) >= max:
                    break
                else:
                    print('当前已有' + str(len(self.shortcodes_ls)) + '个数据···')

        self.get_all_info()


s = Spider()
s.start()
