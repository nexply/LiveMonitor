#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on 17/11/12
import multiprocessing
import os
import random
import sqlite3
from queue import Queue
from multiprocessing.dummy import Pool

import requests
from bs4 import BeautifulSoup

__author__ = 'Mumushuimei'

import time
from selenium import webdriver
from fake_useragent import UserAgent

ua = UserAgent()
headers = {}
q = Queue(50)
lock = multiprocessing.Lock()
rootpath = os.getcwd().replace('\\', '/')
path = os.path.join(rootpath, 'imges/')
if not os.path.exists(path):
    os.mkdir(path)


def geturl():
    # word = input('输入查找词：')
    options = webdriver.ChromeOptions()
    options.add_argument('lang=zh_CN.UTF-8')
    options.add_argument('user-agent={}'.format(ua.random))
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option('prefs', prefs)

    driver = webdriver.Chrome(chrome_options=options)
    driver.maximize_window()  # 窗口最大化

    fmq = '{}{}'.format(int(time.time()), random.randint(100, 999))
    url = 'https://image.baidu.com/search/index?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&fmq={}_R&pv=&ic=0&nc=1&z=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&word={}'.format(
        fmq, '情欲诱惑学生')
    try:
        driver.get(url)
        driver.w
    except(Exception) as e:
        print(e)

    while 1:
        pag1 = len(driver.page_source)
        for i in range(10):
            driver.execute_script('document.documentElement.scrollTop=100000')
            # time.sleep(random.random()/4)
        print(pag1, '滚动网页')
        pag2 = len(driver.page_source)
        if pag1 == pag2:
            print('已经到达页面底部！！')
            break
    time.sleep(0.5)

    content = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(content, 'html.parser')
    elems = soup.find_all(class_='imgitem')
    time.sleep(5)
    driver.quit()
    # 打开数据库
    conn = sqlite3.connect('imgurls.db')
    # 这个就是事务隔离级别，默认是需要自己commit才能修改数据库，置为None则自动每次修改都提交,否则为""
    conn.isolation_level = None
    # 获取到游标对象
    c = conn.cursor()
    # 用游标来查询就可以获取到结果
    try:
        c.execute('''create table urls(url text primary key not null,status int default 1)''')
    except(Exception) as e:
        print(e)
    # urllist = []
    nu = 1
    for i in elems:
        print('提取下载地址存入数据库：{}'.format(nu))
        nu += 1
        ur = i['data-objurl']
        # urllist.append((ur,))
        try:
            c.execute('insert into urls values (?,?)', (ur, 1))
        except(Exception) as e:
            print(e)
        print(ur)

    conn.close()


def readurl(q):
    # 打开数据库
    conn = sqlite3.connect('imgurls.db')
    # 这个就是事务隔离级别，默认是需要自己commit才能修改数据库，置为None则自动每次修改都提交,否则为""
    conn.isolation_level = None
    # 获取到游标对象
    c = conn.cursor()
    # 用游标来查询就可以获取到结果
    try:
        c.execute('select * from urls where status=1')
    except(Exception) as e:
        print(e)
    selecs = c.fetchall()
    for selec in selecs:
        q.put(selec[0])
        try:
            c.execute('update urls set status=2 where url=?', (selec[0],))
        except(Exception) as e:
            print(e)
    conn.close()


def download(url):
    # url = q.get(timeout=5)
    imgname = url.split('/')[-1]
    imgpath = '{}{}'.format(path, imgname)
    statu=os.path.exists(imgpath)
    if not statu:
        headers['User-Agent'] = ua.random
        try:
            resp = requests.get(url, headers=headers, timeout=5).content
            with open(imgpath, 'wb') as f:
                f.write(resp)
            lock.acquire()
            print('下载图片：{}'.format(imgname))
            lock.release()
        except(Exception) as e:
            lock.acquire()
            print(e)
            lock.release()

    else:
        lock.acquire()
        print('重复图片：{}'.format(imgname))
        lock.release()


def run():
    pool = Pool(30)
    pool.apply_async(readurl, (q,))
    time.sleep(1)
    while 1:
        try:
            url = q.get(timeout=10)
            pool.apply_async(download, (url,))
        except(KeyboardInterrupt, SystemExit, Exception) as e:
            print(e)
            print('结束！！？？')
            pool.terminate()
            pool.join()
            break
    pool.close()
    pool.join()


if __name__ == '__main__':
    geturl()
    run()
