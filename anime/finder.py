# coding = utf-8
import json
import time
from urllib import parse, request
from selenium import webdriver, common
from common.config import Config



class AnimeFinder:
    NO_ASSIGNED = 0
    TIMELINE = 1
    SEARCH = 2
    INDEX = 3
    season = {1: 'Winter', 2: 'Winter', 3: 'Winter', 4: 'Spring', 5: 'Spring', 6: 'Spring',
              7: 'Summer', 8: 'Summer', 9: 'Summer', 10: 'Fall', 11: 'Fall', 12: 'Fall'}

    def __init__(self):
        self.finder_type = self.NO_ASSIGNED
        self.result = None
        self.filter = self.__read_filter()
        # print(self.filter)

    def get_timeline(self):
        '''
        This method is used to query animes information of current season which is called timeline by bilibili. 
        '''
        print("Initializing...")
        timeline_driver = self.__create_driver()

        year = time.strftime('%Y', time.localtime(time.time()))
        month = int(time.strftime('%m', time.localtime(time.time())))
        print("Get animes information of this season (%s %s)." % (year, self.season[month]))
        timeline_driver.get("http://bangumi.bilibili.com/anime/timeline")
        # print(timeline_driver.page_source)
        date_ele = timeline_driver.find_elements_by_xpath('//ul[@id="bangumi"]/li')
        dates = []
        timeline = []
        for date in date_ele:
            d = date.get_attribute("data-anchor")
            dates.append(d)
            day = {}
            day["date"] = d
            day["weekday"] = timeline_driver.find_element_by_xpath('//ul[@id="bangumi"]/li[@data-anchor="' + d + '"]'
                                                                                                                 '/div[@class="bgm-timeline-title"]'
                                                                                                                 '/span[@class="week-day"]').text
            animes_ele = timeline_driver.find_elements_by_xpath('//ul[@id="bangumi"]/li[@data-anchor="' + d + '"]'
                                                                                                              '/ul[@class="bangumi c-list"]/li'
                                                                                                              '/div[@class="c-item"]')
            animes = []
            for anime_ele in animes_ele:
                anime = {}
                anime["bg"] = anime_ele.find_element_by_xpath('a[@class="preview"]/img').get_attribute("src")
                anime["url"] = anime_ele.find_element_by_xpath('div[@class="r-i"]/a').get_attribute("href")
                anime["name"] = anime_ele.find_element_by_xpath('div[@class="r-i"]/a/p[@class="t"]/span').text
                time_status = anime_ele.find_element_by_xpath('div[@class="r-i"]/p[@class="update-time"]').text
                anime["time"], anime["status"] = time_status.split(" ")
                if anime["status"] == "更新":
                    anime["status"] = "未更新"
                anime["episode"] = anime_ele.find_element_by_xpath('div[@class="r-i"]') \
                    .find_element_by_class_name("update-info").text
                try:
                    anime["episode_url"] = anime_ele.find_element_by_xpath('div[@class="r-i"]/a[2]').get_attribute(
                        "href")
                except common.exceptions.NoSuchElementException as err:
                    anime["episode_url"] = "N/A"
                # print(anime["episode_url"])
                animes.append(anime)
            day["animes"] = animes
            timeline.append(day)
        print("Resolve page successfully.")
        timeline_driver.close()
        self.result = timeline
        self.finder_type = self.TIMELINE
        # print(json.dumps(timeline, ensure_ascii=False))

    def search(self, keyword):
        print("Initializing...")
        search_driver = self.__create_driver()
        print('Searching for keyword %s...' %keyword)
        para = {"keyword": keyword}
        search_driver.set_page_load_timeout(Config().get_property("time", "page_load_timeout"))
        search_driver.get("http://search.bilibili.com/bangumi?"+parse.urlencode(para))

        print("Resolve searching result.")
        # print(search_driver.page_source)
        if search_driver.find_element_by_class_name("no-result").is_displayed():
            print("No anime is found.")
            return

        search = {"keyword": keyword}
        bases = search_driver.find_elements_by_xpath('//div[@class="so-wrap"]/div[@class="ajax-render"]/'
                                                         'li[@class="synthetical"]')
        search["animes"] = []
        for base in bases:
            name = base.find_element_by_xpath('div[@class="right-info"]/div[@class="headline"]/'
                                                'a[@class="title"]').text
            desc = base.find_element_by_xpath('div[@class="right-info"]/div[@class="des "]').text
            bg = base.find_element_by_xpath('div[@class="left-img"]/a/img').get_attribute("data-src")
            if bg is None:
                bg = base.find_element_by_xpath('div[@class="left-img"]/a/img').get_attribute("src")
            else:
                bg = bg[2:]

            season_ele = base.find_elements_by_xpath('ul[@class="so-episode"]/a[@class="list sm "]')
            seasons = []
            for season in season_ele:
                url = season.get_attribute("href")
                season_name = season.find_element_by_xpath('span[@class="bgm-list-title"]').text
                seasons.append({"name": season_name, "url": url})
            search["animes"].append({"name": name, "desc": desc, "bg": bg, "seasons": seasons})
        # print(json.dumps(search, ensure_ascii=False))
        print("Resolve result successfully.")
        self.result = search
        self.finder_type = self.SEARCH

    def index(self, para):
        print("Initializing...")
        index_driver = self.__create_driver()
        index_driver.get("http://bangumi.bilibili.com/anime/index#p=2&v=0&area=&stat=0&y=2017&q=0&tag=&t=1&sort=0")
        print(index_driver.page_source)
        bases = index_driver.find_elements_by_xpath('//div[@class="v_list"]/ul[@class="v_ul"]'
                                                        '/li/div[@class="preview"]')
        animes = []
        for base in bases:
            name = base.find_element_by_xpath('div[@class="info_wrp"]/div[@class="info"]/a/div[@class="t"]').text
            episode_status = base.find_element_by_xpath('div[@class="info_wrp"]/div[@class="info"]/'
                                                        'p[@class="num"]').text
            if episode_status.find("更新至") != -1:
                episode = episode_status[3:]
                status = "未完结"
            else:
                episode = episode_status
                status = "已完结"
            bg = base.find_element_by_xpath('div[@class="cover"]/a/div[@class="img-loading"]/img')\
                .get_attribute("data-img")
            url = base.find_element_by_xpath('div[@class="cover"]/a').get_attribute("href")
            sort_info = base.find_element_by_xpath('div[@class="cover"]/a/div[@class="shadow"]'
                                                   '/span[@class="sort-info"]').text
            print(episode, status)
            animes.append({"name":name, "episode":episode, "status":status, "bg":bg,
                           "url": url, "sort_info": sort_info})
        self.result = animes
        self.finder_type = self.INDEX
        print(json.dumps(animes, ensure_ascii=False))

        bases = index_driver.find_elements_by_class_name("expand")
        for base in bases:
            base.click()

        bases = index_driver.find_elements_by_xpath('//div[@class="bgm-index-nav"]/'
                                                   'div[@class="special_selector"]/'
                                                   'div[@class="special_mbox"]')
        index_paras = []
        for base in bases:
            item = {}
            item["kind"] = base.find_element_by_xpath('div[@class="left"]').text
            item["pid"] = base.find_element_by_xpath('div[contains(@class, "right")]').get_attribute("data-pid")
            item["eng_name"] = ""
            labels = base.find_elements_by_xpath('div[contains(@class, "right")]/a')
            item["label"] = []
            for label in labels:
                value = label.get_attribute("data-value")
                label_name = label.text
                item["label"].append({"name":label_name, "value": value, "used": True, "eng_name":""})
                #print(label_name, value)
            index_paras.append(item)

        label = [{"name":"追番人数", "value":"1", "used":True, "eng_name":"Popular"},
                 {"name":"更新时间", "value":"0", "used":True, "eng_name":"Updated Time"},
                 {"name":"开播时间", "value":"2", "used":True, "eng_name":"Year/Season"}]
        item = {"kind": "排序方式", "pid":"8", "eng_name":"Sort", "label":label}
        index_paras.append(item)
        print(json.dumps(index_paras, ensure_ascii=False))
        self.__update_filter(index_paras)

    def __read_filter(self):
        with open("filter.json", "r") as fin:
            filter_json = fin.read()
            fin.close()
        return json.loads(filter_json, encoding="utf-8")

    def __update_filter(self, new_obj):
        for old_kind in self.filter:
            for old_label in old_kind["label"]:
                old_label["used"] = False
            old_pid = old_kind["pid"]
            new_kind_idx = -1
            for i, new_kind in enumerate(new_obj):
                if new_kind["pid"] == old_pid:
                    new_kind_idx = i
                    break
            if new_kind_idx != -1:
                new_label_hash = {}
                for i, new_label in enumerate(new_obj[new_kind_idx]["label"]):
                    new_label_hash[new_label["value"]] = i
                print(new_label_hash)
                for old_label in old_kind["label"]:
                    old_label["name"] = new_obj[new_kind_idx]["label"][new_label_hash[old_label["value"]]]["name"]
                    old_label["used"] = True
                    del new_label_hash[old_label["value"]]
                    print(new_label_hash)
                for idx in new_label_hash.values():
                    old_kind["label"].append(new_obj[new_kind_idx]["label"][idx])
        print(json.dumps(self.filter, ensure_ascii=False))
        self.filter = new_obj
        with open("filter.json", "w") as fout:
            fout.write(json.dumps(new_obj, ensure_ascii=False))
            fout.close()

    def __create_driver(self):
        browser = Config().get_property("parameters", "browser")
        if browser == "phantomjs":
            exec_path = Config().get_property("path", "phantomjs_exec_path")
            dcap = dict(webdriver.DesiredCapabilities.PHANTOMJS)
            # Set header of request
            dcap["phantomjs.page.settings.userAgent"] = (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
                "(KHTML, like Gecko) Chrome/15.0.87"
            )
            # Not to load images
            dcap["phantomjs.page.settings.loadImages"] = False
            driver = webdriver.PhantomJS(exec_path, desired_capabilities=dcap)
        elif browser == "chrome":
            exec_path = Config().get_property("path", "chrome_driver_path")
            driver = webdriver.Chrome(executable_path=exec_path)
        else:
            print("Browser is not supported.")
            driver = None
        return driver

    def set_timeline(self, timeline):
        try:
            for day in self.result:
                test = day["date"]
                test = day["weekday"]
                for anime in day["animes"]:
                    test = anime["name"]
                    test = anime["episode"]
                    test = anime["time"]
                    test = anime["status"]
                    test = anime["url"]
                    test = anime["episode_url"]
                    test = anime["bg"]
        except KeyError as err:
            print("Invalid format of timeline object.")
            return
        else:
            self.result = timeline
            self.finder_type = self.TIMELINE

    def set_search(self, search):
        try:
            test = search["keyword"]
            for anime in search["animes"]:
                test = anime["name"]
                test = anime["desc"]
                test = anime["seasons"]
                test = anime["bg"]
                for season in anime["seasons"]:
                    test = season["name"]
                    test = season["url"]
        except KeyError as err:
            print("Invalid format of search object.")
        else:
            self.result = search
            self.finder_type = self.SEARCH


    def __display_timeline(self):
        for day in self.result:
            print('-'*20)
            print(day["date"], day["weekday"])
            for anime in day["animes"]:
                print("--%s, %s, %s, %s. Anime URL:%s, Lastest Bangumi URL:%s, Cover URL:%s"
                      % (anime["name"], anime["episode"], anime["time"], anime["status"],
                         anime["url"], anime["episode_url"], anime["bg"]))

    def __display_search(self):
        print("Search Keyword:", self.result["keyword"])
        for anime in self.result["animes"]:
            print('-'*20)
            print("Anime Name:", anime["name"])
            print("Description:", anime["desc"])
            print("Background:", anime["bg"])
            print("Seasons:")
            for season in anime["seasons"]:
                print("--Season:%s, URL:%s" % (season["name"], season["url"]))

    def display(self):
        if self.finder_type == self.NO_ASSIGNED:
            print("No content to display.")
        elif self.finder_type == self.TIMELINE:
            self.__display_timeline()
        elif self.finder_type == self.SEARCH:
            self.__display_search()
        else:
            print("No content to display.")

    def get_result(self):
        return self.result

    def get_finder_type(self):
        return self.finder_type


if __name__ == '__main__':
    finder = AnimeFinder()
    '''finder.get_timeline()
    finder.display()'''
    '''finder.search("ice")
    finder.display()'''
    finder.index([])


