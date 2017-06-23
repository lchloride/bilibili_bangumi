# coding=utf-8
import os
import requests
from threading import Timer
from common.log import Log

USER_AGENT = 'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25'

class Downloader:
    CMD_LINE = 1
    GUI = 2

    def __init__(self, mode=CMD_LINE, progress_bar_var=None, speed_str=None):
        self.last_per = -1
        self.last_block_sec = 0
        self.current_block = 0
        self.progress = progress_bar_var
        self.mode = mode
        self.log = Log()
        self.speed_str = speed_str

    def download(self, url, name, referer='', origin='www.bilibili.com', progess=True):
        self.log.write_log("Start to download video.", self.mode)
        if self.speed_str is not None:
            timer = Timer(1, self.speed)
            timer.start()
        r = requests.get(url, stream=True,
                         headers={'User-Agent': USER_AGENT, 'Referer': referer, 'Origin': origin})
        name = os.path.dirname(os.path.dirname(os.path.abspath("downloader.py")))+"\\"+name
        print(r.headers)
        with open(name, 'wb') as f:
            l = int(r.headers["Content-Length"])
            for i, chunk in enumerate(r.iter_content(chunk_size=4096)):
                self.current_block = i
                if chunk:
                    if progess:
                        self.progess_callback(i, 4096, l)
                    f.write(chunk)
        self.log.write_log("Write video successfully. The file locates at " + name, self.mode)

        # request.urlretrieve(url, os.path.dirname(os.path.dirname(os.path.abspath("downloader.py")))+"\\"+name, self.progess_callback)

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
            if self.progress is None:
                print('%.2f%%' % per)
            else:
                self.progress.set(per)

    def speed(self):
        blocks_size = (self.current_block-self.last_block_sec)*4
        if blocks_size >= 1024*1024:
            self.speed_str.set("Speed: %.2fGB/s" % (blocks_size/(1024*1024)))
        elif blocks_size >= 1024:
            self.speed_str.set("Speed: %.2fMB/s" % (blocks_size/1024))
        else:
            self.speed_str.set("Speed: %.2fKB/s" % blocks_size)
        self.last_block_sec = self.current_block
        if self.progress.get() < 100:
            timer = Timer(1, self.speed)
            timer.start()
        else:
            self.speed_str.set("Speed: --")



if __name__ == '__main__':
    Downloader().download('http://cn-sdyt-cu-v-02.acgvideo.com/vg3/2/c1/18691321-1-hd.mp4?expires=1497546300&platform=pc&ssig=AJRQXGxD54OqW7-iaaK0MA&oi=1873074864&nfa=zlb44/URExVDmluh6FGErg==&dynamic=1&hfa=2071050155',
                          '18691321-1-hd.mp4')
