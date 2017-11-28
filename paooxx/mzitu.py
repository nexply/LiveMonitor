#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on 17/11/25
__author__ = 'Mumushuimei'
import os
import sqlite3
import sys
import time
from multiprocessing.dummy import Pool, Queue

import requests
import logging
from fake_useragent import UserAgent
from pyquery import PyQuery as pq

code = sys.getfilesystemencoding()
logging.basicConfig(filename='mzitu.log',level=logging.WARNING)

class mzitu:
    def __init__(self):
        self.starturl = 'http://www.mzitu.com/all/'
        self.ua = UserAgent()
        self.qu = Queue(1000)
        self.qu2 = Queue(1000)
        self.suburls = []
        self.oldmurls = []
        conno=sqlite3.connect('mzituoldu.db')
        try:
            conno.execute('create table oldmurls(url text primary key)')
        except(Exception) as e:
            print('创建表ou:{}'.format(e))
        conno.close()
        conns = sqlite3.connect('mzitusubu.db')
        try:
            conns.execute('create table suburls(url text primary key,status int default 1)')
        except(Exception) as e:
            print('创建表su:{}'.format(e))
        conns.close()

    def gethtml(self, url):
        headers = {}
        headers['User-Agent'] = self.ua.random
        headers['Referer'] = url
        try:
            resp = requests.get(url, headers=headers, timeout=8)
            if resp.encoding == 'ISO-8859-1':
                resp.encoding = requests.utils.get_encodings_from_content(resp.content)[0]
            html = pq(resp.text)
            cont = resp.content
            return html, cont
        except(Exception) as e:
            print('gethtml错误：{}'.format(e))
            logging.warning('gethtml错误：{}'.format(e))
            return None, None

    def getmurl(self):
        resp = self.gethtml(self.starturl)[0]
        if resp != None:
            elem = resp('.all')('a').items()
            murls = {}
            for ele in elem:
                murl = ele.attr('href')
                title = ele.text()
                murls[murl] = title
            return murls
        else:
            print('murl未get到网页内容！')
            logging.warning('murl未get到网页内容！')
            return None

    def getsuburl(self, url):
        resp = self.gethtml(url)[0]
        if resp != None:
            elem = resp('.pagenavi').children('a')
            num = int(elem.eq(-2).children('span').text())
            for i in range(1, num + 1):
                suburl = '{}/{}'.format(url, i)
                try:
                    self.qu.put(suburl, timeout=60)
                except(Exception) as e:
                    print('qu.put Error:{}'.format(e))
            self.qu2.put(url)
            print('已get完：{}'.format(url))
        else:
            print('suburl未get到网页内容！')
            logging.warning('suburl未get到网页内容！')

    def getimgurl(self, url):

        try:
            resp = self.gethtml(url)[0]
            if resp != None:
                elem = resp('.main-image')('img').attr('src')
                title = resp('.currentpath').next('h2').text()
                return elem, title
            else:
                print('imgurl未get到网页内容！')
                logging.warning('imgurl未get到网页内容！')
                return None, None
        except(Exception) as e:
            print('getimgurlE:{}'.format(e))
            logging.warning('getimgurlE:{}'.format(e))

    def mkdir(self, rootpath=os.path.abspath('.'), dir='mzitu'):
        global path
        path = os.path.join(rootpath, dir)
        if not os.path.exists(path):
            os.mkdir(path)

    def download(self, url, ):
        imgurl = self.getimgurl(url)
        global path
        imgname = '{}{}{}'.format(imgurl[0].split('/')[-3], imgurl[0].split('/')[-2], imgurl[0].split('/')[-1])
        imgpath = os.path.join(path, imgname)
        statu = os.path.exists(imgpath)
        headers = {}
        if not statu:
            for t in range(2):
                headers['User-Agent'] = self.ua.random
                headers['Referer'] = url
                headers['Host'] = 'i.meizitu.net'
                try:
                    resp = requests.get(imgurl[0], headers=headers, timeout=8)
                    with open(imgpath, 'wb') as f:
                        f.write(resp.content)
                    print('下载：{}'.format(imgurl[0]))
                    break
                except(Exception) as e:
                    print('下载图片错误：{}'.format(e))
                    logging.warning('下载图片错误：{}'.format(e))
                    time.sleep(5)
        else:
            print('已下载：{}'.format(imgname))

    def savesuburl(self):
        i=0
        conn=sqlite3.connect('mzitusubu.db')
        cur=conn.cursor()
        suburls = []
        while 1:
            try:
                suburl = (self.qu.get(timeout=20),)
                suburls.append(suburl)
                i+=1
                if i>=2000:
                    cur.executemany('insert or ignore into suburls(url) values(?)',suburls)
                    conn.commit()
                    suburls = []
                    i=0
            except(Exception) as e:
                print('suburls Error:{}'.format(e))
                cur.executemany('insert or ignore into suburls(url) values(?)', suburls)
                conn.commit()
                cur.close()
                conn.close()
                break
        print('保存suburl')

    def saveoldmurl(self):
        conn=sqlite3.connect('mzituoldu.db')
        cur=conn.cursor()
        oldmurls = []
        while 1:
            try:
                oldmurl = (self.qu2.get(timeout=20),)
                oldmurls.append(oldmurl)
            except(Exception) as e:
                print('oldmurl Error:{}'.format(e))
                cur.executemany('insert or ignore into oldmurls(url) values(?)',oldmurls)
                conn.commit()
                oldmurls=[]
                cur.close()
                conn.close()
                break
        print('保存oldmurl')

    def run(self):
        self.mkdir(rootpath='D:/QMDownload')
        murls = self.getmurl()

        pool1 = Pool(50)
        pool1.apply_async(self.savesuburl)
        pool1.apply_async(self.saveoldmurl)

        conno = sqlite3.connect('mzituoldu.db')
        oldurls = conno.execute('select url from oldmurls').fetchall()
        conno.close()
        for murl in murls:
            omurl = (murl,)
            if omurl not in oldurls:
                pool1.apply_async(self.getsuburl(murl, ))
                # oldurls.append(omurl)
            else:
                print('{}已经下过了'.format(murl))
        pool1.close()
        pool1.join()

        pool2 = Pool(20)
        conns=sqlite3.connect('mzitusubu.db')
        cur=conns.cursor()
        while 1:
            surls = cur.execute('select url from suburls where status=1').fetchmany(300)
            if surls == []:
                break
            oldsurls = []
            for surl in surls:
                pool2.apply_async(self.download, (surl[0],))
                oldsurls.append(surl)
            time.sleep(8)
            cur.executemany('update suburls set status=2 where url=?', oldsurls)
            conns.commit()
        cur.close()
        conns.close()
        pool2.close()
        pool2.join()
        print('下载完成！！！！')


if __name__ == '__main__':
    mzitu = mzitu()
    mzitu.run()
