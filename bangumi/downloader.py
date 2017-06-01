# coding=utf-8
import os
from urllib import request


class Downloader:
    def __init__(self):
        self.last_per = -1

    def download(self, url, name, progess=True):
        if progess:
            request.urlretrieve(url, os.path.dirname(os.path.dirname(os.path.abspath("downloader.py")))+"\\"+name, self.progess_callback)
        else:
            request.urlretrieve(url, "../"+name)

    def progess_callback(self, a, b, c):
        '''''回调函数 
        @a:已经下载的数据块 
        @b:数据块的大小 
        @c:远程文件的大小 
        '''
        per = round(100.0 * a * b / c, 0)
        if per > 100:
            per = 100
        if per != self.last_per:
            self.last_per = per
            print('%.2f%%' % per)


if __name__ == '__main__':
    Downloader().download('http://cn-bjsj-cc-v-03.acgvideo.com/vg3/f/47/3299010-1-hd.mp4?expires=1496343600&platform=pc&ssig=NBeOMOtPJsv0JlTc_l-ADA&oi=3698530067&nfa=zlb44/URExVDmluh6FGErg==&dynamic=1&hfa=2063801976',
                          '13989517-1-hd.mp4')
