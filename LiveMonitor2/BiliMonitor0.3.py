#!/usr/bin/python3
# Created on 17/11/10
__author__ = 'Mumushuimei'

import configparser
import json
import logging
import os
import subprocess
import sys
import time

import requests
from fake_useragent import UserAgent

code = sys.getdefaultencoding()


def log():
    # create logger
    logger = logging.getLogger('Bili')
    # Set default log level
    logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    ch2 = logging.FileHandler('bili.log')
    ch2.setLevel(logging.WARNING)

    # create formatter
    formatter = logging.Formatter('%(asctime)s_%(name)s_%(levelname)s: %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)
    ch2.setFormatter(formatter)

    # add ch to logger
    # The final log level is the higher one between the default and the one in handler
    logger.addHandler(ch)
    logger.addHandler(ch2)
    return logger


def tim(Tim):
    for tt in range(Tim):
        n = tt + 1
        wid = 45
        pr = int(wid * n / Tim)
        sys.stdout.write(' ' * (wid + 15) + '\r')
        sys.stdout.flush()
        sys.stdout.write(u'##等待时间：{:3}/{:3}s# '.format(n, Tim))
        sys.stdout.write('{}{}{}'.format('>' * pr, '-' * (wid - pr), '#'))
        sys.stdout.flush()
        time.sleep(1)
        sys.stdout.write('\r')


class monitor:
    # 监控主体
    def __init__(self):
        self.status = {}
        self.rooms = {}
        cop = configparser.ConfigParser()
        cop.read('uplist.txt', encoding='utf-8')
        for op in cop.options('bili'):
            self.rooms[op] = cop.get('bili', op)
            self.status[self.rooms[op]] = 0
        log.info('Uplist:{}'.format(self.rooms))
        self.ua = UserAgent()

    def getlist(self):
        # code = sys.getfilesystemencoding()
        url = 'https://api.live.bilibili.com/i/api/following?page=1&pageSize=80'
        headers = {'User-Agent': self.ua.random,
                   'cookie':}
        try:
            r = requests.get(url, headers=headers)
            if (r.status_code == requests.codes.ok):
                # pprint.pprint(r.json())
                resul = r.json()['data']['list']
                log.info('成功获取关注列表！                ')
                return resul
        except(Exception) as e:
            log.warning('获取关注列表错误：{}                '.format(e))
            return []

    def find(self):
        uplist = self.getlist()
        for up in self.rooms:
            upname = self.rooms[up]
            log.info('=================================')
            log.info('监控: %s' % upname)
            for r in uplist:
                if r['uname'] == upname:
                    log.info('Bili房间：{}'.format(r['title'][:12]))
                    if r['live_status'] == 1:
                        self.status[upname] += 1
                        log.info('%s 正在直播！！！' % r['uname'])
                        if self.status[upname] == 1:
                            try:
                                log.info('发送通知短信！！！')
                                rms = subprocess.check_output(
                                    ['python2', os.path.join(os.path.abspath('.'), 'dysmsapi', 'send196.py'), 'bili',
                                     up])
                                # rms = send196.runsend(r['uname'])
                                rmsg = json.loads(rms)['Message']
                                log.info('发信返回：{}'.format(rmsg))
                            except(Exception) as e:
                                log.warning('发信错误：{}'.format(e))
                    else:
                        self.status[upname] = 0
                        log.info('TAT {} 不在！！'.format(r['uname']))
                    time.sleep(3)


def main():
    live = monitor()
    times = 0
    while 1:
        try:
            live.find()
            times += 1
            log.info('timse:{}'.format(times))
            if times >= 600:
                log.warning('##开始重启脚本…………')
                time.sleep(1)
                try:
                    os.execlp('python', 'python', 'BiliMonitor0.3.py')
                except(Exception) as e:
                    log.warning('重启脚本错误：{}'.format(e))
            tim(160)
        except(KeyboardInterrupt, SystemExit):
            log.warning('退出监控！！')
            sys.exit('exit:退出监控！！                                                      ')


if __name__ == '__main__':
    log = log()
    main()
