#!/usr/bin/python3
# Created on 17/11/9
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


def log(path):
    # create logger
    logger = logging.getLogger('Loger')
    # Set default log level
    logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    ch2 = logging.FileHandler(path)
    ch2.setLevel(logging.WARNING)

    # create formatter
    formatter = logging.Formatter('%(asctime)s_%(levelname)s: %(message)s')

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
    # 监控主体程序
    def __init__(self):
        # 定义参数
        cp = configparser.ConfigParser()
        cp.read('uplist.txt', encoding='utf-8')
        opt = cp.options('douyu')
        self.rooms = {}
        self.onlinestatus = {}
        self.num = {}
        for op in opt:
            self.rooms[op] = cp.get('douyu', op)
            self.onlinestatus[op] = 0
            self.num[op] = 0
        log.info('Uplist:{}'.format(self.rooms))
        self.times = 0
        self.ua = UserAgent()

    def findDouyu(self, room):
        # 查找斗鱼
        header = {'User-Agent': self.ua.random}
        try:
            respon = requests.get('http://open.douyucdn.cn/api/RoomApi/room/' + room, headers=header)
            time.sleep(1)
            r = respon.json()
            if r['error'] == 0:  # 判断API接口是否正常访问
                roomname = r['data']['room_name']
                upname = r['data']['owner_name']
                roomstatus = r['data']['room_status']
                on = (roomstatus == u'1')
                log.info(u'>房间：{}'.format(roomname))
                # API接口读取状态，房间开播状态
                return 1, on, upname
            else:
                log.warning(u'>API接口错误：error: {}'.format(r[u'error']))
                return 0,
        except(Exception)as e:
            log.warning(u'>读取斗鱼网页错误：{}'.format(e))
            return 0,

    def run(self):
        for room in self.rooms:
            log.info('======================================')
            try:
                findresult = self.findDouyu(room)
                upname = 'None'
                if findresult[0]:
                    upname = findresult[2]
                    self.onlinestatus[room] = findresult[1]
                log.info(u'>在线状态：{}'.format(self.onlinestatus[room]))
                if self.onlinestatus[room]:
                    self.num[room] += 1
                else:
                    self.num[room] = 0
                    log.info(u'>--TAT-- {} 不在！！！<'.format(upname))
                if self.num[room] == 1:
                    log.info(u'>{} 开播啦！发送信息!!!'.format(upname))
                    try:
                        for ra in range(5):
                            mas = subprocess.check_output(['python2',
                                                           os.path.join(os.path.abspath('.'), 'dysmsapi', 'send196.py'),
                                                           'douyu',
                                                           room])
                            rmsg = json.loads(mas)['Message']
                            log.info(u'>发信返回：{}'.format(rmsg))
                            time.sleep(20)
                            if rmsg == 'OK':
                                break
                    except(Exception) as e:
                        log.warning(u'发信错误！！{}'.format(e))
                elif self.num[room] > 1:
                    log.info(u'>{} 正在直播!!!<'.format(upname))
            except(Exception) as e:
                log.warning(u'run错误:{}'.format(e))
            self.times += 1
            log.info('>times:{}'.format(self.times))
            time.sleep(5)
            if self.times >= 600:
                log.warning(u'##开始重启脚本…………')
                time.sleep(1)
                try:
                    os.execlp('python', 'python', 'DouyuMonitor0.3.py')
                except(Exception) as e:
                    log.warning(u'重启脚本错误：{}'.format(e))


def main():
    live = monitor()
    while 1:
        try:
            live.run()
            tim(150)
        except(KeyboardInterrupt, SystemExit):
            log.warning(u'退出监控！                           ')
            sys.exit(u'exit:退出监控！')


if __name__ == '__main__':
    log = log('douyu.log')
    main()
