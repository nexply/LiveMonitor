# coding:utf-8
import os
import subprocess

sen = subprocess.check_output(['python2', os.path.join(os.path.abspath('.'), 'dysmsapi', 'send196.py'), 'douyu', '196'])
print(sen)
