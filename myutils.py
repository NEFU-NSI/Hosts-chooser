import multi
from fake_useragent import UserAgent
import requests
import re
from prettytable import PrettyTable

from crontab import CronTab
import os
import sys
import subprocess

def run_core(domain, area):
    # Encrypt!
    if area == "debug":
        iplist = ['220.181.38.148', '39.156.69.79', '210.23.129.34', '210.23.129.34', '220.181.38.148', '39.156.69.79', '202.108.22.220', '220.181.33.31', '112.80.248.64', '14.215.178.80', '180.76.76.92', '210.23.129.34', '210.23.129.34', '39.156.69.79', '220.181.38.148', '203.12.160.35', '203.12.160.35', '39.156.69.79', '220.181.38.148',
                  '202.108.22.220', '220.181.33.31', '112.80.248.64', '14.215.178.80', '180.76.76.92', '203.12.160.35', '203.12.160.35', '220.181.38.148', '39.156.69.79', '61.8.0.113', '61.8.0.113', '220.181.38.148', '39.156.69.79', '202.108.22.220', '220.181.33.31', '112.80.248.64', '14.215.178.80', '180.76.76.92', '61.8.0.113', '61.8.0.113']
    else:
        ipdict = multi.multi_local_dns(domain)
        print("[+]Got domain! \n" + str(list(ipdict[1].keys())))
    return domain, ipdict


def run_remote_core(domain, area):
    ua = UserAgent()
    headers = {"User-Agent": ua.random, }
    head = ["http://www.","https://www."]
    status = []
    for i in head:
        try:
            r = requests.get(i+domain)
            status.append(r.status_code)
        except:
            pass
        continue
    if 200 in status:
        r = requests.get("https://en.ipip.net/dns.php?a=dig&host=" +
                        domain+"&area%5B%5D="+area, headers=headers)
        iplist = re.findall("\\d+\\.\\d+\\.\\d+\\.\\d+", r.text)
        print("[+]Got domain! \n" + str(iplist))
        return domain, iplist
    else:
        raise domainError

def output_dic(domain, ip_dic):
    print("[+]Output:")

    table = PrettyTable(["Domain", "ip", "delay(/s)"])
    table.align["Domain"] = "l"
    for ip, delay in ip_dic.items():
        # print(str(domain) + "    " + str(ip) + "    " + str(delay))
        table.add_row([domain, ip, delay])

    print(table)

def update_hosts(domain, new_ip):
    if os.getuid() != 0:
        sys.exit("not root?")

    if len(new_ip) != 0:
        print("[-]Start updating hosts")
        for ip in new_ip[::-1]:
            cmd = ['sed', '-i', rf'/^[0-9.]\+[[:space:]]\+{domain}\>/s/[^[:space:]]\+/{ip}/', '/etc/hosts']
            try:
                subprocess.check_call(cmd)
                print("Add {0} {1}".format(domain, ip))
            except:
                print("Error: {0} {1}".format(domain, ip))
        print("[+]Done!")

def update_crontab(domain):
    my_user_cron = CronTab(user=True)  # 创建当前用户的crontab
    # 删除原有的crontab文件中重复的内容

    objs = my_user_cron.find_comment(domain)
    if objs:
        for obj in objs:
            my_user_cron.remove(obj)

    job = my_user_cron.new(command='python3 /program/python/Hosts-chooser-master main.py -t ' + domain + ' --clean')
    job.setall('*/2 * * * *')  # 设置执行时间
    job.set_comment(domain)

    my_user_cron.write()

class domainError(Exception):
    def __init__(self,err='invalid domian'):
        Exception.__init__(self,err)
