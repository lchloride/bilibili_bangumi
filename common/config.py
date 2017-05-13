# coding=utf-8
import argparse
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
            with codecs.open('../settings.conf', 'r', encoding='utf-8') as f:
                Config.__instance.cp.read_file(f)
        return Config.__instance

    def get_property(self, section, option):
        if self.cp.has_option(section, option):
            return self.cp.get(section, option)
        else:
            raise NonExistedProperty("[%s] %s" %(section, option))

    def set_property(self, section, option, value):
        self.cp.set(section, option, value)
        self.cp.write(open('../settings.conf', 'w', encoding="utf-8"))

    def display_all_properties(self):
        for section in self.cp.sections():
            print("[%s]" % section)
            for option in self.cp.options(section):
                print("%s = %s" % (option, self.cp.get(section, option)))
            print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Interfaces of Configurations Operations.")
    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument("-a", "--all", action="store_true",
                        help="Display all properties.")
    group2.add_argument("-g", "--get", action="store",
                        help="Get property based on SECTION and OPTION.",
                        metavar=("SECTION","OPTION"), type=str, nargs=2)
    group2.add_argument("-s", "--set", action="store",
                        help="Set VALUE to property of SECTION and OPTION.",
                        metavar=("SECTION", "OPTION", "VALUE"), type=str, nargs=3)
    args = parser.parse_args()
    print(args)

    conf = Config()
    if args.all:
        conf.display_all_properties()
    elif args.get is not None:
        print(conf.get_property(args.get[0], args.get[1]))
    elif args.set is not None:
        conf.set_property(args.set[0], args.set[1], args.set[2])


