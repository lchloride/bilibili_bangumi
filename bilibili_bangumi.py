# coding=utf-8
from finder import PhantomJSFinder
from downloader import Downloader
bangumi_url = "http://www.bilibili.com/video/av10184012/"
finder = PhantomJSFinder(bangumi_url)
url_list = finder.getVideoURLs(True)
for url in url_list:
    name = url[:url.rfind("?")]
    name = name[url.rfind("/")+1:]
    print("Retrieve", name, url)
    Downloader().download(url, name)
