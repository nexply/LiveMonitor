#!/usr/bin/python
# -*- coding: utf-8 -*-
# Created on 17/12/2
__author__ = 'Mumushuimei'
import gevent.monkey ;gevent.monkey.patch_time()
import time
import random
import gevent

def peach(name):
    for i in range(1, 6):
        start_time = time.time()
        time.sleep(random.random())
        end_time = time.time()
        # 使用 round() 控制小数点位数!
        print("%s产出第%s个桃子,耗时%s"%(name, i, round(end_time - start_time, 2)))

def apple(name):
    for i in range(1, 8):
        start_time = time.time()
        time.sleep(random.random())
        end_time = time.time()
        print("%s产出第%s个苹果,耗时%s"%(name, i, round(end_time - start_time, 2)))

def main():
    # 注意:下面的语句,没有等号! 没有等号! 没有等号!
    gevent.joinall([
        gevent.spawn(peach,"LI"),
        gevent.spawn(apple,"HO"),
        ])

if __name__ == "__main__":
    main()