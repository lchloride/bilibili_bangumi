# coding=utf-8
from finder import PhantomJSFinder, ChromeFinder, FinderException
from downloader import Downloader
from config import Config
import argparse


def create_finder(url):
    browser = Config().get_property("parameters", "browser")
    if browser == "phantomjs":
        finder = PhantomJSFinder(url)
    elif browser == "chrome":
        finder = ChromeFinder(url)
    else:
        raise FinderException("Invalid selected browser.")
    return finder


def main():
    parser = argparse.ArgumentParser(description="Fetch and download bangumi video from bilibili website. "\
                                     "For other operation, please use corresponding module.")
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument("-f", "--fetch", action="store",
                       help="Fetch video real URL from bangumi playing page like 'www.bilibili.com/video/av10366622'.",
                       metavar="BANGUMI_URL")
    group1.add_argument("-d", "--download", action="store",
                       help="Download video from storage server by URL like 'http://cn-jsks2-dx.acgvideo.com/vg8/2/dc/16824755-1-hd.mp4?...'(parameters omitted)",
                       metavar="VIDEO_URL")
    group1.add_argument("-fd", action="store",
                       help="Fetch and download video from bangumi playing page like 'www.bilibili.com/video/av10366622'.",
                       metavar="BANGUMI_URL")
    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument("-rp", "--randproxy", action="store_true",
                        help="Using random proxy server.")
    group2.add_argument("-p", "--proxy", action="store", help="Using proxy server with specific index",
                        metavar="INDEX", type=int)
    '''parser.add_argument("-c", "--config", action="store",
                        help="Use configuration file. If configuration file is not assigned, default one will be used.",
                        default="settings.conf", metavar="FILE")'''
    args = parser.parse_args()

    if args.fetch is not None:
        print("fetch")
        finder = create_finder(args.fetch)
        if args.proxy is not None:
            print(finder.getVideoURLs(True))
        else:
            print(finder.getVideoURLs())
    elif args.download is not None:
        print("download")
        name = args.download[:args.download.rfind("?")]
        name = name[args.download.rfind("/") + 1:]
        downloader = Downloader().download(args.download, name)
    elif args.fd is not None:
        print("fetch & download")
        finder = create_finder(args.fd)
        if args.proxy is not None:
            url_list = finder.getVideoURLs(True)
        else:
            url_list = finder.getVideoURLs()
        for url in url_list:
            name = url[:url.rfind("?")]
            name = name[url.rfind("/") + 1:]
            print("Retrieve", name, url)
            Downloader().download(url, name)

    if args.proxy is not None:
        print("proxy")
    elif args.randproxy is not None:
        print("random proxy")

    print(args)


if __name__ == '__main__':
    main()
