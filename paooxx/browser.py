#!/usr/bin/python
# coding=utf-8

import os
import sys

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

reload(sys)
sys.setdefaultencoding('utf-8')
ua = UserAgent()


# 定义参数
# rootpath = os.getcwd().replace('\\', '/')

class browser:
    # 启动浏览器
    def __init__(self):
        # 参数设定
        self.rootpath = os.getcwd().replace('\\', '/')

    def prin(self, txt):
        # 打印封装
        print(txt)
        try:
            with open('{}/Bmonitor.log'.format(self.rootpath), 'a+')as log:
                log.writelines('{}\n'.format(txt))
        except(Exception) as e:
            print('输出错误：{}'.format(e))

    def start(self, path):
        self.dcap = dict(DesiredCapabilities.PHANTOMJS)
        # 从USER_AGENTS列表中随机选一个浏览器头，伪装浏览器
        self.dcap['phantomjs.page.settings.userAgent'] = (ua.random)
        # 不载入图片，爬页面速度会快很多
        self.dcap['phantomjs.page.settings.loadImages'] = False

        # 打开带配置信息的phantomJS浏览器
        try:
            dr = webdriver.PhantomJS(executable_path=path, desired_capabilities=self.dcap)
            self.prin('      ### 浏览器启动成功 ###')
        except(Exception) as e:
            self.prin('>>>浏览器启动错误：{}'.format(e))
        dr.implicitly_wait(10)
        # 设置60秒页面超时返回，类似于requests.get()的timeout选项，driver.get()没有timeout选项
        dr.set_page_load_timeout(60)
        # 设置30秒脚本超时时间
        dr.set_script_timeout(30)
        return dr


if __name__ == '__main__':
    driver = browser()

    driver.start('D:/PYProgram/phantomjs-2.1.1/bin/phantomjs.exe')
