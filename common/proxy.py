# coding=utf-8
import argparse
import json
from random import randint


class ProxyException(BaseException):
    def __init__(self, msg):
        self.args = msg


class Proxy:
    __instance = None

    def __init__(self):
        pass

    def __new__(cls, *args, **kwd):
        if Proxy.__instance is None:
            Proxy.__instance = object.__new__(cls, *args, **kwd)
            Proxy.__instance.proxy_list = []
            Proxy.__instance.filename = ""
        return Proxy.__instance

    def load(self, filename="../proxy.json"):
        self.__instance.filename = filename
        try:
            fin = open(filename, "r")
        except IOError:
            print("Cannnot open file ", filename)
            self.__instance.proxy_list = []
        json_str = fin.readline()
        fin.close()
        try:
            json_obj = json.loads(json_str, encoding="utf-8")
        except json.JSONDecodeError:
            print("Cannot resolve string in file", filename)
            self.__instance.proxy_list = []
        else:
            self.__instance.proxy_list = json_obj

    def get_proxy(self, idx=-1):
        l = len(self.__instance.proxy_list)
        if l == 0:
            raise ProxyException("No available proxy")

        # idx out of range
        if idx >= l or idx < 1:
            idx = -1
        # random idx OR modify idx to base 0
        if idx == -1:
            idx = randint(0, len(self.__instance.proxy_list)-1)
        else:
            idx -= 1

        ip = "%s:%d" % (self.__instance.proxy_list[idx]["ip"], self.__instance.proxy_list[idx]["port"])
        return ip

    def set_proxy(self, ip, port):
        new_proxy = {"ip": ip, "port": port}
        if new_proxy not in self.__instance.proxy_list:
            self.__instance.proxy_list.append(new_proxy)
        self.__dump()

    def delete_proxy(self, ip, port):
        delete_proxy = {"ip": ip, "port": port}
        self.__instance.proxy_list.remove(delete_proxy)
        self.__dump()

    def __dump(self):
        fout = open(self.__instance.filename, "w")
        json_str = json.dumps(self.__instance.proxy_list)
        fout.write(json_str)
        fout.close()

    def get_all_proxy(self):
        return self.proxy_list

    def display_all(self):
        for i, proxy in enumerate(self.proxy_list):
            print("%d. IP: %s, Port: %s" % (i+1, proxy["ip"], proxy["port"]))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Interfaces of Proxy Operations.")
    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument("-a", "--all", action="store_true",
                        help="Display all proxies.")
    group2.add_argument("-g", "--get", action="store",
                        help="Get proxy in the position of INDEX.",
                        metavar="INDEX", type=int)
    group2.add_argument("-i", "--insert", action="store",
                        help="Insert new proxy with IP and port.",
                        metavar=("IP", "PORT"), type=str, nargs=2)
    group2.add_argument("-d", "--delete", action="store",
                        help="Delete proxy with IP and port.",
                        metavar=("IP", "PORT"), type=str, nargs=2)

    args = parser.parse_args()
    print(args)

    proxy = Proxy()
    proxy.load()
    if args.all:
        proxy.display_all()
    elif args.delete is not None:
        proxy.delete_proxy(args.delete[0], int(args.delete[1]))
    elif args.insert is not None:
        proxy.set_proxy(args.insert[0], int(args.insert[1]))
    elif args.get is not None:
        print(proxy.get_proxy(args.get))
