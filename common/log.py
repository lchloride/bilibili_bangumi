# coding=utf-8

from queue import Queue
from tkinter import *
import sys

import threading
from common.BaseThread import BaseThread

class Log(object):
    __instance = None

    def __init__(self):
        # Log.__instance.string_pool = Queue(max_size)
        # Log.__instance.handler_list = handler_list
        pass

    def __new__(cls, *arg, **kwargs):
        if Log.__instance is None:
            Log.__instance = object.__new__(cls, *arg, **kwargs)
            Log.__instance.string_pool = Queue(500)
            Log.__instance.handler_list = []
            Log.__instance.thread = BaseThread(display_log,
                                               Log.__instance.string_pool,
                                               'log_thread')
            '''Log.__instance.thread = threading.Thread(target=display_log,
                                                     args=(Log.__instance.string_pool, ))'''
            Log.__instance.thread.setDaemon(True)
            Log.__instance.thread.start()
        return Log.__instance

    # 完成一条内容的输出，输出内容不保证即刻执行
    # flag表示待输出的设备，0为退出线程，1为输出到屏幕
    def write_log(self, content, flag):
        string_set = {"flag": flag, "content": content, "handler": self.__instance.handler_list}
        self.string_pool.put(string_set)

    def kill(self):
        item = {"flag": 0x0, "content": None}
        self.string_pool.put(item)

    def get_thread(self):
        return self.thread

    @staticmethod
    def get_instance():
        return Log.__instance

    def set_handler(self, handler_list):
        Log.__instance.handler_list = handler_list


# 向屏幕/文件输出信息的线程体
def display_log(string_pool):
    while True:
        string_set = string_pool.get()
        handler_list = string_set["handler"]
        if string_set["flag"] == 0:
            break
        elif string_set["flag"] == 1:
            print(string_set["content"])
        else:
            handler = handler_list[string_set["flag"]-2]
            if isinstance(handler, Listbox):
                '''handler.activate(0)
                handler.insert(ACTIVE, string_set["content"])'''
                handler.insert(END, string_set["content"])
                handler.yview_moveto(1.0)
                handler.update_idletasks()
            else:
                handler.write(string_set["content"]+"\n")
