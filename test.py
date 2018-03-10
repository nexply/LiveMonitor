#!/usr/bin/python
# -*- coding: utf-8 -*-
# Created on 18/1/23
__author__ = 'Mumushuimei'
import sys

code = sys.getfilesystemencoding()

c='dy_did=014fccefa71a5f8fc55689d400081501; Hm_lvt_e99aee90ec1b2106afe7ec3b199020a7=1516864542,1517880865; smidV2=2018020609342631822799962c5ffd94c318d4bf6af8e200d55f4247c6e54d0; Hm_lpvt_e99aee90ec1b2106afe7ec3b199020a7=1517880865; acf_yb_t=DjMvVtXHYiUcwCd2nNr3KfXXtO80gKv0; Hm_lvt_e0374aeb9ac41bee98043654e36ad504=1517880863; Hm_lpvt_e0374aeb9ac41bee98043654e36ad504=1517880898; acf_yb_auth=289e6d86dea1f5b66cc8475bbed292bc10c776aa; acf_yb_new_uid=rEdlXlnVedNM; acf_yb_uid=51276995'
cookie=dict((l.split('=') for l in c.split(';')))
print(cookie)
