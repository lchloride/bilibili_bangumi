# coding=utf-8

import html.parser
import json
import os
import time

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from common.proxy import Proxy, ProxyException
from common.config import Config
from common.log import Log


class BadURL(BaseException):
    def __init__(self, msg):
        self.args = msg


class FinderException(BaseException):
    def __init__(self, msg):
        self.args = [msg]


class Finder:
    RANDOM_PROXY = -1
    NO_PROXY = -2
    CMD_LINE = 1
    GUI = 2

    def __init__(self, bangumi_url="", mode=CMD_LINE, result_list=None):
        self.bangumi_url = bangumi_url
        self.mode = mode
        self.log = Log()
        self.result_list = result_list

    def set_bangumi_url(self, bangumi_url):
        self.bangumi_url = bangumi_url

    def get_video_url(self, proxy_idx=NO_PROXY):
        return self.bangumi_url


class ChromeFinder(Finder):
    '''def __init__(self, bangumi_url=""):
        self.bangumi_url = bangumi_url'''

    def get_video_url(self, proxy_idx=Finder.NO_PROXY):
        bangumi_url = self.bangumi_url
        if bangumi_url == "":
            raise BadURL("Bad bangumi URL")

        exec_path = Config().get_property("path", "chrome_driver_path")

        self.log.write_log("Initializing...", self.mode)
        if proxy_idx != Finder.NO_PROXY:
            chrome_options = webdriver.ChromeOptions()
            proxy = Proxy()
            proxy.load()
            proxy_ip = proxy.get_proxy()
            chrome_options.add_argument('--proxy-server=' + proxy_ip)
            # ChromeOptions options = new ChromeOptions();
            # options.addArguments("user-data-dir=/path/to/your/custom/profile");
            exec_path = Config().get_property("path", "chrome_driver_path")
            bangumi_driver = webdriver.Chrome(executable_path=exec_path,
                                              chrome_options=chrome_options)
            player_driver = webdriver.Chrome(executable_path=exec_path,
                                                chrome_options=chrome_options)
            api_driver = webdriver.Chrome(executable_path=exec_path,
                                             chrome_options=chrome_options)
        else:
            bangumi_driver = webdriver.Chrome(executable_path=exec_path)

            player_driver = webdriver.Chrome(executable_path=exec_path)
            api_driver = webdriver.Chrome(executable_path=exec_path)

            self.log.write_log("Start to get bangumi page", self.mode)
        self.log.write_log("Start to get bangumi page", 0x1)

        # Get URL of player
        bangumi_driver.set_page_load_timeout(30)
        try:
            bangumi_driver.get(bangumi_url)
        except TimeoutException:
            # print(bangumi_driver.page_source)
            if bangumi_driver.page_source.find('''name="flashvars"''') == -1:
                bangumi_driver.close()
                raise TimeoutException()
            else:
                pass
        with open("bangumi.html", "w", encoding="utf-8") as fout:
            fout.write(bangumi_driver.page_source)
            fout.close()

        parameters = bangumi_driver.find_element_by_name("flashvars").get_attribute("value")
        cookies = []
        cookies.append(bangumi_driver.get_cookie("buvid3"))
        cookies.append(bangumi_driver.get_cookie("fts"))
        self.log.write_log("Get URL of player successfully", self.mode)
        bangumi_driver.close()

        # Generate api URL by cracked player
        self.log.write_log("Start to get player page", self.mode)
        player_driver.get("file:///" + os.path.realpath("../bangumi/cracked_player.html").replace('\\', '/') +
                          "?" + parameters)

        time.sleep(10)
        for entry in player_driver.get_log('browser'):
            print(entry)
        api_source = player_driver.page_source
        self.log.write_log("Get player page successfully", self.mode)
        # print(api_source)
        idx = api_source.find("""<div id="api_url">""")
        if idx == -1:
            player_driver.close()
            api_driver.close()
            raise BadURL("Bad bangumi api URL")
        else:
            api_source = api_source[idx + 18:]
            idx = api_source.find("</div>")
            api_url = api_source[:idx]
            self.log.write_log("Get URL of api", self.mode)

        api_url = html.parser.unescape(api_url)
        player_driver.close()

        # Get detailed json of bangumi
        api_driver.get(api_url)
        for cookie in cookies:
            api_driver.add_cookie(cookie)
        api_driver.get(api_url)
        bangumi_json = api_driver.find_element_by_tag_name("body").text
        bangumi_object = json.loads(bangumi_json)
        api_driver.close()

        # Return urls
        url_list = []
        try:
            for i in range(len(bangumi_object["durl"])):
                url_list.append(bangumi_object["durl"][i]["url"])
            return url_list
        except KeyError as err:
            self.log.write_log("Cannot resolve bangumi information.", self.mode)
            raise err
        return url_list


class PhantomJSFinder(Finder):
    '''def __init__(self, bangumi_url=""):
        self.bangumi_url = bangumi_url'''

    def get_video_url(self, proxy_idx=Finder.NO_PROXY):
        bangumi_url = self.bangumi_url
        if bangumi_url == "":
            raise BadURL("Bad bangumi URL")

        # print("Initializing...")
        self.log.write_log("Initializing...", self.mode)
        exec_path = Config().get_property("path", "phantomjs_exec_path")

        dcap = dict(DesiredCapabilities.PHANTOMJS)
        # Set header of request
        dcap["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
                                                    "AppleWebKit/537.36 (KHTML, like Gecko) "\
                                                    "Chrome/58.0.3029.110 Safari/537.36"

        # Not to load images
        dcap["phantomjs.page.settings.loadImages"] = False

        if proxy_idx != self.NO_PROXY:
            # Set proxy which is randomly chosen from proxy list
            proxy = Proxy()
            proxy.load()
            service_args = ['--proxy=' + proxy.get_proxy(proxy_idx), '--proxy-type=http']
            # Create drivers (Cost most time)
            bangumi_driver = webdriver.PhantomJS(exec_path, desired_capabilities=dcap, service_args=service_args)
            player_driver = webdriver.PhantomJS(exec_path, desired_capabilities=dcap, service_args=service_args)
            api_driver = webdriver.PhantomJS(exec_path, desired_capabilities=dcap, service_args=service_args)
        else:
            # Create drivers (Cost most time)
            bangumi_driver = webdriver.PhantomJS(exec_path, desired_capabilities=dcap)
            player_driver = webdriver.PhantomJS(executable_path=exec_path, desired_capabilities=dcap)
            api_driver = webdriver.PhantomJS(executable_path=exec_path, desired_capabilities=dcap)

        # print("Start to get bangumi page")
        self.log.write_log("Start to get bangumi page", self.mode)

        # Get URL of player
        bangumi_driver.set_page_load_timeout(int(Config().get_property("time", "page_load_timeout")))
        bangumi_driver.delete_all_cookies()
        try:
            bangumi_driver.get(bangumi_url)
        except TimeoutException:
            print(bangumi_driver.page_source)
            # bangumi_driver.get_screenshot_as_file("page.png")
            if bangumi_driver.page_source.find('''class="player bilibiliHtml5Player"''') == -1:
                bangumi_driver.close()
                raise TimeoutException()
            else:
                pass

        real_url = bangumi_driver.current_url
        self.log.write_log("Real URL of this page: "+real_url, self.mode)

        if real_url.find("bangumi.bilibili.com") != -1:
            # It is a real bangumi page
            try:
                element = WebDriverWait(bangumi_driver, 60).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "bilibiliHtml5Player")))
            except TimeoutException:
                bangumi_driver.save_screenshot("page.png")
                with open("bangumi.html", "w", encoding="utf-8") as fout:
                    fout.write(bangumi_driver.page_source)
                    fout.close()
                raise TimeoutException()
            finally:
                # print("Get bangumi page successfully", bangumi_driver.current_url)
                self.log.write_log("Get bangumi page successfully. ", self.mode)

            player_url = bangumi_driver.find_element_by_class_name("bilibiliHtml5Player").get_attribute("src")


        else:
            # It is a normal video page
            self.log.write_log("Get bangumi page successfully. ", self.mode)
            # Get av id
            aid_str = real_url[real_url.find("av")+2:real_url.rfind("/")]
            # Get comment id of episode series
            bangumi_driver.get('https://www.bilibili.com/widget/getPageList?aid='+aid_str)
            index_info = json.loads(bangumi_driver.find_element_by_tag_name("body").text)
            # Get this video index of episode series
            page_idx = real_url.rfind("/index_")
            if page_idx == -1:
                page_idx = 1
            else:
                page_idx = int(real_url[page_idx+7:real_url.rfind(".html")])
            # Generate player url with cid, aid and pre_ad
            player_url = ""
            for page in index_info:
                if page["page"] == page_idx:
                    player_url = "prefix?cid=%s&aid=%s&pre_ad=0" % (page["cid"], aid_str)
                    break

        # print("Get URL of player successfully", player_url)
        cookies = []
        cookies.append(bangumi_driver.get_cookie("buvid3"))
        cookies.append(bangumi_driver.get_cookie("fts"))
        self.log.write_log("Get URL of player successfully: " + player_url, self.mode)
        bangumi_driver.close()

        # Resolve URL of player
        player_url_list = player_url.split("?")
        if len(player_url_list) != 2:
            self.log.write_log("Cannot resolve URL of player", self.mode)
            return
        else:
            parameters = player_url_list[1]
            # print("Resolve URL of player successfully")
            self.log.write_log("Resolve URL of player successfully", self.mode)

        # Generate api URL by cracked player
        # print("Start to get player page")
        self.log.write_log("Start to get player page", self.mode)
        for cookie in cookies:
            api_driver.add_cookie(cookie)
        player_driver.get("file:///" + os.path.realpath("../bangumi/cracked_player.html").replace('\\', '/') +
                          "?" + parameters)
        time.sleep(2)
        api_source = player_driver.page_source
        # print("Get player page successfully")
        self.log.write_log("Get player page successfully", self.mode)

        # Find URL of api

        idx = api_source.find("""<div id="api_url">""")
        if idx == -1:
            print(api_source)
            print(player_driver.find_element_by_id("heimu").text)
            raise BadURL("Bad bangumi api URL")
        else:
            api_source = api_source[idx + 18:]
            idx = api_source.find("</div>")
            api_url = api_source[:idx]

        api_url = html.parser.unescape(api_url)
        # print("Get URL of api", api_url)
        self.log.write_log("Get URL of api: "+api_url, self.mode)

        player_driver.close()

        # Get detailed json of bangumi
        for cookie in cookies:
            api_driver.add_cookie(cookie)
        api_driver.get(api_url)
        bangumi_json = api_driver.find_element_by_tag_name("body").text
        bangumi_object = json.loads(bangumi_json)
        api_driver.close()

        # Return urls
        url_list = []
        try:
            for i in range(len(bangumi_object["durl"])):
                url_list.append(bangumi_object["durl"][i]["url"])
        except KeyError as err:
            self.log.write_log("Cannot resolve bangumi information.", self.mode)
            raise err
        self.log.write_log("Fetch video URL(s) successfully.", self.mode)
        if self.mode == self.GUI:
            self.log.write_log("Video URL(s):", 0x2)
            for url in url_list:
                self.log.write_log(url, 0x2)
            if self.result_list is not None:
                self.result_list = url_list
        return url_list


if __name__ == '__main__':
    # この番組はエロマンガ先生の第四話：エロマンガ先生です。
    # There are two forms of bangumi URL.
    # One is like "www.bilibili.com/video/av10184012", the other is like "bangumi.bilibili.com/anime/5997/play#103920"
    # finder = ChromeFinder("http://www.bilibili.com/video/av10184012/")
    # finder = PhantomJSFinder("https://bangumi.bilibili.com/anime/5997/play#103920")
    finder = PhantomJSFinder("https://www.bilibili.com/video/av10184012/")
    print(finder.get_video_url(Finder.NO_PROXY))
