# coding = utf-8
import argparse
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
    para_key = {"8":"t", "4":"v", "2":"area", "5": "stat", "3":"y", "7":"q", "6":"tag", "9":"sort", "1":"p"}

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
        timeline_driver.get("https://bangumi.bilibili.com/anime/timeline")
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
        search_driver.get("https://search.bilibili.com/bangumi?"+parse.urlencode(para))

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

            season_ele = base.find_elements_by_xpath('ul[@class="so-episode"]/a[contains(@class, "list")]')
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

    def index(self, para={}):
        print("Initializing...")
        index_driver = self.__create_driver()
        para = self.__refine_para(para)
        print("Get anime index page... ")
        index_driver.get("https://bangumi.bilibili.com/anime/index#"+parse.urlencode(para))#p=2&v=0&area=&stat=0&y=2017&q=0&tag=&t=1&sort=0")
        print(index_driver.current_url + " Successfully finished.")
        # print(index_driver.page_source)
        print("Resolve results.")
        bases = index_driver.find_elements_by_xpath('//div[@class="v_list"]/ul[@class="v_ul"]'
                                                        '/li/div[@class="preview"]')
        animes = []

        for base in bases:
            name = base.find_element_by_xpath('div[@class="info_wrp"]/div[@class="info"]/'
                                              'a/div[contains(@class,"t")]').text
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
            # print(episode, status)
            animes.append({"name":name, "episode":episode, "status":status, "bg":bg,
                           "url": url, "sort_info": sort_info})
        self.result = animes
        self.finder_type = self.INDEX
        print("Resolve results successfully.")
        # print(json.dumps(animes, ensure_ascii=False))

        print("Update index filter.")
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
                # print(label_name, value)
            index_paras.append(item)

        label = [{"name":"追番人数", "value":"1", "used":True, "eng_name":"Popular"},
                 {"name":"更新时间", "value":"0", "used":True, "eng_name":"Updated Time"},
                 {"name":"开播时间", "value":"2", "used":True, "eng_name":"Year/Season"}]
        item = {"kind": "排序方式", "pid":"8", "eng_name":"Sort Rule", "label":label}
        index_paras.append(item)

        label = [{"name":"升序", "value":"1", "used":True, "eng_name":"Asc"},
                 {"name":"降序", "value":"0", "used":True, "eng_name":"Desc"}]
        item = {"kind": "顺序", "pid":"9", "eng_name":"Order", "label":label}
        index_paras.append(item)

        item = {"kind": "页码", "pid": "1", "eng_name": "Page", "label": []}
        index_paras.append(item)
        # print(json.dumps(index_paras, ensure_ascii=False))
        self.__update_filter(index_paras)
        print("Update index filter successfully.")

    def __refine_para(self, para):
        key = para.keys()
        refined = {}
        if "p" not in key:
            refined["p"] = '1' # Page 1
        else:
            refined = para["p"]
        if "sort" not in key:
            refined["sort"] = '0' # Desc Order
        else:
            refined["sort"] = para["sort"]
        if "t" not in key:
            refined["t"] = '1' # Sort by favorite members
        else:
            refined["t"] = para["t"]
        if "v" not in key:
            refined["v"] = "0" # Type = All
        else:
            refined["v"] = para["v"]
        if "area" not in key:
            refined["area"] = "0" # Area = All
        else:
            refined["area"] = para["area"]
        if "stat" not in key:
            refined["stat"] = "0" # Status = All
        else:
            refined["stat"] = para["stat"]
        if "y" not in  key:
            refined["y"] = "0" # Year = All
        else:
            refined["y"] = para["y"]
        if "q" not in key:
            refined["q"] = "0" # Season = All
        else:
            refined["q"] = para["q"]
        if "tag" not in key:
            refined["tag"] = "" # Tag = All
        else:
            refined["tag"] = para["tag"]
        return refined

    def __read_filter(self):
        with open("filter.json", "r") as fin:
            filter_json = fin.read()
            fin.close()
        return json.loads(filter_json, encoding="utf-8")

    def __update_filter(self, new_obj):
        kind_idx_list = []
        for idx in range(len(new_obj)):
            kind_idx_list.append(idx)
        print(kind_idx_list)
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
                # print(new_label_hash)
                for old_label in old_kind["label"]:
                    old_label["name"] = new_obj[new_kind_idx]["label"][new_label_hash[old_label["value"]]]["name"]
                    old_label["used"] = True
                    del new_label_hash[old_label["value"]]
                    # print(new_label_hash)
                for idx in new_label_hash.values():
                    old_kind["label"].append(new_obj[new_kind_idx]["label"][idx])
                kind_idx_list[new_kind_idx] = -1
        print(kind_idx_list)
        for i, new_kind in enumerate(new_obj):
            if kind_idx_list[i] != -1:
                self.filter.append(new_kind)
        # print(json.dumps(self.filter, ensure_ascii=False))
        # self.filter = new_obj
        with open("filter.json", "w") as fout:
            fout.write(json.dumps(self.filter, ensure_ascii=False))
            fout.close()

    def display_filters(self):
        print("Directions:\n  Parameters for filter are formatted as ONE JSON string with at most 9 objects.\n"
              "  Key of object means kind and value of it means label. \n"              
              "  There are 9 keys: p, t, sort, v, area, stat, y, q and tag.\n"
              "  Non-existed key means default value of this key.\n"
              "  These information can be find in the following list. \n"
              '  Example: {"area":"2", "y":"2017"} ==> AREA attribute is Japan AND YEAR attribute is 2017\n')
        print("Kind and Label List:")
        for kind in self.filter:
            print("Kind:%s(%s), Key:%s" % (kind["kind"], kind["eng_name"], self.para_key[kind["pid"]]))
            for label in kind["label"]:
                if label["used"]:
                    print("--Label:%s(%s), Value:%s" % (label["name"], label["eng_name"], label["value"]))


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

    def set_index(self, index):
        try:
            for i, anime in enumerate(self.result):
                test = anime["name"]
                test = anime["status"]
                test = anime["episode"]
                test = anime["sort_info"]
                test = anime["url"]
                test = anime["bg"]
        except KeyError:
            print("Invalid format of index object.")
        else:
            self.result = index
            self.finder_type = self.INDEX

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

    def __display_index(self):
        for i, anime in enumerate(self.result):
            print("%d. %s" % (i+1, anime["name"]))
            print("--%s %s %s" % (anime["status"], anime["episode"], anime["sort_info"]))
            print("--URL: %s" % anime["url"])
            print("--Cover URL: %s" % anime["bg"])

    def display(self):
        if self.finder_type == self.NO_ASSIGNED:
            print("No content to display.")
        elif self.finder_type == self.TIMELINE:
            self.__display_timeline()
        elif self.finder_type == self.SEARCH:
            self.__display_search()
        elif self.finder_type == self.INDEX:
            self.__display_index()
        else:
            print("No content to display.")

    def get_result(self):
        return self.result

    def get_finder_type(self):
        return self.finder_type


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="3 ways to find animes by "
                                                 "Basic search / Current season / Anime indexes."\
                                     "For other operation, please use corresponding module.")
    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument("-t", "--timeline", action="store_true",
                        help="Find animes of current season.")
    group2.add_argument("-s", "--search", action="store",
                        help="Search animes by keyword.",
                        metavar="KEYWORD", type=str)
    group2.add_argument("-i", "--index", action="store",
                        help="Find animes by indexes. Use 'finder -ft' to see format of PARAs."
                             "No PARAs will use its default value.",
                        metavar="PARAS", type=str, nargs='?', const="{}")
    group2.add_argument("-ft", "--filter", action="store_true",
                        help="Display format of PARAs when finding animes by indexes.")
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument("-j", "--json", action="store_true",
                        help="Display result in json format.")
    group1.add_argument("-l", "--list", action="store_true",
                        help="Display result in list format.")
    args = parser.parse_args()
    print(args)
    finder = AnimeFinder()
    if args.timeline:
        finder.get_timeline()
    elif args.search is not None:
        finder.search(args.search)
    elif args.index is not None:
        finder.index(json.loads(args.index))
    elif args.filter:
        finder.display_filters()

    if not args.filter:
        if args.json:
            print(json.dumps(finder.get_result(), ensure_ascii=False))
        else:
            finder.display()


