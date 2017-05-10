# coding = utf-8
import json
import time
from selenium import webdriver, common
from common.config import Config


class AnimeFinder:
    NO_ASSIGNED = 0
    TIMELINE = 1
    season = {1: 'Winter', 2: 'Winter', 3: 'Winter', 4: 'Spring', 5: 'Spring', 6: 'Spring',
              7: 'Summer', 8: 'Summer', 9: 'Summer', 10: 'Fall', 11: 'Fall', 12: 'Fall'}

    def __init__(self):
        self.finder_type = self.NO_ASSIGNED
        self.timeline = []

    def get_timeline(self):
        self.finder_type = self.TIMELINE
        print("Initializing...")
        exec_path = Config().get_property("path", "phantomjs_exec_path")
        dcap = dict(webdriver.DesiredCapabilities.PHANTOMJS)
        # Set header of request
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
            "(KHTML, like Gecko) Chrome/15.0.87"
        )
        # Not to load images
        dcap["phantomjs.page.settings.loadImages"] = False
        timeline_driver = webdriver.PhantomJS(exec_path, desired_capabilities=dcap)
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

        timeline_driver.close()
        self.timeline = timeline
        print(json.dumps(timeline, ensure_ascii=False))

    def set_timeline(self, timeline):
        try:
            test = timeline[0]
            test = timeline[0]["date"]
            test = timeline[0]["weekday"]
            test = timeline[0]["animes"]
            test = timeline[0]["animes"]["bg"]
            test = timeline[0]["animes"]["url"]
            test = timeline[0]["animes"]["name"]
            test = timeline[0]["animes"]["time"]
            test = timeline[0]["animes"]["status"]
            test = timeline[0]["animes"]["episode"]
            test = timeline[0]["animes"]["episode_url"]
        except KeyError as err:
            print("Invalid format of timeline object.")
            return
        else:
            self.timeline = timeline
            self.finder_type = self.TIMELINE

    def __display_timeline(self):
        for day in self.timeline:
            print('-'*20)
            print(day["date"], day["weekday"])
            for anime in day["animes"]:
                print("--%s, %s, %s, %s. Anime URL:%s, Lastest Bangumi URL:%s, Cover URL:%s"
                      % (anime["name"], anime["episode"], anime["time"], anime["status"],
                         anime["url"], anime["episode_url"], anime["bg"]))

    def display(self):
        if self.finder_type == self.NO_ASSIGNED:
            print("No content to display.")
        elif self.finder_type == self.TIMELINE:
            self.__display_timeline()
        else:
            print("No content to display.")


if __name__ == '__main__':
    finder = AnimeFinder()
    finder.get_timeline()
    finder.display()

