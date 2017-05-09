# coding=utf-8

from selenium import webdriver
from config import Config
from proxy import Proxy


class Anime():
    RANDOM_PROXY = -1
    NO_PROXY = -2

    def __init__(self):
        pass

    def fetch_anime(self, url, proxy_idx=NO_PROXY):
        exec_path = Config().get_property("path", "phantomjs_exec_path")
        print("Initializing")
        dcap = dict(webdriver.DesiredCapabilities.PHANTOMJS)
        # Set header of request
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
            "(KHTML, like Gecko) Chrome/15.0.87"
        )
        # Not to load images
        dcap["phantomjs.page.settings.loadImages"] = False
        if proxy_idx != self.NO_PROXY:
            # Set proxy which is randomly chosen from proxy list
            proxy = Proxy()
            proxy.load()
            service_args = ['--proxy=' + proxy.get_proxy(proxy_idx), '--proxy-type=http']
            anime_driver = webdriver.PhantomJS(executable_path=exec_path, desired_capabilities=dcap, service_args=service_args)
        else:
            anime_driver = webdriver.PhantomJS(executable_path=exec_path, desired_capabilities=dcap)

        print("Load anime page")
        anime_driver.set_page_load_timeout(Config().get_property("time", "page_load_timeout"))
        anime_driver.get(url)

        print("Resolve information")
        # print(anime_driver.page_source)

        bg = anime_driver.find_element_by_xpath('//div[@class="main-inner"]/div[@class="info-content"]/'
                                                 'div[@class="bangumi-preview"]/img').get_property("src")
        title = anime_driver.find_element_by_xpath('//div[@class="main-inner"]/div[@class="info-content"]/'
                                                   'div[@class="bangumi-info-r"]/div[@class="b-head"]/'
                                                   'h1[@class="info-title"]').text
        tag_ele = anime_driver.find_elements_by_xpath('//div[@class="main-inner"]/div[@class="info-content"]/'
                                                   'div[@class="bangumi-info-r"]/div[@class="b-head"]/'
                                                   'a/span[@class="info-style-item"]')
        tags = []
        for tag in tag_ele:
            tags.append(tag.text)
        play = anime_driver.find_element_by_xpath('//div[@class="main-inner"]/div[@class="info-content"]/'
                                                  'div[@class="bangumi-info-r"]/div[@class="info-count"]/'
                                                  'span[contains(@class, "info-count-item-play")]/em').text
        favorite = anime_driver.find_element_by_xpath('//div[@class="main-inner"]/div[@class="info-content"]/'
                                                      'div[@class="bangumi-info-r"]/div[@class="info-count"]/'
                                                      'span[contains(@class, "info-count-item-fans")]/em').text
        danmaku = anime_driver.find_element_by_xpath('//div[@class="main-inner"]/div[@class="info-content"]/'
                                                     'div[@class="bangumi-info-r"]/div[@class="info-count"]/'
                                                     'span[contains(@class, "info-count-item-review")]/em').text
        update_date_ele = anime_driver.find_elements_by_xpath('//div[@class="main-inner"]/div[@class="info-content"]/'
                                                          'div[@class="bangumi-info-r"]/div[@class="info-row info-update"]/'
                                                          'em/span')
        update_dates = ""
        for date in update_date_ele:
            update_dates += ", "+date.text
        # There is a Chinese caesura sign before cv's name.
        # Cv stands for character voice whose Japanese name is Seiyuu(声優).
        js = 'document.getElementsByClassName("info-cv")[0].style.overflow = "visible"'
        anime_driver.execute_script(js)
        cv_ele = anime_driver.find_elements_by_xpath('//div[@class="main-inner"]/div[@class="info-content"]/'
                                                  'div[@class="bangumi-info-r"]/div[@class="info-row info-cv"]/'
                                                  'em/span[@class="info-cv-item"]')
        changed_idx = []
        for i in range(len(cv_ele)):
            if cv_ele[i].is_displayed():
                pass
            else:
                changed_idx.append(str(i))
                js = 'document.getElementsByClassName("info-cv-item")['+str(i)+'].style.display = "block"'
                anime_driver.execute_script(js)
                i -= 1

        cvs = []
        for i in range(len(cv_ele)):
            # print(cv_ele[i].text, cv_ele[i].is_displayed())
            if i == 0:
                cvs.append(cv_ele[i].text)
            else:
                cvs.append(cv_ele[i].text[1:])

        for idx in changed_idx:
            js = 'document.getElementsByClassName("info-cv-item")[' + idx + '].style.display = "inline"'
            anime_driver.execute_script(js)

        desc = anime_driver.find_element_by_xpath('//div[@class="main-inner"]/div[@class="info-content"]/'
                                                  'div[@class="bangumi-info-r"]/div[@class="info-row info-desc-wrp"]/'
                                                  'div[@class="info-desc"]').text
        episode_ele = anime_driver.find_elements_by_xpath('//a[@class="v1-complete-text"]')
        episodes = []
        for episode_link in episode_ele:
            item = {}
            item["link"] = episode_link.get_attribute("href")
            item["title"] = episode_link.get_attribute("title")
            img_ele = episode_link.find_element_by_tag_name("img")
            item["image"] = img_ele.get_attribute("src")
            episodes.append(item)

        sponsor = anime_driver.find_element_by_xpath('//div[contains(@class, "sponsor-tosponsor")]'
                                                     '/span').text
        similar_ele = anime_driver.find_elements_by_xpath('//li[@class="similar-list-child"]/a/'
                                                      'div[@class="similar-name"]/'
                                                      'div[@class="similar-name-l"]')
        similar = []
        for s in similar_ele:
            if s.is_displayed():
                similar.append(s.text)

        js = 'document.getElementsByClassName("v1-bangumi-list-season-wrapper")[0].style.display="block"'
        anime_driver.execute_script(js)
        anime_driver.save_screenshot("page.png")
        season_ele = anime_driver.find_element_by_class_name('v1-bangumi-list-season').find_elements_by_tag_name("li")
        seasons = []
        for season in season_ele:
            item = {"name": season.text,
                    "cur": True if season.get_attribute("class") == "cur" else False,
                    "link": "bangumi.bilibili.com/anime/"+season.get_attribute("data-season-id")}
            seasons.append(item)

        anime_driver.close()
        json_obj = {"bg": bg, "title": title, "tags": tags, "play": play, "favorite": favorite,
                    "danmaku": danmaku, "update_date": update_dates, "cvs": cvs, "desc": desc,
                    "episodes": episodes, "sponsor": sponsor, "similar": similar, "seasons": seasons}
        return json_obj

    def display(self, obj):
        print("Background image URL:", obj["bg"])
        print("Anime title:", obj["title"])
        s = ""
        for i in range(len(obj["tags"])):
            if i == 0:
                s += obj["tags"][i]
            else:
                s += ", " + obj["tags"][i]
        print("Anime tags:", s)
        print("Play times:", obj["play"])
        print("Favorite:", obj["favorite"])
        print("Danmaku count:", obj["danmaku"])
        print("Update date:", obj["update_date"])
        s = ""
        for i in range(len(obj["cvs"])):
            if i == 0:
                s += obj["cvs"][i]
            else:
                s += ", " + obj["cvs"][i]
        print("CVs:", s)
        print("Description:", obj["desc"])
        print("Seasons:")
        for season in obj["seasons"]:
            print("Name: %s%s, Link: %s" % (season["name"], "(current)" if season["cur"] else "", season["link"]))
        print("Episodes:")
        for episode in obj["episodes"]:
            print("Title: %s, Link: %s, Image URL: %s" % (episode["title"], episode["link"], episode["image"]))
        print("Sponsors:", obj["sponsor"])
        s = ""
        for i in range(len(obj["similar"])):
            if i == 0:
                s += obj["similar"][i]
            else:
                s += ", " + obj["similar"][i]
        print("Similar animes:", s)


if __name__ == '__main__':
    anime = Anime()
    obj = anime.fetch_anime("http://bangumi.bilibili.com/anime/5997")
    # print(obj)
    anime.display(obj)
