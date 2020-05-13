import subprocess as sp
from bs4 import BeautifulSoup
from lxml import etree
import requests
import platform
import re
import random

SYSTEM_STR = platform.system()
CONSOLE_ENCODING = 'utf-8'

LOSE_COUNT_PATTERN = re.compile(r'(\d+)% packet loss', re.IGNORECASE)
AVG_WAIT_TIME_PATTERN = re.compile(r'rtt min/avg/max/mdev = ([\d./]+) ms', re.IGNORECASE)
PING_CMD = 'ping -c 3 -W 3'

if 'Windows' == SYSTEM_STR:
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                "Chrome/81.0.4044.138 Safari/537.36"
    CONSOLE_ENCODING = "gbk"
    LOSE_COUNT_PATTERN = re.compile(r'(\d+)% 丢失', re.IGNORECASE)
    AVG_WAIT_TIME_PATTERN = re.compile(r'平均 = (\d+)ms', re.IGNORECASE)
    PING_CMD = 'ping -n 3 -w 3'

elif 'Linux' == SYSTEM_STR:
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                "Chrome/81.0.4044.138 Safari/537.36"
elif 'MacOS' == SYSTEM_STR:
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) " \
                "Chrome/81.0.4044.138 Safari/537.36"
else:
    USER_AGENT = None


def getProxys(page=1):
    s = requests.Session()
    # 高匿
    url = f'https://www.xicidaili.com/nn/{page}'

    header = {
        'User-Agent': USER_AGENT
    }

    r = s.get(url, headers=header)

    htmlStr = r.text
    soup = BeautifulSoup(htmlStr, 'lxml')
    ipListTable = soup.find_all(id='ip_list')[0]
    ipListInfo = ipListTable.contents

    proxys_list = []
    for index in range(len(ipListInfo)):
        if index % 2 == 1 and index != 1:
            dom = etree.HTML(str(ipListInfo[index]))
            ip = dom.xpath('//td[2]')
            port = dom.xpath('//td[3]')
            protocol = dom.xpath('//td[6]')
            proxys_list.append((ip[0].text, port[0].text, protocol[0].text.lower()))
    return proxys_list


def checkIp(ip: str):
    cmd = f'{PING_CMD} {ip}'
    p = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)

    # ping 3 次，wait timeout 3秒
    out = p.stdout.read().decode(CONSOLE_ENCODING)

    loseCount = LOSE_COUNT_PATTERN.findall(out)
    if len(loseCount) == 0:
        lose = 3
    else:
        lose = int(loseCount[0])

        # 如果丢包数目大于2个,则认为连接超时,返回平均耗时1000ms
        if lose > 2:
            # 返回False
            return 1000
        # 如果丢包数目小于等于2个,获取平均耗时的时间
        else:
            # 平均时间
            avgWasteTime = AVG_WAIT_TIME_PATTERN.findall(out)
            # 当匹配耗时时间信息失败,默认三次请求严重超时,返回平均耗时1000ms
            if len(avgWasteTime) == 0:
                return 1000
            else:
                #
                average_time = int(avgWasteTime[0])
                # 返回平均耗时
                return average_time


PROXY_IP_POOL = None


def getProxy(expectProtocol='https'):
    global PROXY_IP_POOL
    if PROXY_IP_POOL is None or len(PROXY_IP_POOL) == 0:
        PROXY_IP_POOL = getProxys(1)

    # 如果平均时间超过200ms重新选取ip
    while True:
        # 从100个IP中随机选取一个IP作为代理进行访问
        proxy = random.choice(PROXY_IP_POOL)
        # 检查ip
        ip = proxy[0]
        protocol = proxy[2]
        if expectProtocol != protocol:
            continue
        average_time = checkIp(ip)
        if average_time > 200:
            # 去掉不能使用的IP
            PROXY_IP_POOL.remove(proxy)
            print("ip连接超时, 重新获取中!")
        if average_time < 200:
            break

    # 去掉已经使用的IP
    PROXY_IP_POOL.remove(proxy)
    return proxy


def getProxyURL(expectProtocol='https'):
    proxy = getProxy(expectProtocol)
    return f'{proxy[2]}://{proxy[0]}:{proxy[1]}'
