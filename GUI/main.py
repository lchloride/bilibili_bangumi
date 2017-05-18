from tkinter import *
from GUI.paracontainer import ParaContainer
from common.log import Log


class BiliBangumiUI:
    def __init__(self):
        log = Log()
        self.root = root = Tk()
        self.menubar = menubar = Menu(root)

        # Setting menu
        self.settingmenu = settingmenu = Menu(menubar, tearoff=0)
        settingmenu.add_command(label="Preference", command=hello)
        settingmenu.add_separator()
        settingmenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="Setting", menu=settingmenu)

        # Video menu
        self.videomenu = videomenu = Menu(menubar, tearoff=0)
        videomenu.add_command(label="Fetch URL", command=self.fetch_url)
        videomenu.add_command(label="Download", command=hello)
        videomenu.add_command(label="Fetch & Download", command=hello)
        menubar.add_cascade(label="Video", menu=videomenu)

        # create more pulldown menus
        self.animemenu = animemenu = Menu(menubar, tearoff=0)
        animemenu.add_command(label="Query Info", command=hello)
        self.discovermenu = discovermenu = Menu(animemenu, tearoff=0)
        discovermenu.add_command(label="Anime Timeline")
        discovermenu.add_command(label="Anime Indexes")
        discovermenu.add_command(label="Anime Searching")
        animemenu.add_cascade(label="Discover", menu=discovermenu)
        menubar.add_cascade(label="Anime", menu=animemenu)

        self.helpmenu = helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=hello)
        helpmenu.add_command(label="Help", command=hello)
        menubar.add_cascade(label="Help", menu=helpmenu)

        # display the menu
        root.config(menu=menubar)
        root.geometry('500x400+500+200')
        root.update()

        # Prepare container of parameters
        self.paraframe = paraframe = Frame(root, width=root.winfo_width(), height=200)
        paraframe.pack_propagate(0)
        paraframe.pack()
        paraframe.update()

        # Massage part
        # Message label
        self.msgframe = msgframe = Frame(root, height=400, width=root.winfo_width())
        msgframe.pack_propagate(0)
        self.msglabel = msglabel = Label(msgframe, text="Message", width=root.winfo_width(), anchor=W)
        msglabel.pack()
        # Listbox frame = listbox + scrollbar
        self.listboxframe = listboxframe = Frame(msgframe, width=root.winfo_width())
        self.scrollbar = Scrollbar(listboxframe, orient=VERTICAL)
        self.listbox = Listbox(listboxframe, yscrollcommand=self.scrollbar.set, height=10, width=70)
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
        self.listboxframe.pack()
        msgframe.pack()
        log.set_handler([self.listbox])
        print(log.handler_list)

        self.container = ParaContainer(paraframe, self.listbox)
        root.mainloop()

    def fetch_url(self):
        self.container.display(ParaContainer.FETCHVIDEOURL)


def hello():
    print("hello!")

ui = BiliBangumiUI()


