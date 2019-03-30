import subprocess
import re
import json
import argparse
from urllib.request import urlopen
from urllib.error import URLError
from collections import namedtuple
import prettytable
ip_regex = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
res_info = namedtuple('res_info', ['number', 'ip', 'autonomous_system', 'country', 'isp'])


def get_traceroute(addr):
    process = subprocess.Popen('tracert -d ' + addr, shell=True, stdout=subprocess.PIPE)
    output = process.communicate()[0].decode('cp866').splitlines()
    ips = []
    for line in output:
        l = line.split()
        if '*' in l: break
        if len(l) != 0:
            if ip_regex.match(l[-1]):
                ips.append((l[0], l[-1]))
    return ips


def get_info(ips):
    result = []
    for ip in ips:
        with urlopen('http://ip-api.com/json/{0}'.format(ip[1])) as response:
            data = json.load(response)
            if data['status'] != 'fail':
                res = res_info(ip[0], ip[1], data['as'], data['country'], data['isp'])
            else:
                res = res_info(ip[0], ip[1], 'Not stated', 'Not stated', 'Not stated')
            result.append(res)
    return result


def make_table(result):
    table = prettytable.PrettyTable(['number', 'IP', 'Autonomous system', 'Country', 'Provider'])
    for r in result:
        table.add_row(list(r))
    return table


def traceroute(addr):
    table = make_table(get_info(get_traceroute(addr)))
    with open('{} traceroute.txt'.format(addr), 'w') as f:
        f.write(table.get_string())


def internet_on():
    try:
        urlopen('google.com', timeout=5)
        return True
    except URLError:
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--address', '-a', action='store', dest='addr')
    args = parser.parse_args()
    if internet_on():
        traceroute(args.addr)
    else:
        print('No connection')


if __name__ == '__main__':
    traceroute()
