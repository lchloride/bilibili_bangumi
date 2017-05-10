# coding=utf-8

from urllib import request


class Downloader:
    def __init__(self):
        self.last_per = -1

    def download(self, url, name, progess=True):
        if progess:
            request.urlretrieve(url, "../"+name, self.progess_callback)
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
    pass
