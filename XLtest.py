#!/usr/bin/python
# -*- coding: utf-8 -*-
# Created on 18/1/25
__author__ = 'Mumushuimei'
import sys

code = sys.getfilesystemencoding()
from openpyxl import Workbook

wb = Workbook()
sheet=wb.get_active_sheet()
sheet['A1']='名字'
sheet['B1']='密码'
wb.save('g:/test1.xlsx')
# if __name__ == '__main__':
#     pass
