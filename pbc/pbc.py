#!/usr/bin/env python3.4

from bs4 import BeautifulSoup
import requests
import chardet
import json
import re
import tkinter
import log
import asyncio
import aiohttp

log.LOG_ON = 1
debug = None
def dump(obj,path,compress=1):
    separators=(",",":")if compress else None
    indent = None if compress else 4
    with open(path,"w") as f:
        json.dump(obj,f,separators=separators,indent=indent)
def load(path):
    with open(path) as f:
        return tuple(tuple(x)for x in json.load(f))

def dumpurl():
    br = branches()
    dump(tuple((x+(announce(x[1]),))for x in br),"branch.json")
    
def loadurl():
    "(name,host,announce)"
    try:
        res = load("branch.json")
    except FileNotFoundError:
        dumpurl()
        return loadurl()
    else:
        return res


"""
@asyncio.coroutine
def asyGET(*args,**kwargs):
    log.log("GETing",args)
    response = yield from aiohttp.request("GET", *args, **kwargs)
    if not response:
        log.log("try again",*args)
        asyGET(*args,**kwargs)
    print(response)
    log.log("GET done",args)
    return (yield from response.read_and_close())

@asyncio.coroutine
def asyBS(url,li,sem):
    with (yield from sem):
        page = yield from asyGET(url[1],compress=True)
    log.log("CDing",url[0])
    encoding = chardet.detect(page)['encoding']
    log.log("CD Done",url[0])
    log.log("BSing",url[0])
    bs = BeautifulSoup(page,"html5lib",from_encoding=encoding)
    log.log("BS Done",url[0])
    li[url[0]]=bs
    return bs


def test():
    li = {}
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    sem = asyncio.Semaphore(5,loop=loop)
    tasks = [asyBS(url,li,sem) for url in flag()]
    res = loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
    return li,res"""

def getBS(url):
    log._log("getBs(%s)"%(url,))
    import time
    time.sleep(0.1)
    req = requests.get(url)
    res = BeautifulSoup(req.content,"html5lib")
    req.close()
    return res

def branches():
    "(name,host)"
    url = "http://www.pbc.gov.cn/rmyh/105226/105442/index.html"
    table = getBS(url).find("td",attrs={"width":"720"}).findAll("table")[-1]
    return tuple(map(lambda x:(x.text,x["href"]),table.findAll("a")))

def announce(url="http://www.pbc.gov.cn/"):
    from urllib import parse
    bs = getBS(url)
    a = bs.find("a",text="公告信息") or bs.find("a",text="通知与公告")
    if not a:
        print ('trouble')
        bs = getBS(url,"")
    annurl = parse.urljoin(url,a['href'])
    return annurl

def getflag():
    from urllib import parse
    tu = loadurl()
    temp = []
    for x in tu[:]:
        print(x[0])
        if x[0].count("北京"): temp.append(x+("http://beijing.pbc.gov.cn/beijing/132024/19153/index2.html","bj",))
        elif x[0].count("上海"): temp.append(x+("http://shanghai.pbc.gov.cn/fzhshanghai/113574/13197/index2.html","sh",))
        else:
            bs = getBS(x[2])
            a = bs.find('a',text="下一页").get("tagname","")
            if not a or a.count('['): a = x[2]
            else: a = parse.urljoin(x[2],a)
            st = bs.findAll(text="公告信息 ") or bs.findAll(text="公告信息")
            st = st[-1]
            st = st.findParent("table").findNextSibling()
            hi = st.findChildren("tr")
            if len(hi) == 1:
                if st.findNextSibling().findNextSibling():
                    temp.append(x+(a,"ttdd",))
                else:temp.append(x+(a,"ttd",))
            else: temp.append(x+(a,"tdt",))
    dump(temp,"flags.json")
def flag(): return load("flags.json") # (name, host, announce, index, type)

class News:
    def __init__(self):
        pass
    def __repr__(self):
        return "\n"+"\n".join("%s: %s"%(k,v) for k,v in sorted(self.__dict__.items()))+"\n"

class Branch:
    def __new__(cls,flag=None,*args,**kw):
        if flag is None:
            return super().__new__(cls)
        elif flag[4] == "ttd":
            return super().__new__(TTD)
        return super().__new__(cls)
    def __init__(self,flag=None):
        flag = flag or ("",)*5
        self.name, self.host, self.announce, self.pages, self.type = flag
        self.item, self.num, self.data = 0, 0, []
    def index(self,page):
        if page == 1: return self.announce
        match = re.match(r"(.*?index)\d*(\.html$)",self.pages)
        if match:
            return str(page).join(match.groups())
    def __repr__(self):
        return self.name
    def do(self):return []

class TTD(Branch):
    def __init__(self,flag=None):
        super().__init__(flag)
        if self.type != "ttd":raise ValueError("Need TTD")
        self.getPages()

    @log.log
    @log.track
    def getPages(self):
        bs = getBS(self.announce)
        self.item = int(re.findall("共(\\d+)条", bs.text)[0])
        self.num = int(re.findall("分(\\d+)页", bs.text)[0])
        return self.item, self.num
        """string = bs.findAll(text="公告信息 ") or bs.findAll(text="公告信息")
        string = string[-1]
        target = string.findParent("table").findNextSibling().findNextSibling()
        pages = target.contents[3] if len(target.contents)>3 else target.findChild("tr").findNextSibling()
        pages = pages.findChild("td")
        pages = pages.findChild("td") or pages
        self.num = int((re.findall("分(\\d+)页", pages.text))[0])
        if self.num > 0:
            from urllib import parse
            self.pages = parse.urljoin(self.host,(pages.findChild("a",text="下一页")or{}).get("tagname",self.announce))
            if self.pages.count("["):self.pages = self.announce
            print(self.pages)"""
        
    def ttd(self):
        for x in range(self.num):
            url = self.index(x+1)
            bs = getBS(url)
            string = bs.findAll(text="公告信息 ") or bs.findAll(text="公告信息")
            if not string:
                print(url,self.name,self.announce)
            string = string[-1]
            target = string.findParent("table").findNextSibling().findNextSibling()
            lists = target.findChild("ul") or target.contents[1]
            if lists.name == "ul":
                lists = lists.findChildren("li")
            else:
                lists = tuple(x.findParent("td") for x in lists.findChildren("a"))
                lists = tuple(x for x in lists if not re.match("\\s*共\\d+条",x.text))
            for td in lists:
                temp = News()
                a = td.findChild("a")
                temp.href = a["href"]
                temp.title1 = a["title"]
                temp.title2 = a.text
                temp.date = td.contents[-1]
                self.data.append(temp)
        return self.data
    do = ttd
                 

    
#ttd:table, separator, target(list+pages)
for url in flag()[:0]:
    if url[-1]!="ttd":continue
    print(url[0],url[2])
    bs = getBS(url[2])
    string = (bs.findAll(text="公告信息 ") or bs.findAll(text="公告信息"))[-1]
    target = string.findParent("table").findNextSibling().findNextSibling()

    lists = target.findChild("ul") or target.contents[1]# or target.findChild("tr")
    pages= target.contents[3] if len(target.contents)>3 else target.findChild("tr").findNextSibling()
    if lists.name == "ul":
        lists = lists.findChildren("li")
    elif lists.name == "tdr":
        lists = lists.findChildren("tr")
    else:
        lists = tuple(x.findParent("td") for x in lists.findChildren("a"))
        lists = tuple(x for x in lists if not re.match("\\s*共\\d+条",x.text))
         
    pages = pages.findChild("td")
    pages = pages.findChild("td") or pages
    num = (re.findall("分(\\d+)页", pages.text))
    



    print(num)
    for td in lists:

        a = td.findChild("a")
        href = a["href"]
        title1 = a["title"]
        title2 = a.text
        date = td.contents[-1]

        
        #print(href)
        print(title1,date,href)
        #print(title2)
    print()



class MainWindow(tkinter.Toplevel):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.withdraw()
        self.root = master
        self.title("各分行公告信息")
        self.geometry("800x600+50+50")
        self.resizable(height=1,width=1)
        self.after(500, lambda: self.focus_force())
        self.menubar=self.MenuBar(self)
        self.main_frame = self.MainFrame(self)
        self.protocol("WM_DELETE_WINDOW",self.makesure)
        self.pack()
        self.deiconify()
    def pack(self):
        self.main_frame.pack(fill=tkinter.BOTH,side=tkinter.TOP,expand="yes")
    def makesure(self):
        self.destroy()
        self.root.destroy()
    class MainFrame(tkinter.Frame):
        def __init__(self,parent=None,cnf={},**kw):
            kw.update({"height":600,"width":800,"bg":"red"})
            super().__init__(parent,cnf,**kw)
            self.root, self.top = parent.root, parent
            self.branches = []
            self.left = self.LeftFrame(self)
            self.right = self.RightFrame(self)
            self.left.poll()
        class LeftFrame(tkinter.Frame):
            def __init__(self,master=None,cnf={},**kw):
                self.root, self.top = master.root, master.top
                kw.update({"height":600,"width":300,"bg":"green"})
                super().__init__(master,cnf,**kw)
                self.pack(fill=tkinter.Y,side=tkinter.LEFT,expand="no")
                self.list = self.List(self)
            def poll(self):
                now = self.list.curselection()
                if now and now != self.master.right.current:
                    self.master.right.current = now
                    self.master.right.show()
                self.after(100,self.poll)
            class List(tkinter.Listbox):
                def __init__(self,master=None,cnf={},**kw):
                    self.root, self.top = master.root, master.top
                    kw.update({"width":20,"height":37})
                    super().__init__(master,cnf,**kw)
                    self.after(1000,self.getlist)
                    self.pack(fill=tkinter.BOTH,side=tkinter.LEFT,expand="yes")
                def poll(self):
                    self.id = self.after(100,self.poll)
                    pipe = self.root.pipe
                    branches = self.master.master.branches
                    if pipe.poll():
                        succ, res = pipe.recv()
                        if succ:
                            log.log("suss kakunin",res)
                            branches.append(res)
                            if res: self.insert(tkinter.END,res.name)     
                        if len(branches) is len(flag()):
                            self.insert(tkinter.END,"全部")
                            self.after_cancel(self.id)
                        else:
                            pipe.send(("Branch(flag()[%d])"%len(branches),))
                def getlist(self):
                    self.root.pipe.send(("Branch(flag()[%d])"%0,))
                    self.id = self.after(100, self.poll)
                        
        class RightFrame(tkinter.Frame):
            def __init__(self,master=None,cnf={},**kw):
                self.root, self.top = master.root, master.top
                kw.update({"height":600,"width":490,"bg":"yellow"})
                super().__init__(master,cnf,**kw)
                self.pack(fill=tkinter.BOTH,side=tkinter.LEFT,expand="yes")
                self.br = self.master.branches
                self.current=[-1]
                self.listindex=[-1]
                self.list = self.List(self)
                self.poll()
            class List(tkinter.Listbox):
                def __init__(self,master=None,cnf={},**kw):
                    kw.update({})
                    super().__init__(master,cnf,**kw)
                    self.pack(fill=tkinter.BOTH,side=tkinter.LEFT,expand="yes")
                    self.scrollbar = tkinter.Scrollbar(self.master, command=self.yview)
                    self.configure(yscrollcommand=self.scrollbar.set)
                    self.scrollbar.pack(fill=tkinter.Y,side=tkinter.RIGHT,before = self)
            def show(self):
                try:self.after_cancel(self.id)
                except:pass
                self.list.delete(0,tkinter.END)
                if self.current[0] == len(self.br):
                    self.list.insert(0,"%s"%"全部")
                else:
                    sub = self.br[self.current[0]]
                    self.list.insert(0,"%s 分%d页 共%d条"%(sub.name,sub.num,sub.item))
                if len(self.master.branches) == len(flag()): self.showdetail()
            def showdetail(self):
                if self.current[0] == len(flag()):
                    self.showall()
                else:
                    task = self.br[self.current[0]]
                    if task.data:self.showdata()
                    else:
                        self.root.pipe.send(("task.do()",{},{"task":task}))
                        self.list.insert(tkinter.END,"%s"%"显示详细内容")
                        self.waitresult()
            def waitresult(self):
                try:self.after_cancel(self.id)
                except:pass
                log.log("Waiting",self.current[0])
                self.list.insert(tkinter.END,"连接中，请稍候！")
                if self.root.pipe.poll():
                    log.log("Got",self.current[0])
                    succ, temp = self.root.pipe.recv()
                    self.br[self.current[0]].data=temp
                    self.after_cancel(self.id)
                    self.showdata()
                else:self.id=self.after(1000,self.waitresult)
            def showall(self):
                self.list.delete(1,tkinter.END)
                self.list.insert(tkinter.END,"暂不支持")
            def showdata(self):
                self.list.delete(1,tkinter.END)
                for item in self.br[self.current[0]].data:
                    self.list.insert(tkinter.END,"%s %s"%(item.title1,item.date))
            def poll(self):
                now = self.list.curselection()
                if now and now != self.listindex:
                    self.listindex = now
                    self.tryopen()
                self.after(100,self.poll)
            def tryopen(self):
                br_index = self.current[0]
                if br_index == len(flag()):return
                item_index = self.listindex[0]
                if item_index == 0:return
                data = self.br[br_index].data[item_index-1]
                from urllib import parse
                url = parse.urljoin(self.br[br_index].host,data.href)
                self.open(url,data.title1)
            @staticmethod
            def open(url,title):
                from webbrowser import open
                try:from tkinter import messagebox
                except ImportError:
                    import tkinter.messagebox
                    messagebox = tkinter.messagebox
                if messagebox.askyesno(title,"是否要打开网址 %s ?"%url):
                    return open(url)
                
    class MenuBar(tkinter.Menu):
        def __init__(self,parent=None,cnf={},**kw):
            super().__init__(parent,cnf,**kw)
            self.root = parent.root
            self.menus = {"FileMenu":self.FileMenu(self),
                          }
            parent.config(menu=self)
        class FileMenu(tkinter.Menu):
            def __init__(self,menubar=None,cnf={},**kw):
                kw.pop("tearoff",None)
                super().__init__(menubar,cnf,tearoff=0,**kw)
                self.add_command(label="退出",command=lambda:menubar.root.destroy())
                menubar.add_cascade(menu=self,label="文件")
        
    

@log.log
def main():
    from multiprocessing import Process, Pipe
    tEnd, aEnd = Pipe()
    pt = Process(target=ptkinter,args=(tEnd,),name="thinter")
    pa = Process(target=pasync,args=(aEnd,),name="async")
    pt.start()
    pa.start()
    pt.join()
    pa.terminate()
    
    

def ptkinter(pipe):
    pipe.send, pipe.recv =log.track(pipe.send), log.track(pipe.recv)
    global debug
    log.open()
    debug = root = tkinter.Tk(className="pbc")
    root.pipe = pipe
    pipe.send(("123+456",))
    if pipe.poll(0.1):
        log.log('This should be (stat:1,res:579):',pipe.recv())
    root.withdraw()
    root.MainWindow = MainWindow(root)
    root.mainloop()
    try:root.destroy()
    except:pass
    log.close()

def pasync(pipe):
    pipe.send, pipe.recv =log.track(pipe.send), log.track(pipe.recv)
    c = consumer()
    c.send(None)
    while True:
        if not pipe.poll():continue
        task = pipe.recv()
        log.log("Got task: %s"%(task,))
        if task == "close":
            c.close()
            break
        res = c.send(task)
        log.log("Got res: %s %s"%res)
        if res[0]:
            log.log("Succ: %s"%task[0])
            pipe.send(res)
        else:
            log.log("Failed: %s"%task[0])
            pipe.send(res)
            

def consumer():
    import traceback
    r = ''
    while True:
        n = yield r
        if not n:
            return
        try: res = eval(*n)
        except:
            r = 0, None
            log.log("Failed.", traceback.format_exc())
        else: r = 1, res
                


if __name__ == "__main__":
    """debug  = test()
    for x in flag():
        if x[0] not in debug[0]:
            print(x)
    for x in debug[1][0]:
        print("%s\n\n"%x)"""
    main()




"""
tar = tar.findNext("tbody").findNext("tbody").findChild("tr")
body = tar.findChildren("tr")
pages = tar.findNextSibling().findChild("td").findChild("td")

num = (re.findall("分(\d+)页", pages.text))
"""
#"""
    

