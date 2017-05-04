# coding=utf-8

import os
import html.parser
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from config import Config
from downloader import Downloader


class BadURL(BaseException):
    def __init__(self, msg):
        self.args = msg


class Finder:
    def __init__(self, bangumi_url=""):
        self.bangumi_url = bangumi_url

    def set_bangumi_url(self, bangumi_url):
        self.bangumi_url = bangumi_url

    def getVideoURLs(self):
        bangumi_url = self.bangumi_url
        if bangumi_url == "":
            raise BadURL("Bad bangumi URL")

        player_url = ""
        exec_path = Config().get_property("path", "phantomjs_exec_path")
        print("Initializing...")
        bangumi_driver = webdriver.PhantomJS(executable_path=exec_path)
        player_driver = webdriver.PhantomJS(executable_path=exec_path)
        api_driver = webdriver.PhantomJS(executable_path=exec_path)

        print("Start to get bangumi page")
        # Get URL of player
        bangumi_driver.get(bangumi_url)
        try:
            element = WebDriverWait(bangumi_driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "bilibiliHtml5Player")))
        finally:
            print("Get bangumi page successfully")
            player_url = bangumi_driver.find_element_by_class_name("bilibiliHtml5Player").get_attribute("src")
        print("Get URL of player successfully")
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
        # print(os.path.realpath("cracked_player.html"))
        print("Start to get player page")
        player_driver.get("file:///" + os.path.realpath("cracked_player.html").replace('\\', '/') +
                          "?" + parameters)
        # print(player_driver.current_url)
        time.sleep(2)
        # player_driver.get_screenshot_as_file('show.png')
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
    finder = Finder("https://www.bilibili.com/video/av10184012/")
    finder.getVideoURLs()
