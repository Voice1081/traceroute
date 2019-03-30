import subprocess
import re
import json
from urllib.request import urlopen
from collections import namedtuple
ip_regex = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
res_info = namedtuple('res_info', ['number', 'ip', 'as', 'country', 'isp'])


def get_traceroute(addr):
    process = subprocess.Popen('tracert -d ' + addr, shell=True, stdout=subprocess.PIPE)
    output = process.communicate()[0].decode('cp866').splitlines()
    ips = []
    for line in output:
        l = line.split()
        if '*' in l: break
        if ip_regex.match(l[-1]):
            ips.append((l[0], l[-1]))
    return ips


def get_info(ips):
    result = []
    for ip in ips:
        with urlopen('http://ip-api.com/json/{0}'.format(ip[1])) as response:
            data = json.load(response)
            res = res_info(ip[0], ip[1], data['as'], data['country'], data['isp'])
            result.append(res)
    return result

