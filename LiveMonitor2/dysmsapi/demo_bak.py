# -*- coding: utf-8 -*-
# ！D:\Python27\python.exe
import os
import sys
import uuid

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.profile import region_provider
from aliyunsdkdysmsapi.request.v20170525 import QuerySendDetailsRequest
from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest

"""
短信业务调用接口示例，版本号：v20170525

Created on 2017-06-12

"""

reload(sys)
sys.setdefaultencoding('utf8')

# 注意：不要更改
REGION = "cn-hangzhou"
PRODUCT_NAME = "Dysmsapi"
DOMAIN = "dysmsapi.aliyuncs.com"

# ACCESS_KEY_ID/ACCESS_KEY_SECRET 根据实际申请的账号信息进行替换
ACCESS_KEY_ID = "LTAI3FNxthUADrnd"
ACCESS_KEY_SECRET = "a1F6RJ3BzPT1n0DU5OzQnF4VquLgLM"

acs_client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION)
region_provider.add_endpoint(PRODUCT_NAME, REGION, DOMAIN)


def send_sms(business_id, phone_numbers, sign_name, template_code, template_param=None):
    smsRequest = SendSmsRequest.SendSmsRequest()
    # 申请的短信模板编码,必填
    smsRequest.set_TemplateCode(template_code)

    # 短信模板变量参数
    if template_param is not None:
        smsRequest.set_TemplateParam(template_param)

    # 设置业务请求流水号，必填。
    smsRequest.set_OutId(business_id)

    # 短信签名
    smsRequest.set_SignName(sign_name);

    # 短信发送的号码列表，必填。
    smsRequest.set_PhoneNumbers(phone_numbers)

    # 调用短信发送接口，返回json
    smsResponse = acs_client.do_action_with_exception(smsRequest)

    # TODO 业务处理

    return smsResponse


def query_send_detail(biz_id, phone_number, page_size, current_page, send_date):
    queryRequest = QuerySendDetailsRequest.QuerySendDetailsRequest()
    # 查询的手机号码
    queryRequest.set_PhoneNumber(phone_number)
    # 可选 - 流水号
    queryRequest.set_BizId(biz_id)
    # 必填 - 发送日期 支持30天内记录查询，格式yyyyMMdd
    queryRequest.set_SendDate(send_date)
    # 必填-当前页码从1开始计数
    queryRequest.set_CurrentPage(current_page)
    # 必填-页大小
    queryRequest.set_PageSize(page_size)

    # 调用短信记录查询接口，返回json
    queryResponse = acs_client.do_action_with_exception(queryRequest)

    # TODO 业务处理

    return queryResponse


__name__ = 'send'
if __name__ == 'send':
    rootpath = os.getcwd().replace('\\', '/')
    with open(rootpath + '/ini.txt', 'r')as f:
        uper = f.read()
    __business_id = uuid.uuid1()
    # print 'Business_id = %s' % __business_id
    params = "{\"code\":\"12345\",\"upname\":\"uper\"}"
    send_sms(__business_id, "18673312624", "木木睡没", "SMS_107950119", params)

if __name__ == 'query':
    print query_send_detail("1234567^8901234", "13000000000", 10, 1, "20170612")
