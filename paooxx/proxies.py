#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on 17/11/11
__author__ = 'Mumushuimei'

import multiprocessing
import random
import sqlite3
import time
from multiprocessing.dummy import Pool

import requests
from fake_useragent import UserAgent

from pyquery import PyQuery as pq

ua = UserAgent()
header = {}
multiprocessing.freeze_support()
lock = multiprocessing.Lock()


def getip(num=10):
    # input('页数：')
    urls = []
    # 打开数据库
    conn = sqlite3.connect('ip.db')
    # 这个就是事务隔离级别，默认是需要自己commit才能修改数据库，置为None则自动每次修改都提交,否则为""
    conn.isolation_level = None
    # 获取到游标对象
    c = conn.cursor()
    # 用游标来查询就可以获取到结果
    try:
        c.execute('''create table allip(ip text primary key not null)''')
    except(Exception) as e:
        print(e)

    # with open('D:/PYProgram/paooxx/ip.txt','r') as f:
    #     ips=f.readlines()
    # for i in ips:
    #     ip=i.split('\n')[0]
    #     try:
    #         c.execute('insert into allip values (?)', (ip,))
    #         print '加入IP：{}'.format(ip)
    #     except(Exception)as e:
    #         print e
    for i in range(num):
        urls.append('http://www.kuaidaili.com/free/inha/{}/'.format(i + 1))

    for url in urls:
        header['UserAgent'] = ua.random
        # proxies={'http':'218.56.132.157:8080'}

        try:
            respons = requests.get(url, headers=header,
                                   timeout=10).content  # , proxies=proxies
            respons = pq(respons)
        except:
            print('翻页错误：{}'.format(e))
            continue

        time.sleep(random.random() + 1)
        print('第 {} 页。'.format(url))
        elem = list(respons('tr').items())
        for i in elem:
            datas = i('[data-title]').text().split(' ')
            if len(datas) > 1:
                ip = datas[0]
                port = datas[1]
                ipurl = '{}:{}'.format(ip, port)
                try:
                    c.execute('insert into allip values (?)', (ipurl,))
                    print('加入IP：{}'.format(ipurl))
                except(Exception) as e:
                    print(e)
    conn.close()


def urltest(url):
    header['UserAgent'] = ua.random
    proxies = {'http': url}
    try:
        respons = pq(requests.get('http://www.baidu.com',
                                  headers=header, proxies=proxies, timeout=9).content)
        res = respons('body').attr('link')
        print(res)
        if res != '#0000cc':
            lock.acquire()
            print('代理失效：{}'.format(url))
            # print respons
            lock.release()
            return url
        # respons = requests.get('http://jandan.net/ooxx', headers=header, proxies=proxies, timeout=5)
        # res = respons.status_code
        # if res != 200:
        #     lock.acquire()
        #     print '代理失效：{}'.format(url)
        #     # print respons
        #     lock.release()
        #     return url
        lock.acquire()
        print('测试通过：{} 返回 {}'.format(url, res))
        lock.release()
    except(Exception) as e:
        lock.acquire()
        print('代理失效：{}'.format(url))
        # print e
        lock.release()
        return url


def iptest():
    # 打开数据库
    conn = sqlite3.connect('ip.db')
    # 这个就是事务隔离级别，默认是需要自己commit才能修改数据库，置为None则自动每次修改都提交,否则为""
    conn.isolation_level = None
    # 获取到游标对象
    c = conn.cursor()
    # 用游标来查询就可以获取到结果
    c.execute('select * from allip')

    results = []

    pool = Pool(30)
    while 1:
        re = c.fetchone()
        if re is None:
            break
        url = re[0]
        result = pool.apply_async(urltest, (url,))
        results.append(result)
    pool.close()
    pool.join()

    for i in results:
        badip = i.get()
        c.execute('delete from allip where ip=?', (badip,))

    c.execute('select * from allip')
    mel = c.fetchall()
    for i in mel:
        print(i[0])
    # 关闭数据库
    conn.close()


def nihao():
    pass


if __name__ == '__main__':
    a = eval(input('输入1：获取ip\n输入2：测试ip:'))
    if a == 1:
        getip(20)
    elif a == 2:
        iptest()
