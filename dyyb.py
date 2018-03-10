#!/usr/bin/python
# -*- coding: utf-8 -*-
# Created on 18/1/23
__author__ = 'Mumushuimei'
import json
import random
import sqlite3
import sys
import time

import requests

code = sys.getfilesystemencoding()
ua = u'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36'
headers = {}
headers[u'Referer'] = u'https://yuba.douyu.com/'
headers[
    u'Cookie'] = u'dy_did=f6986f891c65b8da1176158357071501;smidV2=2018021119040943182c2db4ef66079086aff47042841a00ab81d77bae94730;acf_yb_t=a4DYQp6SOCqZZkvxiYa3oc0MdKQjY6mV;Hm_lvt_e99aee90ec1b2106afe7ec3b199020a7=1520333397,1520407624,1520475003,1520644973;Hm_lvt_e0374aeb9ac41bee98043654e36ad504=1520573446,1520644517,1520710744,1520712605;acf_yb_auth=c4cb9d9fb1c8b1041edff866abbad4e3da011f39;acf_yb_new_uid=rEdlXlnVedNM;acf_yb_uid=51276995;Hm_lpvt_e0374aeb9ac41bee98043654e36ad504=1520712606'


def tim(t):
    for i in xrange(t):
        time.sleep(1)


def getlist():
    post_ids = []
    for i in range(1, 3):
        #timest = format(time.time() % 1, '0.16f')
        url = u'https://yuba.douyu.com/wbapi/web/group/postlist'
        params = {u'group_id': 564, u'page': i}
        headers[u'User-Agent'] = ua
        try:
            r = requests.get(url, headers=headers, params=params, timeout=9)
            r.encoding = 'utf-8'
            if r.encoding == u'ISO-8859-1':
                r.encoding = requests.utils.get_encodings_from_content(r.content)[0]
        except(Exception) as e:
            print e
        resp = json.loads(r.text)
        try:
            for i in xrange(3, len(resp[u'data'])):
                post_id = resp[u'data'][i][u'post_id']
                post_ids.append(post_id)
        except:
            print r.text  # json.dumps(resp, ensure_ascii=False, encoding='UTF-8')

    return post_ids


def postmsg():
    conn = sqlite3.connect(u'yuba.db')
    post_ids = getlist()
    timest = format(time.time() % 1 / 1000, '0.19f')
    try:
        cur = conn.cursor()
        cur.execute(u"delete from post_id where datetime('now','localtime')>datetime(tim,'+12 hours')")
        conn.commit()
        cur.execute(u"select id from post_id")
    except(Exception) as e:
        print u'sqlite3E:', e
    oids = []
    newids = []
    for id in cur.fetchall():
        oids.append(id[0])
    for nid in post_ids:
        if nid not in oids:
            newids.append(nid)
    print newids
    nm = 0
    for post_id in newids:
        timest = format(time.time() % 1, '0.16f')
        url = u'https://yuba.douyu.com/ybapi/answer/comment?{}'.format(timest)
        data = {u'content': u'<p>[开车][开车]水水更健康</p>', u'pid': post_id, 'vo_id': '', 'tokensign': ''}
        headers[u'User-Agent'] = ua
        try:
            r = requests.post(url, headers=headers, data=data)
            r.encoding = u'utf-8'
            if r.encoding == u'ISO-8859-1':
                r.encoding = requests.utils.get_encodings_from_content(r.content)[0]
            mes = json.loads(r.text)[u'message']
            print u'post_id：', post_id
            if mes == '':
                cur.execute(u"insert or ignore into post_id values(?,datetime('now','localtime'))", (post_id,))
                conn.commit()
            print u'message:', mes
        except(Exception) as e:
            print u'postE:', e
        nm += 1
        if nm == 5:
            nm = 0
            tim(300)
        tim(random.randint(7, 10))
    cur.close()
    conn.close()


if __name__ == '__main__':
    postmsg()
