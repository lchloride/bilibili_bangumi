# coding=utf-8
import argparse
import json
import os
from urllib import request

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import DesiredCapabilities
from selenium import webdriver

from common.config import Config, NonExistedProperty
from common.log import Log


class Danmaku(object):
    CMD_LINE = 1
    GUI = 2

    def __init__(self, mode=CMD_LINE):
        self.cid = ""
        self.mode = mode
        self.log = Log()
        self.driver = self.__create_driver()
        if self.driver is not None:
            self.driver.set_page_load_timeout(int(Config().get_property("time", "page_load_timeout")))

    def __del__(self):
        self.driver.close()

    def get_cid(self):
        return self.cid

    def set_cid(self, cid):
        if isinstance(cid, int):
            self.cid = str(cid)
        elif isinstance(cid, str):
            self.cid = cid
        else:
            self.log.write_log("Wrong format of cid!", self.mode)
            return

    def __create_driver(self):
        try:
            browser = Config().get_property("parameters", "browser")
        except NonExistedProperty as err:
            self.log.write_log("Non-existed para: parameters--browser", self.mode)
            return

        self.log.write_log("Initializing...", self.mode)
        if browser == "phantomjs":
            exec_path = Config().get_property("path", "phantomjs_exec_path")

            dcap = dict(DesiredCapabilities.PHANTOMJS)
            # Set header of request
            dcap["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
                                                        "AppleWebKit/537.36 (KHTML, like Gecko) "\
                                                        "Chrome/58.0.3029.110 Safari/537.36"

            # Not to load images
            dcap["phantomjs.page.settings.loadImages"] = False

            # Create drivers (Cost most time)
            driver = webdriver.PhantomJS(exec_path, desired_capabilities=dcap)
        elif browser == "chrome":
            exec_path = Config().get_property("path", "chrome_driver_path")
            driver = webdriver.Chrome(executable_path=exec_path)
        else:
            self.log.write_log("Invalid browser parameter.", self.mode)
            return None
        return driver

    def obtain_cid(self, video_url):
        self.log.write_log("Start to obtain cid of video "+video_url, self.mode)
        if 'bangumi.bilibili.com' in video_url:
            # Real bangumi with copyright
            bangumi_id = video_url[video_url.rfind("#")+1:]
            # print(bangumi_id)
            url = 'https://bangumi.bilibili.com/web_api/episode/%s.json' % bangumi_id
            try:
                self.driver.get(url)
            except TimeoutException as err:
                self.log.write_log("Getting aid of bangumi URL timed out.", self.mode)
                raise err
            episode_info = json.loads(self.driver.find_element_by_tag_name("pre").text)
            self.cid = episode_info["result"]["currentEpisode"]["danmaku"]
        elif 'www.bilibili.com/video/av' in video_url:
            # Normal video without copyright
            # Get av id
            aid_str = video_url[video_url.find("av")+2:video_url.rfind("/")]
            # Get comment id of episode series
            self.driver.get('https://www.bilibili.com/widget/getPageList?aid='+aid_str)
            index_info = json.loads(self.driver.find_element_by_tag_name("body").text)
            # Get this video index of episode series
            page_idx = video_url.rfind("/index_")
            if page_idx == -1:
                page_idx = 1
            else:
                page_idx = int(video_url[page_idx+7:video_url.rfind(".html")])
            # Check cid
            for page in index_info:
                if page["page"] == page_idx:
                    self.cid = str(page["cid"])
                    break
        else:
            self.log.write_log("Invalid video URL: "+video_url, self.mode)
            return

    def download(self):
        self.log.write_log("Start to obtain danmaku of video "+self.cid, self.mode)
        if self.cid == "":
            print("No cid is assigned!")
            return
        url = "http://comment.bilibili.com/%s.xml" %self.cid
        name = "%s/%s_danmaku.xml" % (os.path.dirname(os.path.dirname(os.path.abspath("danmaku.py"))),
                                   self.cid)

        self.log.write_log("Start to get danmaku.", self.mode)

        # Get URL of player
        self.driver.set_page_load_timeout(int(Config().get_property("time", "page_load_timeout")))
        try:
            self.driver.get(url)
        except TimeoutException as err:
            self.driver.close()
            raise err
        else:
            self.log.write_log("Get danmaku successfully.", self.mode)
            with open(name, "w", encoding="utf-8") as fout:
                fout.write(self.driver.page_source)
                self.log.write_log("Write danmaku file successfully. The file locates at "+name, self.mode)
                fout.close()


if __name__ == '__main__':
    '''In most circumstances, you will use URL of video to download danmaku like command:
    danmaku.py -a http://www.bilibili.com/video/av10860435/
    Also, there is a direct way to download danmaku using its chat ID(danmaku ID) like:
    danmaku.py -c 17965402
    The danmaku file is in XML format and it will locate in project root folder.
    (The video mentioned above is named "【自制字幕】NO RADIO NO LIFE 生放送特番", uploaded by AmenGuard.)
    '''
    parser = argparse.ArgumentParser(description="Obtain danmaku of video using its URL."\
                                     "For other operation, please use corresponding module.")
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument("-c", "--chatid", action="store",
                        help="Obtain danmaku by chat ID of video.(Advanced command)")
    group1.add_argument("-a", "--avid", action="store",
                        help="Obtain danmaku by video URL.(Normal circumstance)")
    args = parser.parse_args()

    print(args)

    dan = Danmaku()
    if args.avid is not None:
        dan.obtain_cid(args.avid)
    elif args.chatid is not None:
        dan.set_cid(args.chatid)
    else:
        print("Wrong Parameters!")
        exit()

    dan.download()
