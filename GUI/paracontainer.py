from tkinter import *

from common.config import Config
from common.proxy import Proxy
import bangumi.finder
import tkinter.messagebox
from bangumi.finder import Finder, PhantomJSFinder, ChromeFinder, FinderException
from threading import Thread


class ParaContainer:
    NONE = 0
    DEFAULT = 1
    FETCHVIDEOURL = 2

    def __init__(self, frame, msg_listbox):
        self.display_type = self.NONE
        self.frame = frame
        if frame.winfo_children() is not None:
            for widget in frame.winfo_children():
                widget.destroy()
        self.__display_default()
        self.proxy = None
        self.msg_listbox = msg_listbox

    def display(self, display_type):
        self.__remove()
        if display_type == self.DEFAULT:
            self.__display_default()
        elif display_type == self.FETCHVIDEOURL:
            self.__display_fetch_video_url()

    def __remove(self, frame=None):
        if frame is None:
            frame = self.frame
        for widget in frame.winfo_children():
            if widget.winfo_children() is not None:
                self.__remove(widget)
            widget.destroy()

    def __display_default(self):
        self.display_type = self.DEFAULT
        default_label = Label(self.frame, text="Select operations in menu.", width=200, anchor=W)
        default_label.pack()

    def __display_fetch_video_url(self):
        self.display_type = self.FETCHVIDEOURL

        self.frame.update()
        left_frame = Frame(self.frame, width=int(self.frame.winfo_width()/2), bg="red", height=50,
                           padx=5)
        left_frame.pack(side=LEFT)
        left_frame.pack_propagate(0)
        left_frame.update()
        para_label = Label(left_frame, text="Parameters", anchor=W,
                           width=int(left_frame.winfo_width()))
        para_label.pack()
        url_frame = Frame(left_frame, width=left_frame.winfo_width())
        url_frame.pack()
        url_label = Label(url_frame, text="URL")
        url_label.pack(side=LEFT)
        url_label.update()
        self.url_entry = url_entry = Entry(url_frame, width=left_frame.winfo_width()-url_label.winfo_width())
        self.url_entry.pack(side=LEFT, fill=X)
        exec_btn = Button(left_frame, text="Fetch", command=self.fetch)
        exec_btn.pack(side=BOTTOM)

        right_frame = Frame(self.frame, width=self.frame.winfo_width()/2, bg="blue",padx=5)
        right_frame.pack(side=LEFT)
        self.__display_proxy(right_frame)
        right_frame.update()
        left_frame.config(height=right_frame.winfo_height())

    def __display_proxy(self, frame):
        frame.update()
        proxy_label = Label(frame, text="Proxy", width=frame.winfo_width(), anchor=W)
        proxy_label.pack()
        self.v = IntVar()
        self.v.set(0)

        notuse_rbtn = Radiobutton(frame, text="Not Use", variable=self.v, value=0,
                                  command=None)
        notuse_rbtn.pack(anchor=W)
        random_rbtn = Radiobutton(frame, text="Random", variable=self.v, value=1,
                                  command=None)
        random_rbtn.select()
        random_rbtn.pack(anchor=W)
        random_rbtn.update()
        select_rbtn = Radiobutton(frame, text="Select from List", variable=self.v, value=2,
                                  command=None)
        select_rbtn.pack(anchor=W)
        select_rbtn.deselect()

        proxy_listboxframe = Frame(frame, width=frame.winfo_width())
        proxy_scrollbar = Scrollbar(proxy_listboxframe, orient=VERTICAL)
        self.proxy_listbox = proxy_listbox = Listbox(proxy_listboxframe, yscrollcommand=proxy_scrollbar.set, height=5,
                                width=70)
        proxy_scrollbar.config(command=proxy_listbox.yview)
        proxy_scrollbar.pack(side=RIGHT, fill=Y)
        proxy_listbox.pack(side=LEFT, fill=BOTH, expand=1)
        proxy_listboxframe.pack()
        proxy = Proxy()
        proxy.load()
        for p in proxy.get_all_proxy():
            proxy_listbox.insert(END, "%s:%d" % (p["ip"], p["port"]))

    def get_proxy(self):
        print(self.v.get())
        if self.v == 1:
            self.proxy = Proxy().get_proxy()
        elif self.v == 2:
            print(self.proxy_listbox.focus_get())
            self.proxy = Proxy().get_proxy(self.proxy_listbox.focus_get())

    def fetch(self):
        url = self.url_entry.get()
        if url == "":
            tkinter.messagebox.showerror("Error", "Should have URL")
            return
        finder = create_finder(url, mode=Finder.GUI)
        result = ""
        v = self.v.get()
        print(v)

        if v == 0:
            # result = finder.get_video_url()
            th = Thread(target=finder.get_video_url)
        elif v == 1:
            # result = finder.get_video_url(Finder.RANDOM_PROXY)
            th = Thread(target=finder.get_video_url, args=(Finder.RANDOM_PROXY, ))
        elif v == 2:
            selection_tuple = self.proxy_listbox.curselection()
            if len(selection_tuple) == 0:
                tkinter.messagebox.showerror("Error", "Select a proxy.")
                return
            else:
                index = selection_tuple[0]
            print(index)
            # result = finder.get_video_url(index)
            th = Thread(target=finder.get_video_url, args=(index, ))
        th.start()


def create_finder(url, mode=Finder.CMD_LINE):
    browser = Config().get_property("parameters", "browser")
    if browser == "phantomjs":
        finder = PhantomJSFinder(url, mode)
    elif browser == "chrome":
        finder = ChromeFinder(url, mode)
    else:
        raise FinderException("Invalid selected browser.")
    return finder



