import json
import requests
import random
import re
import chardet
import os
import time
 
from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109 import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109 import UpdateDomainRecordRequest
from LocalV6Helper import get_Local_ipv6_address

#parse config
import configparser
conf = configparser.ConfigParser()
conf.read("config.ini")

# modified from code https://www.52pojie.cn/forum.php?mod=viewthread&tid=783673&page=1

 
#此类是修改阿里云的解析ip
class Aliyunddns(object):
    def __init__(self):
        self.client = AcsClient(conf.get('config', 'AccessKeyID'), conf.get('config', 'AccessKeySecret'), 'cn-hangzhou');
        self.domain = conf.get('config', 'Domain')

    #检测本地网络环境，是否是联网状态
    def IsConnectNet(self):
        try:
            requests.get('http://www.baidu.com',timeout=5)
            return True
        except requests.exceptions.ConnectionError as e:
            return False

    # 检测本地外网ip是否和解析的ip一致
    def CheckLocalip(self):
        if not self.IsConnectNet():
            print('网络不通...')
            return

        #这里为了防止频繁的访问阿里云api，会把ip存入本地的ip.txt文件中
        #每次都和本地文件中的ip地址进行对比，不一致再去访问阿里云api进行修改
        netip = get_Local_ipv6_address()
        if os.path.exists('ip.txt'):
            with open('ip.txt','r') as fp:
                file_ip = fp.read()

            if file_ip == netip:
                print('IP相同, 不需要重新解析。')
                return
            else:
                print('IP不相同, 开始重新解析...')
                with open('ip.txt','w') as fp:
                    fp.write(netip)
                    fp.close()
                self.GetDomainRecords()
        else:
            print('文件不存在，直接写入外网IP')
            with open('ip.txt','w') as fp: fp.write(netip)
            self.GetDomainRecords()

    #开始更新
    def Update(self,ip,record):
        udr = UpdateDomainRecordRequest.UpdateDomainRecordRequest()
        udr.set_accept_format('json')
        udr.set_RecordId(record['RecordId'])
        udr.set_RR(record['RR'])
        udr.set_Type(record['Type'])
        udr.set_Value(ip)
        response = self.client.do_action_with_exception(udr)
        UpdateDomainRecordJson = json.loads(response.decode('utf-8'))
        print(UpdateDomainRecordJson)

    #获取阿里云域名解析信息
    def GetDomainRecords(self):
        DomainRecords = DescribeDomainRecordsRequest.DescribeDomainRecordsRequest()
        DomainRecords.set_DomainName(self.domain)
        DomainRecords.set_accept_format('json')
        response = self.client.do_action_with_exception(DomainRecords)
        record_dict = json.loads(response.decode('utf-8'))
        for record in record_dict['DomainRecords']['Record']:
            if not record['RR'] in eval(conf.get('config', 'Records')):
                continue
            netip = get_Local_ipv6_address()

            if record['Value'] != netip:
                print('netip:',netip)
                print('aliip:',record['Value'])
                self.Update(netip, record)

if __name__ == '__main__':
    
    ali = Aliyunddns()
    while True:
        ali.CheckLocalip()
        # 这里设置检测的时间间隔，单位秒
        time.sleep(1200)