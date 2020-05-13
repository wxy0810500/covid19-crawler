import requests
from utils.proxy_ip_pool import getProxyURL


proxies = {"https": "218.241.219.84:3128"}
s = requests.Session()
s.proxies = proxies
r = s.get("https://ip.chinaz.com/")
print(r.text)
