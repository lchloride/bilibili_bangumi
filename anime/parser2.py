# coding=utf-8
import argparse
import json
import re
from urllib import request

days = {"0":"星期日", "1":"星期一", "2":"星期二", "3":"星期三", "4":"星期四", "5":"星期五", "6":"星期六"}
class Anime():
    def __init__(self):
        self.info = None

    def fetch_anime(self, url):
        if not re.match("(https?://)?bangumi.bilibili.com/anime/\d*\S*", url):
            print("Anime URL should formatted like bangumi.bilibili.com/anime/1234.")
            return
        else:
            url = url[url.find("bangumi.bilibili.com"):]
            paras = url.split("/")
            anime_idx = paras[2]
            # print(anime_idx)
            info_url = "http://bangumi.bilibili.com/jsonp/seasoninfo/%s.ver?callback=seasonListCallback&jsonp=jsonp" \
                       % anime_idx

            req = request.Request(info_url)
            req.add_header('User-Agent',
                           'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25')
            req.add_header('Referer', 'https://bangumi.bilibili.com/')
            info_obj = None
            with request.urlopen(req) as f:
                if f.status != 200:
                    print('Failed to fetch information.\nStatus:', f.status, f.reason)
                    for k, v in f.getheaders():
                        print('%s: %s' % (k, v))
                else:
                    info_json = f.read().decode('utf-8')
                    # The content starts with "seasonListCallback(" and ends up with ")"
                    info_obj = json.loads(info_json[19:-2], encoding='utf-8')

            if info_obj is None or info_obj["code"] != 0:
                print("Cannot fetch information properly.")
                return
            if "allow_bp" in info_obj["result"].keys() and info_obj["result"]["allow_bp"] == "1":
                data = "season_id=%s&page=1&pagesize=7" % anime_idx

                req = request.Request('https://bangumi.bilibili.com/sponsor/rankweb/get_sponsor_total')
                req.add_header('User-Agent',
                               'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25')
                req.add_header('Referer', 'https://bangumi.bilibili.com/')

                with request.urlopen(req, data=data.encode('utf-8')) as f:
                    if f.status != 200:
                        print('Status:', f.status, f.reason)
                        for k, v in f.getheaders():
                            print('%s: %s' % (k, v))
                    else:
                        sponsor_obj = json.loads(f.read().decode('utf-8'), encoding='utf-8')
                        info_obj["result"]["sponsors_count"] = sponsor_obj["result"]["users"]
            self.info = info_obj

    def display(self):
        if self.info is None:
            print("No information to display.")
            return
        else:
            try:
                result = self.info["result"]
                print("番剧标题:", result["title"])
                if "jp_title" in result.keys():
                    print("原标题:", result["jp_title"])
                print("地区:", result["area"])
                print("封面图片地址:", result["cover"])
                print("番剧URL:", result["share_url"])
                s = ""
                for i in range(len(result["tags"])):
                    if i == 0:
                        s += result["tags"][i]["tag_name"]
                    else:
                        s += ", " + result["tags"][i]["tag_name"]
                print("类型:", s)
                print("播放量:", result["play_count"])
                print("追番人数:", result["favorites"])
                print("弹幕数量:", result["danmaku_count"])
                print("硬币数量:", result["coins"])
                if result["is_finish"] == "1": # Finished
                    print("更新状态: 已完结 共%s话" % len(result["episodes"]))
                    print("开播时间:", result["pub_time"][0:10])
                elif result["is_finish"] == "0" and result["is_started"] == 1:
                    if result["weekday"] == "-1":
                        print("更新状态: 连载中 更新未定")
                    else:
                        print("更新状态: 连载中 %s %s更新" % (days[result["weekday"]], result["pub_time"][-8:-3]))
                    print("开播时间:", result["pub_time"][0:10])
                elif result["is_started"] == 0:
                    print("更新状态: 未开播")
                    print("开播时间:", result["pub_time"])
                print("声优：")
                role_len = 0
                actor_len = 0
                for i in range(len(result["actor"])):
                    if len(result["actor"][i]["role"]) > role_len:
                        role_len = len(result["actor"][i]["role"])
                    if len(result["actor"][i]["actor"]) > actor_len:
                        actor_len = len(result["actor"][i]["actor"])
                for i in range(len(result["actor"])):
                    print("  %s %s %s"
                          % (result["actor"][i]["role"],
                             '一'*(role_len-len(result["actor"][i]["role"])+2),
                             result["actor"][i]["actor"]))

                # Re-formatted introduction
                brief_display = True
                if (len(result) >= 4 and result["brief"][:-3] in result["evaluate"]) or \
                        (result["brief"] in result["evaluate"]):
                    brief_display = False

                eva = result["evaluate"].split("\n")
                result["evaluate"] = ""
                for e in eva:
                    if e != "":
                        result["evaluate"] += e + "\n     "
                result["evaluate"] = result["evaluate"][:-6]
                print("介绍:", result["evaluate"])
                if brief_display:
                    print("     ", result["brief"])
                if result["allow_bp"] == "1":
                    print("承包人数:", result["sponsors_count"])
                if "staff" in result.keys():
                    staff = result["staff"].split("\n")
                    print("制作人员:")
                    for s in staff:
                        if s != "":
                            print("  ", s)

                # Episodes
                print("剧集列表:")
                for i in range(len(result["episodes"])):
                    if result["episodes"][i]["index"].isdigit():
                        print("  第%s话: 标题: %s; URL: %s; 封面图片: %s"
                              % (result["episodes"][i]["index"],
                                 result["episodes"][i]["index_title"],
                                 result["episodes"][i]["webplay_url"],
                                 result["episodes"][i]["cover"]))
                    elif result["episodes"][i]["index_title"] != "":
                        print("  %s: 标题: %s; URL: %s; 封面图片: %s"
                              % (result["episodes"][i]["index"],
                                 result["episodes"][i]["index_title"],
                                 result["episodes"][i]["webplay_url"],
                                 result["episodes"][i]["cover"]))
                    else:
                        print("  %s: 标题: %s; URL: %s; 封面图片: %s"
                              % (result["episodes"][i]["index"],
                                 result["episodes"][i]["index"],
                                 result["episodes"][i]["webplay_url"],
                                 result["episodes"][i]["cover"]))

                # Other Seasons
                print("分季列表：")
                print("  当前:", result["season_title"])
                if len(result["seasons"]) > 0:
                    for i in range(len(result["seasons"])):
                        print("  其他: %s; URL: https://bangumi.bilibili.com/anime/%s"
                              % (result["seasons"][i]["title"], result["seasons"][i]["season_id"]))
            except KeyError as err:
                print("Broken information.")
                raise err


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Obtain information of anime using its URL."\
                                     "For other operation, please use corresponding module.")
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument("-j", "--json", action="store_true",
                        help="Display result in json format.")
    group1.add_argument("-l", "--list", action="store_true",
                        help="Display result in list format.")
    parser.add_argument("URL")
    args = parser.parse_args()

    anime = Anime()
    anime.fetch_anime(args.URL)
    if args.json:
        print(json.dumps(anime.info, ensure_ascii=False))
    elif args.list:
        anime.display()
    else:
        anime.display()
