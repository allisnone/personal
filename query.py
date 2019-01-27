# -*- coding: utf-8 -*-
import re
import os
import csv
import json
import string
import requests
from urllib.parse import quote

def write_json(d={},file='config.json'):
    with open(file, "w", encoding='utf-8') as f:
        # indent 超级好用，格式化保存字典，默认为None，小于0为零个空格
        #f.write(json.dumps(a, indent=4))
        json.dump(d,f,indent=4,sort_keys=True,ensure_ascii=False)   # 和上面的效果一样
    return

def read_json(file='config.json'): 
    if not os.path.exists(file):
        return {}  
    with open(file, "r", encoding='utf-8') as f:
        #aa = json.loads(f.read())
        #f.seek(0)
        return json.load(f)
    
def encodeURL(url):
    """
    处理包含中文字符串/空格的URL编码问题
    :param url:
    :return:
    """
    return quote(url, safe=string.printable).replace(' ', '%20')

def get_html(url='',refer_url=''):
    proxy = None
    params = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0', 
        'Referer': refer_url }
    r = requests.get(encodeURL(url), params=params, headers=headers, proxies=proxy, verify=False)
    r.encoding = 'utf-8'
    return r.text
    
def my_company_abormal(url,keyword='异常'):
    html = get_html(url)
    #<title>xx科技有限公司 - 广州市商事主体信息公示平台</title>
    #<span id="spanMc" class="title-cnt">xx科技有限公司</span><br />
    #company = re.findall(r'<title>(.*?)</title>',hmtl,re.S|re.M)
    company = re.findall(r'<span id="spanMc" class="title-cnt">(.*?)</span><br />',html,re.S|re.M)
    company_name = ''
    if company:
        company_name = company[0]
    else:
        print('ERROR：获取企业信息异常，请查询：http://cri.gz.gov.cn后更新URL或校验html信息！')
        return False
    #<span style="background-color:red;">该企业已列入经营异常名录</span>
    #abnormal_re = re.search(r'.*<span style="background-color:red;">(.*?)</span>', r.text)
    abnormal_all = re.findall(r'<span style="background-color:red;">(.*?)</span>',html,re.S|re.M)
    abnormal = False
    if abnormal_all:
        for li in abnormal_all:
            if keyword in li:
                print('%s: '%company_name,li)
                abnormal =True
                break
    else:
        print('%s--企业注册信息正常'%company_name)
    return abnormal

def my_fsbd_info(url='',refer_url='',current='xx科技有限公司'):
    """
    获取发输变电注册信息
    """
    html = get_html(url,refer_url)
    abnormal = False
    #<dd><span>注册类别：</span><b>注册xx</b></dd>
    type = re.findall(r'<dd><span>注册类别：</span><b>(.*?)</b></dd>',html,re.S|re.M)
    if type:
        type = type[0]
    #<dd><span>有效期：</span>2020年12月31日</dd>
    valid_date = re.findall(r'<dd><span>有效期：</span>(.*?)</dd>',html,re.S|re.M)
    if valid_date:
        valid_date = valid_date[0]
    #<dt><span>注册单位：</span>  *  </a></dt>
    register_company = re.findall(r'<dt><span>注册单位：</span>(.*?)</a></dt>',html,re.S|re.M)
    company_name = ''
    if register_company:
        if '>' in register_company[0]:
            company_name = register_company[0].split('>')[1].split('\r')[0]
        else:
            pass
    else:
        print('ERROR：获取证书信息异常，请查询：%s 后更新URL或校验html信息！'% refer_url)
        return False
    
    if company_name:
        if company_name==current:
            print('证书注册"正常":  证书类型：%s 注册有效期: %s ，注册公司: %s' % (type,valid_date,company_name))
        else:
            abnormal = True
            print('证书注册"异常"，被盗用注册: 证书类型：%s 注册有效期: %s ，原注册公司: %s，盗用注册公司%s' % (type,valid_date,current,company_name))
    else:
        print('获取注册信息失败！！！')
    return abnormal

d = read_json('config.json')
my_company_abormal(d['company']['url'],d['company']['keyword'])
my_fsbd_info(d['certificate']['url'],d['certificate']['refer'],d['certificate']['company'])
"""
j = {
    'company':
        {
        'url': 'http://cri.gz.gov.cn/Detail?zch=50A22333659FA44651F172941DE608AA&state=009001',
        'refer': 'http://cri.gz.gov.cn',
        'keyword': '异常' 
        },
    'certificate':
        {
        'url': 'http://jzsc.mohurd.gov.cn/dataservice/query/staff/staffDetail/001708050329583149',
        'refer': 'http://jzsc.mohurd.gov.cn/asite/jsbpp/index',
        'company': '科技有限公司' 
        }  
    }
file = 'config.json'
write_json(j, file)
read_json(file)
"""
