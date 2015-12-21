#!/usr/bin/env python3
#coding:utf-8

# Web:
# live = "http://live.sina.com.cn/zt/f/v/finance/globalnews1"
# sina = "http://finance.sina.com.cn/china/"
# roll = "http://roll.news.sina.com.cn/s/channel.php"

# API:
# http://live.sina.com.cn/api/?p=zt&s=tfin&a=cjsyqcrss&special_symbol=globalnews1&channel_symbol=finance&dpc=1
# http://live.sina.com.cn/zt/api/f/get/finance/globalnews1/index.htm?id=254716&tag=0&pagesize=45&dire=f
import requests
import json
import time
import re
import asyncio

url = "http://roll.news.sina.com.cn/interface/rollnews_ch_out_interface.php?"
"&spec=&type=2&date=&ch=01&k=&offset_page=1&offset_num=0&num=1&asc=&page=1"

debug = None
found = []

def ensureascii(string):
    box = []
    for s in string:
        if not s.isprintable(): continue
        box.append(s if ord(s) < 256 else "\\u%04x"%ord(s))
    return ''.join(box)


def js2json(url):
    return ensureascii(re.sub(r"'(\d*)'",lambda x:'"%s"'%x.group(1),\
                              re.sub(r'[{,]\s*([a-zA-Z_$][0-9a-zA-Z_$]*)\s*:',
                             lambda x:x.group(0)[:x.start(1)-x.start(0)]+'"'\
                             +x.group(1)+'"'+x.group(0)[x.end(1)-x.start(0):],\
                                     requests.get(url).content.split\
                                     (b'var jsonData = ')[-1].decode('GB18030')))\
                       .replace(';',''))

class UpdateError(Exception):pass
class UpdatedDuringUpdating(UpdateError):pass

def pr(x):
    url='http://roll.news.sina.com.cn/interface/rollnews_ch_out_interface.php?col=%s&num=1'%x
    print(json.dumps(js2json(url),ensure_ascii=0,indent=4,sort_keys=1))

def index(x=368):
    "新闻频道目录"
    url="http://roll.news.sina.com.cn/interface/rollnews_ch_out_interface.php?num=1&col="
    res = []
    with open('channels.log','w',encoding='utf-8') as f:
        f.write('%s\t%s\t%s\n'%('col','id','title'))
    for i in range(1,x):
        temp = json.loads(js2json(url+str(i)))
        tt = (i,temp['path'][0]['id'],temp['path'][0]['title'])
        print(tt)
        res.append(tt)
        with open('channels.log','a',encoding='utf-8') as f:
            f.write('%s\t%s\t%s\n'%tt)
    return res
            
            
            
        

def newsapi(**kw):
    base = "http://roll.news.sina.com.cn/interface/rollnews_ch_out_interface.php?"
    query = {'page':kw.get('page',1),
             'num':kw.get('num',1),
             'col':kw.get('col','0')
             }
    return base + '&'.join('%s=%s'%q for q in query.items())


def newget():
    res = json.loads(js2json(newsapi(col=43,num=10)))
    for item in res['list']:
        print(item['title'])
def get(url):
    try:
        res = []
        for a in requests.get(url).json()['result']['data']:
            print(a['title'])
            res.append(a)
    except:pass
    else:
        return res

def apiurl(num=10,page=1,**kw):
    "Num:1-50"
    base = 'http://feed.mix.sina.com.cn/api/roll/get?'
    query = {#'pageid':kw.get('pageid',155),
             'lid':kw.get('lid',1686),
             'num':num,
             'page':page}
    return base + '&'.join('%s=%s'%q for q in query.items())

def dump(obj):
    with open('data/news.json','w',encoding='utf-8') as f:
        json.dump(obj,f,separators=(',',':'))

def load():
    if not os.path.exists('data/news.json'): return []
    with open('data/news.json','r',encoding='utf-8') as f:
        obj = json.load(f)
    return obj

def find():
    global debug, found
    for pageid in range(1687):
        print(pageid,end='|',sep='')
        for lid in range(156):
            test(apiurl(1,pageid=pageid,lid=lid))
            if debug['status']['code']:
                print(lid,end='|',sep='')
                continue
            print(lid,pageid)
            found.append((lid,pageid))

def test(url=None):
    global debug
    if url is None:return
    result = json.loads(requests.get(url).text)['result']
    #print(result['status'])
    debug = result
    

si=[]

def query(qu={}):
    base = 'http://api.roll.news.sina.com.cn/zt_list?'
    return base + '&'.join('%s=%s'%q for q in qu.items())

def comp(s1,s2):
    base = 'http://api.roll.news.sina.com.cn/zt_list?'
    return get(base+s1),get(base+s2)
    
    
def sina(url=None):
    if url is None:
        url='http://api.roll.news.sina.com.cn/zt_list'
        '?channel=news&cat_1=gnxw'
        '&cat_2==gdxw1||=gatxw||=zs-pl||=mtjj'
        '&level==1||=2'
        '&show_ext=1'#0
        '&show_all=1'#0
        '&show_num=22'#20
        '&tag=1'
        '&format=json'
        '&page=1'#1
    sinajson = json.loads(requests.get(url).text[21:-2])['result']
    sinatotal = sinajson['total']
    #start = time.localtime(sinajson['start'])
    #end = time.localtime(sinajson['end'])
    #rtime = time.localtime(sinajson['rtime'])
    data = sinajson['data']
    global si
    for item in data:
        si.append(SinaData(item))

class SinaData:
    def __init__(self,data=None):
        #self.authoruid = data['authoruid']
        #self.author = data['author']
        self.url = data['url']
        #self.urls = json.loads(data['urls'])
        #self.wapurl = data['wapurl']
        #self.wapurls = json.loads(data['wapurls'])
        #self.ctime = time.localtime(int(data['createtime']))
        #self.intime = time.localtime(int(data['intime']))
        self.media_name = data['media_name']
        #self.intro = data['intro']
        self.keywords = data['keywords']
        #self.stitle = data['stitle']
        self.title = data['title']
        self.ext5 = data['ext5']
        self.data = data
        self.oid = data['id']
        self.time = time.ctime(int(data['createtime']))
    def __repr__(self):
        return "%s: 《%s》  via %s"%(self.time,self.title,self.media_name)
def init():
    update()
    show(10)

def trytrytry(exc=None):
    if exc is None: exc = UpdatedDuringUpdating
    def decorator(func):
        def wrapper(*args,**kw):
            while 1:
                try: res=func(*args,**kw)
                except exc as e: print(e, 'Try again')
                else: return res
        return wrapper
    return decorator

@trytrytry()
def update():
    total = totalnum()
    flag = 0
    new = []
    oids = getoid()
    page = 1
    while 1:
        li = json.loads(requests.get(apiurl(10,page)).text)['result']
        if li['total'] != total:
            raise UpdatedDuringUpdating
        li = li['data']
        if not li: break
        for news in li:
            if news['oid'] in oids:
                flag = 1
                break
            new.append(news)
        if flag: break
        page += 1
    if new:
        dump(new+load())
    return new
        
def show(num=10):
    if not num: return
    for news in load()[num-1::-1]:
        print(Data(news))

def poll():
    while 1:
        time.sleep(5)
        show(len(update()))

@asyncio.coroutine
def hello():
    print("hello")
    t = yield from asyncio.sleep(1)
    print("hello again %s"%t)
        
def main():
    init()
    poll()
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait([hello(),hello(),hello()]))
    loop.close()
    pass
    #main()
    
