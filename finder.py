# coding=utf-8

import html.parser
import json
import os
import time
from random import random

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.proxy import Proxy, ProxyType
from config import Config


class BadURL(BaseException):
    def __init__(self, msg):
        self.args = msg


class ChromeFinder:

    def __init__(self, bangumi_url=""):
        self.bangumi_url = bangumi_url

    def set_bangumi_url(self, bangumi_url):
        self.bangumi_url = bangumi_url

    def getVideoURLs(self, use_proxy=False):
        bangumi_url = self.bangumi_url
        if bangumi_url == "":
            raise BadURL("Bad bangumi URL")

        exec_path = Config().get_property("path", "phantomjs_exec_path")

        print("Initializing...")
        if use_proxy:
            chrome_options = webdriver.ChromeOptions()
            proxy_ip = "http://61.191.41.130:80"
            chrome_options.add_argument('--proxy-server=' + proxy_ip)
            # ChromeOptions options = new ChromeOptions();
            # options.addArguments("user-data-dir=/path/to/your/custom/profile");
            bangumi_driver = webdriver.Chrome(executable_path="chromedriver.exe",
                                              chrome_options=chrome_options)
        else:
            bangumi_driver = webdriver.Chrome(executable_path="chromedriver.exe",)

        player_driver = webdriver.PhantomJS(executable_path=exec_path)
        api_driver = webdriver.PhantomJS(executable_path=exec_path)

        print("Start to get bangumi page")

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

        parameters = bangumi_driver.find_element_by_name("flashvars").get_attribute("value")
        print("Get URL of player successfully")
        bangumi_driver.close()

        # Generate api URL by cracked player
        print("Start to get player page")
        player_driver.get("file:///" + os.path.realpath("cracked_player.html").replace('\\', '/') +
                          "?" + parameters)

        time.sleep(2)

        api_source = player_driver.page_source
        print("Get player page successfully")

        idx = api_source.find("""<div id="api_url">""")
        if idx == -1:
            raise BadURL("Bad bangumi api URL")
        else:
            api_source = api_source[idx+18:]
            idx = api_source.find("</div>")
            api_url = api_source[:idx]
            print("Get URL of api")

        api_url = html.parser.unescape(api_url)
        player_driver.close()

        # Get detailed json of bangumi
        api_driver.get(api_url)
        bangumi_json = api_driver.find_element_by_tag_name("body").text
        bangumi_object = json.loads(bangumi_json)
        api_driver.close()

        # Return urls
        url_list = []
        for i in range(len(bangumi_object["durl"])):
            url_list.append(bangumi_object["durl"][i]["url"])
        return url_list


class PhantomJSFinder:
    def __init__(self, bangumi_url=""):
        self.bangumi_url = bangumi_url

    def set_bangumi_url(self, bangumi_url):
        self.bangumi_url = bangumi_url

    def getVideoURLs(self, use_proxy=False):
        bangumi_url = self.bangumi_url
        if bangumi_url == "":
            raise BadURL("Bad bangumi URL")

        exec_path = Config().get_property("path", "phantomjs_exec_path")
        print("Initializing...")
        if use_proxy:
            dcap = dict(DesiredCapabilities.PHANTOMJS)
            # 从USER_AGENTS列表中随机选一个浏览器头，伪装浏览器
            dcap["phantomjs.page.settings.userAgent"] = (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
                "(KHTML, like Gecko) Chrome/15.0.87"
            )
            # 不载入图片，爬页面速度会快很多
            dcap["phantomjs.page.settings.loadImages"] = False
            # 设置代理
            service_args = ['--proxy=61.191.41.130:80', '--proxy-type=http']
            bangumi_driver = webdriver.PhantomJS(exec_path, desired_capabilities=dcap, service_args=service_args)
            player_driver = webdriver.PhantomJS(exec_path, desired_capabilities=dcap, service_args=service_args)
            api_driver = webdriver.PhantomJS(exec_path, desired_capabilities=dcap, service_args=service_args)
            # api_driver = webdriver.PhantomJS(executable_path=exec_path)
        else:
            bangumi_driver = webdriver.PhantomJS(exec_path)
            player_driver = webdriver.PhantomJS(executable_path=exec_path)
            api_driver = webdriver.PhantomJS(executable_path=exec_path)

        print("Start to get bangumi page")

        # Get URL of player
        bangumi_driver.set_page_load_timeout(60)
        try:
            bangumi_driver.get(bangumi_url)
        except TimeoutException:
            print(bangumi_driver.page_source)
            bangumi_driver.get_screenshot_as_file("page.png")
            if bangumi_driver.page_source.find('''class="player bilibiliHtml5Player"''') == -1:
                bangumi_driver.close()
                raise TimeoutException()
            else:
                pass

        # print(bangumi_driver.find_element_by_css_selector("div.bg").value_of_css_property("background"))
        try:
            element = WebDriverWait(bangumi_driver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "bilibiliHtml5Player")))
        except TimeoutException:
            print(bangumi_driver.page_source)
            raise TimeoutException()
        finally:
            print("Get bangumi page successfully", bangumi_driver.current_url)

        player_url = bangumi_driver.find_element_by_class_name("bilibiliHtml5Player").get_attribute("src")
        # time.sleep(5)
        # parameters = bangumi_driver.find_element_by_name("flashvars").get_attribute("value")
        print("Get URL of player successfully", player_url)
        bangumi_driver.close()

        # Resolve URL of player
        player_url_list = player_url.split("?")
        if len(player_url_list) != 2:
            print("Cannot resolve URL of player")
            return
        else:
            parameters = player_url_list[1]
            print("Resolve URL of player successfully")

        # Generate api URL by cracked player
        print("Start to get player page")
        player_driver.get("file:///" + os.path.realpath("cracked_player.html").replace('\\', '/') +
                          "?" + parameters)

        time.sleep(2)

        api_source = player_driver.page_source
        print("Get player page successfully")

        idx = api_source.find("""<div id="api_url">""")
        if idx == -1:
            raise BadURL("Bad bangumi api URL")
        else:
            api_source = api_source[idx + 18:]
            idx = api_source.find("</div>")
            api_url = api_source[:idx]
            print("Get URL of api")
        # api_url = player_driver.find_element_by_xpath("/html/body/div[3]").text
        api_url = html.parser.unescape(api_url)
        # print(api_url)
        # print('-'*20)
        player_driver.close()

        # Get detailed json of bangumi
        api_driver.get(api_url)
        bangumi_json = api_driver.find_element_by_tag_name("body").text
        # print(bangumi_json)
        bangumi_object = json.loads(bangumi_json)
        api_driver.close()

        # Return urls
        url_list = []
        for i in range(len(bangumi_object["durl"])):
            url_list.append(bangumi_object["durl"][i]["url"])
        return url_list


if __name__ == '__main__':
    # finder = ChromeFinder("http://www.bilibili.com/video/av10184012/")
    finder = PhantomJSFinder("http://www.bilibili.com/video/av10184012/")
    print(finder.getVideoURLs(True))
