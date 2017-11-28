# encoding=utf-8
"""
采用异步进程方式爬取妹子图
"""
import multiprocessing
import os
import sys
import time
from multiprocessing.dummy import Lock, Pool, Queue

import requests
from fake_useragent import UserAgent
from pyquery import PyQuery as pq

rootpath = os.path.abspath('.')
path = os.path.join(rootpath, 'OOXX')
if not os.path.exists(path):
    os.mkdir(path)

multiprocessing.freeze_support()
lock = Lock()

ua = UserAgent()
headers = {}
qt = Queue(100)


def geturl(qt, num):
    urls = []
    while num > 1:
        urls.append('http://jandan.net/ooxx/page-{}'.format(str(num)))
        num -= 1
    for url in urls:
        print('页码：' + url)
        headers['User-Agent'] = ua.random
        proxies = {'http': 'socks5://127.0.0.1:1080',
                   'https': 'socks5://127.0.0.1:1080'}
        try:
            r = requests.get(url, headers=headers, proxies=proxies, timeout=9)
            r.encoding='utf-8'
            if r.encoding=='ISO-8859-1':
                r.encoding = requests.utils.get_encodings_from_content(r.content)[0]
        except(Exception) as e:
            print(e)
        respons = pq(r.text)
        # with open('html.txt','w+') as f:
        #     f.write(r.text)

        imgelem = list(respons('.view_img_link').items())
        for i in imgelem:
            imgurl = 'http:{}'.format(i.attr('href'))
            qt.put(imgurl, timeout=30)
            if qt.full():
                time.sleep(3)
        time.sleep(3)
    print('没有下一页了!')
q=multiprocessing.Manager()
def download(imgurl):
    imgname = imgurl.split('/')[-1]
    imgpath = os.path.join(path, imgname)
    statu = os.path.exists(imgpath)
    if not statu:
        headers['User-Agent'] = ua.random
        proxies = {'http': 'socks5://127.0.0.1:1080',
                   'https': 'socks5://127.0.0.1:1080'}
        try:
            r = requests.get(imgurl, headers=headers, proxies=proxies, timeout=9)
            with open(imgpath, 'wb') as f:
                f.write(r.content)
        except(Exception) as e:
            print(e)
        lock.acquire()
        print(imgname)
        lock.release()
    else:
        lock.acquire()
        print('重复  %s' % imgname)
        lock.release()


def main():
    tpool = Pool(30)
    num = int(eval(input('起始页码：')))
    tpool.apply_async(geturl, (qt, num))
    while 1:
        try:
            url = qt.get(timeout=30)
            tpool.apply_async(download, (url,))
        except(KeyboardInterrupt, SystemExit, Exception):
            tpool.terminate()
            tpool.join()
            print('结束任务！！！')
            sys.exit()
    tpool.close()
    tpool.join()


if __name__ == '__main__':
    # main()
    geturl(qt, 308)
