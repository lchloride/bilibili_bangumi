import codecs
from configparser import ConfigParser


class Language(object):
    __instance = None

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if Language.__instance is None:
            Language.__instance = object.__new__(cls, *args, **kwargs)
            Language.__instance.cp = ConfigParser()
            with codecs.open('../common/lang.conf', 'r', encoding='utf-8') as f:
                Language.__instance.cp.read_file(f)

        return Language.__instance

    def get_string(self, key, lang):
        if self.cp.has_section(key) and self.cp.has_option(key, lang):
            return self.cp.get(key, lang)
        else:
            return ""

