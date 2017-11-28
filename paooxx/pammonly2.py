#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# Created on 17/11/14
__author__ = 'Mumushuimei'

import multiprocessing
import os
import sqlite3
import sys
import time
from multiprocessing.dummy import Lock, Pool, Queue

import requests
from fake_useragent import UserAgent
from pyquery import PyQuery as pq


reload(sys)
sys.setdefaultencoding('utf8')
type =sys.getfilesystemencoding()
multiprocessing.freeze_support()


class mmonly:
    def __init__(self):
        self.ua = UserAgent()
        self.headers = {}
        self.q1 = Queue(300)
        self.q2 = Queue(1000)
        self.lock = Lock()
       # self.path = 'D:/IMG/'
        self.main_page_urls = []
        self.subpageurls = []
        conn = sqlite3.connect('mmonly.db')
        conn.isolation_level = None
        try:
            conn.execute(
                '''create table subpageurl(url text primary key not null)''')
            conn.execute(
                '''create table imgurl(url text primary key not null)''')
        except(Exception) as e:
            print('创建表：{}'.format(e).decode('utf-8').encode(type))
        finally:
            conn.close()
        self.rootpath = os.getcwd().replace('\\', '/')
        self.path = os.path.join(self.rootpath, 'imges/')
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def get_mainpage_urls(self, inurl):
        # 得到所有主页url
        self.headers['User-Agent'] = self.ua.random
        try:
            req = requests.get(inurl, headers=self.headers, timeout=10)
            req.encoding = 'gbk'
            cont = req.text
            content = pq(cont)
            elem = list(content('div #pageNum').children('a').items())
            for ele in elem:
                if ele.text() == '末页':
                    pgnum = int(ele.attr('href').split('_')[-1].split('.')[0])
            spurl = inurl.split('_')
            for i in range(1, pgnum + 1):
                self.main_page_urls.append(
                    '{}_{}_{}.html'.format(spurl[0], spurl[1], str(i)))
            print('主页计算完毕！！'.decode('utf-8').encode(type))
        except(Exception) as e:
            self.lock.acquire()
            print('主页读取错误：{}'.format(e).decode('utf-8').encode(type))
            self.lock.release()
            return

    def get_subpage_urls(self, inurl):
        # 得到所有子页面url
        self.headers['User-Agent'] = self.ua.random
        try:
            req = requests.get(inurl, headers=self.headers, timeout=10)
            req.encoding = 'gbk'
            cont = req.text
            content = pq(cont)
            elems = list(content('div .ABox').children('a').items())
            for ele in elems:
                url = ele.attr('href')
                self.q1.put(url)
                print('取得子页面地址：{}'.format(url).decode('utf-8').encode(type))
        except(Exception) as e:
            self.lock.acquire()
            print('遍历主页面读取错误：{}'.format(e).decode('utf-8').encode(type))
            self.lock.release()
            return

    def savesuburl(self):
        # 将子页面url存入数据库subpageurl表中

        while 1:
            try:
                suburl = self.q1.get(timeout=20)
                self.subpageurls.append(suburl)
                print('列表存入子页面：{}'.format(suburl).decode('utf-8').encode(type))
            except(Exception) as e:
                print('读取子页面url：{}'.format(e).decode('utf-8').encode(type))
                time.sleep(2)
                if self.q1.empty():
                    time.sleep(2)
                    if self.q1.empty():
                        break
        conn = sqlite3.connect('mmonly.db')
        cur = conn.cursor()
        time.sleep(4)
        print('开始将子页面url写入数据库'.decode('utf-8').encode(type))
        for date in self.subpageurls:
            try:
                cur.execute('insert into subpageurl values(?)', (date,))
                print('写入：{}'.format(date).decode('utf-8').encode(type))
            except(Exception) as er:
                print('写入数据库错误：{}'.format(er).decode('utf-8').encode(type))

        conn.commit()
        conn.close()
        print('写入完毕！！'.decode('utf-8').encode(type))

    def get_img_url(self, inurl):
        # get图片地址
        self.headers['User-Agent'] = self.ua.random
        try:
            req = requests.get(inurl, headers=self.headers, timeout=10)
            time.sleep(0.2)
            req.encoding = 'gbk'
            cont = req.text
            content = pq(cont)
            imgnum = int(content('.totalpage').text())
            urlsp = '.'.join(inurl.split('.')[:-1])
            for n in range(1, imgnum + 1):
                imgpage = '{}_{}.html'.format(urlsp, n)
                self.headers['User-Agent'] = self.ua.random
                try:
                    req = requests.get(
                        imgpage, headers=self.headers, timeout=10)
                    time.sleep(0.3)
                    req.encoding = 'gbk'
                    cont = req.text
                    content = pq(cont)
                    imgurl = content('.down-btn').attr('href')
                    self.q2.put(imgurl)
                except(Exception) as ee:
                    print('get图片url错误：{}'.format(ee).decode('utf-8').encode(type))
                print('get图片url：{}'.format(imgurl).decode('utf-8').encode(type))
        except(Exception) as e:
            print('get图片页面地址错误：{}'.format(e).decode('utf-8').encode(type))
            return

    def download(self, inurl):
        # 下载图片
        # inurl = q.get(timeout=10)
        na = inurl.split('/')
        imgname = '{}{}'.format(na[-2], na[-1])
        imgpath = '{}{}'.format(self.path, imgname)
        statu = os.path.exists(imgpath)
        if not statu:
            self.headers['User-Agent'] = self.ua.random
            try:
                req = requests.get(
                    inurl, headers=self.headers, timeout=8).content
                with open(imgpath, 'wb') as f:
                    f.write(req)
                self.lock.acquire()
                print('下载图片：{}'.format(imgname).decode('utf-8').encode(type))
                self.lock.release()
            except(Exception) as e:
                self.lock.acquire()
                print('下载错误：{}'.format(e).decode('utf-8').encode(type))
                self.lock.release()
        else:
            self.lock.acquire()
            print('重复图片：{}'.format(imgname).decode('utf-8').encode(type))
            self.lock.release()

    def run(self, inurl):
        ch = eval(input('输入1表示采集页面\n输入2表示下载图片\n输入3退出程序\n输入：'.decode(
            'utf-8').encode(type)))
        if ch == 1:
            self.get_mainpage_urls(inurl)
            time.sleep(4)
            pool1 = Pool(20)
            for mainurl in self.main_page_urls:
                pool1.apply_async(self.get_subpage_urls, (mainurl,))
            time.sleep(1)
            self.savesuburl()
            pool1.close()
            pool1.join()
            print('子页面采集完毕！！！'.decode('utf-8').encode(type))
            self.run('http://www.mmonly.cc/mmtp/list_9_2.html')
        elif ch == 2:
            conn = sqlite3.connect('mmonly.db')
            cur = conn.cursor()

            pool2 = Pool(10)
            pool3 = Pool(30)
            cur.execute('select * from subpageurl')
            suburls = cur.fetchall()

            while 1:
                for nn in range(200):
                    try:
                        for i in suburls:
                            pool2.apply_async(self.get_img_url, i)
                            cur.execute(
                                'delete from subpageurl where url=?', i)

                        while 1:
                            img = self.q2.get(timeout=20)
                            pool3.apply_async(self.download, (img,))
                    except(Exception) as e:
                        print('数据库读取子页面url：{}'.format(e).decode('utf-8').encode(type))
                        time.sleep(2)
                        if self.q2.empty():
                            time.sleep(2)
                            if self.q2.empty():
                                break

                conn.commit()
                conn.close()
                conn = sqlite3.connect('mmonly.db')
                cur = conn.cursor()
                cur.execute('select * from subpageurl')
                suburls = cur.fetchall()
                time.sleep(2)
                if self.q2.empty():
                    time.sleep(2)
                    if self.q2.empty():
                        break
            pool3.close()
            pool2.close()
            pool3.join()
            pool2.join()
        else:
            print('结束程序！'.decode('utf-8').encode(type))


if __name__ == '__main__':
    pamain = mmonly()
    pamain.run('http://www.mmonly.cc/mmtp/list_9_2.html')
