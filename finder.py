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
from proxy import Proxy, ProxyException
from config import Config


class BadURL(BaseException):
    def __init__(self, msg):
        self.args = msg


class FinderException(BaseException):
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
            proxy = Proxy()
            proxy.load()
            proxy_ip = proxy.get_proxy()
            chrome_options.add_argument('--proxy-server=' + proxy_ip)
            # ChromeOptions options = new ChromeOptions();
            # options.addArguments("user-data-dir=/path/to/your/custom/profile");
            bangumi_driver = webdriver.Chrome(executable_path="chromedriver.exe",
                                              chrome_options=chrome_options)
        else:
            bangumi_driver = webdriver.Chrome(executable_path="chromedriver.exe", )

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
            api_source = api_source[idx + 18:]
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
            # Set header of request
            dcap["phantomjs.page.settings.userAgent"] = (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
                "(KHTML, like Gecko) Chrome/15.0.87"
            )
            # Not to load images
            dcap["phantomjs.page.settings.loadImages"] = False

            # Set proxy which is randomly chosen from proxy list
            proxy = Proxy()
            proxy.load()
            service_args = ['--proxy=' + proxy.get_proxy(), '--proxy-type=http']

            # Crate drivers (Cost most time)
            bangumi_driver = webdriver.PhantomJS(exec_path, desired_capabilities=dcap, service_args=service_args)
            player_driver = webdriver.PhantomJS(exec_path, desired_capabilities=dcap, service_args=service_args)
            api_driver = webdriver.PhantomJS(exec_path, desired_capabilities=dcap, service_args=service_args)
        else:
            # Crate drivers (Cost most time)
            bangumi_driver = webdriver.PhantomJS(exec_path)
            player_driver = webdriver.PhantomJS(executable_path=exec_path)
            api_driver = webdriver.PhantomJS(executable_path=exec_path)

        print("Start to get bangumi page")

        # Get URL of player
        bangumi_driver.set_page_load_timeout(int(Config().get_property("time", "page_load_timeout")))
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

        try:
            element = WebDriverWait(bangumi_driver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "bilibiliHtml5Player")))
        except TimeoutException:
            print(bangumi_driver.page_source)
            raise TimeoutException()
        finally:
            print("Get bangumi page successfully", bangumi_driver.current_url)

        player_url = bangumi_driver.find_element_by_class_name("bilibiliHtml5Player").get_attribute("src")
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

        # Find URL of api
        idx = api_source.find("""<div id="api_url">""")
        if idx == -1:
            raise BadURL("Bad bangumi api URL")
        else:
            api_source = api_source[idx + 18:]
            idx = api_source.find("</div>")
            api_url = api_source[:idx]

        api_url = html.parser.unescape(api_url)
        print("Get URL of api", api_url)
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


if __name__ == '__main__':
    # この番組はエロマンガ先生の第四話：エロマンガ先生です。
    # finder = ChromeFinder("http://www.bilibili.com/video/av10184012/")
    finder = PhantomJSFinder("http://bangumi.bilibili.com/anime/5998/play#103895")
    print(finder.getVideoURLs(True))
