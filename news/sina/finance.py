#!/usr/bin/env python3
#coding:utf-8

"新浪财经"

# sina = "http://finance.sina.com.cn/china/"
# live = "http://live.sina.com.cn/zt/f/v/finance/globalnews1"

import requests
import json
import time
import os

_print = print
cmd = 0
log = 1
history_path = 'data/finance.json'
log_path = 'log/finance.log'

class UpdateError(Exception):pass
class UpdatedDuringUpdating(UpdateError):pass

def cmd_print(*args,**kw):
    def alpnumonly(string):
        buffer=[]
        for char in str(string):
            buffer.append(char if ord(char)<128 else '?')
        return ''.join(buffer)
    return _print(*map(alpnumonly,args),**kw)
if cmd: print = cmd_print

def filelog(func):
    import time
    def wrapper(*args,**kw):
        with open(log_path,'a',encoding='utf-8')as f:
            _print(time.ctime(),'LOG:',*args,file=f,**kw)
        return func(*args,**kw)
    return wrapper
if log: print = filelog(print)

def dump(obj):
    with open('data/finance.json','w',encoding='utf-8') as f:
        json.dump(obj,f,separators=(',',':'))

def load():
    if not os.path.exists('data/finance.json'): return []
    with open('data/finance.json','r',encoding='utf-8') as f:
        obj = json.load(f)
    return obj

def totalnum():
    return json.loads(requests.get(apiurl(1)).text)['result']['total']

def gettotal():
    box=[]
    for x in range(0,totalnum(),50):
        url = apiurl(50,x//50+1)
        box.extend(json.loads(requests.get(url).text)['result']['data'])
    dump(box)
    
def apiurl(num=10,page=1,**kw):
    "Num:1-50"
    base = 'http://feed.mix.sina.com.cn/api/roll/get?'
    base = 'http://feed.mix.sina.com.cn/api?'
    query = {'pageid':kw.get('pageid',155),
             'lid':kw.get('lid',1686),
             'num':num,
             'page':page}
    return base + '&'.join('%s=%s'%q for q in query.items())

def getoid():
    return tuple(n['oid'] for n in load())

def sina():
    sinajson = json.loads(requests.get(sinaurl()).text)['result']
    sinatotal = sinajson['total']
    start = time.localtime(sinajson['start'])
    end = time.localtime(sinajson['end'])
    rtime = time.localtime(sinajson['rtime'])
    data = sinajson['data']
    global si
    for item in data:
        si.append(SinaData(item))

class Data:
    def __init__(self,data=None):
        self.authoruid = data['authoruid']
        self.author = data['author']
        self.url = data['url']
        self.urls = json.loads(data['urls'])
        self.wapurl = data['wapurl']
        self.wapurls = json.loads(data['wapurls'])
        self.ctime = time.localtime(int(data['ctime']))
        self.intime = time.localtime(int(data['intime']))
        self.media_name = data['media_name']
        self.intro = data['intro']
        self.keywords = data['keywords']
        self.stitle = data['stitle']
        self.title = data['title']
        self.wapsummary = data['wapsummary']
        self.data = data
        self.oid = data['oid']
        self.time = time.ctime(int(data['ctime']))
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
        
def show(num=10,new=0):
    if not num: return
    sur = 'New:' if new else 'Old:'
    for news in load()[num-1::-1]:
        print(sur, Data(news))

def poll():
    while 1:
        time.sleep(5)
        show(len(update()),1)
        
def main():
    init()
    poll()
    
if __name__ == "__main__":
    main()
    
