#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import chardet
import json
import re

__log = 1

def log(*args, **kwargs):
    if __log:print(*args, **kwargs)

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
    try:
        res = load("branch.json")
    except FileNotFoundError:
        dumpurl()
        return loadurl()
    else:
        return res

def getBS(url,encoding=None):
    if encoding is None:
        return BeautifulSoup(requests.get(url).content,"html5lib")
    content = requests.get(url).content
    encoding = encoding or chardet.detect(content)
    return BeautifulSoup(content,"html5lib",from_encoding=encoding)

def branches():
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

def announcelist(url=None):
    if url is None: return

def getflag():
    tu = loadurl()
    temp = []
    for x in tu[:]:
        if x[0].count("北京"): temp.append(x+("bj",))
        elif x[0].count("上海"): temp.append(x+("sh",))
        else:
            bs = getBS(x[2])
            st = bs.findAll(text="公告信息 ") or bs.findAll(text="公告信息")
            st = st[-1]
            st = st.findParent("table").findNextSibling()
            hi = st.findChildren("tr")
            if len(hi) == 1:
                if st.findNextSibling().findNextSibling():
                    temp.append(x+("ttdd",))
                else:temp.append(x+("ttd",))
            else: temp.append(x+("tdt",))
    dump(temp,"flags.json")
def flag(): return load("flags.json")

class News:
    def __init__(self):
        pass
    def __repr__(self):
        return "\n"+"\n".join("%s: %s"%(k,v) for k,v in sorted(self.__dict__.items()))+"\n"

class Branch:
    def __new__(cls,flag=None,*args,**kw):
        if flag is None:
            return super().__new__(cls)
        elif flag[3] == "ttd":
            return super().__new__(TTD)
    def __init__(self,flag=None):
        flag = flag or ("",)*4
        self.name, self.host, self.announce, self.type = flag
        self.num, self.data, self.pages = 0, [], self.announce
    def index(self,page):
        if page == 1: return self.announce
        match = re.match(r"(.*?index)\d*(\.html$)",self.pages)
        if match:
            return str(page).join(match.groups())
    def __repr__(self):
        return self.name

class TTD(Branch):
    def __init__(self,flag=None):
        super().__init__(flag)
        if self.type != "ttd":raise ValueError("Need TTD")
        self.getPages()
        
    def getPages(self):
        bs = getBS(self.announce)
        string = bs.findAll(text="公告信息 ") or bs.findAll(text="公告信息")
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
            print(self.pages)
        
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




"""
tar = tar.findNext("tbody").findNext("tbody").findChild("tr")
body = tar.findChildren("tr")
pages = tar.findNextSibling().findChild("td").findChild("td")

num = (re.findall("分(\d+)页", pages.text))
"""
#"""
    

