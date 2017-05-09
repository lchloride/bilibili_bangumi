# coding=utf-8
from configparser import ConfigParser
import codecs


class NonExistedProperty(BaseException):
    def __init__(self, msg):
        self.args = msg


# Note that Config class is NOT thread-safe
class Config:
    __instance = None

    def __init__(self):
        pass

    def __new__(cls, *args, **kwd):
        if Config.__instance is None:
            Config.__instance = object.__new__(cls, *args, **kwd)
            Config.__instance.cp = ConfigParser()
            with codecs.open('settings.conf', 'r', encoding='utf-8') as f:
                Config.__instance.cp.read_file(f)
        return Config.__instance

    def get_property(self, section, option):
        if self.cp.has_option(section, option):
            return self.cp.get(section, option)
        else:
            raise NonExistedProperty("[%s] %s" %(section, option))

    def set_property(self, section, option, value):
        self.cp.set(section, option, value)


if __name__ == '__main__':
    conf = Config()
    conf2 = Config()
    print(conf.get_property("path", "phantomjs_exec_path"))
    print(conf2.get_property("path", "phantomjs_exec_path"))
