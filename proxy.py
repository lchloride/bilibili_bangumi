# coding=utf-8

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

    def load(self, filename="proxy.json"):
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

        if idx >= l or idx < 0:
            idx = -1
        if idx == -1:
            idx = randint(0, len(self.__instance.proxy_list)-1)

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

if __name__ == '__main__':
    proxy = Proxy()
    proxy.load()
    print(proxy.get_proxy())
    proxy.set_proxy('61.191.41.130', 80)