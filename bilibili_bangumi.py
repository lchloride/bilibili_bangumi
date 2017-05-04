# coding=utf-8
from finder import Finder
from downloader import Downloader
bangumi_url = "https://www.bilibili.com/video/av1965419/"
finder = Finder(bangumi_url)
url_list = finder.getVideoURLs()
for url in url_list:
    name = url[:url.rfind("?")]
    name = name[url.rfind("/")+1:]
    print("Retrieve", name, url)
    Downloader().download(url, name)
