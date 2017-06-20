from time import ctime
import threading

class BaseThread(threading.Thread):
    def __init__(self, func, args, name='', download_func=None):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.url = args[0]
        self.download_func = download_func
        self.res = None
        self.referer = args[1] if len(args)>=2 else ""

    def getResult(self):
        return self.res

    def run(self):
        print('starting %s at: %s' %(self.name, ctime()))
        self.res = self.func(self.url)
        if self.download_func is not None and self.download_func.__name__ == 'download'\
                and self.referer is not None:
            for video_url in self.res:
                name = video_url[:video_url.rfind("?")]
                name = name[name.rfind("/") + 1:]
                self.download_func(video_url, name, self.referer)
        print('%s finished at: %s' %(self.name, ctime()))
