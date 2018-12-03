import requests
import random
from datetime import datetime
from bs4 import BeautifulSoup
import threading
from six.moves import urllib
import socket
from wasabi import Printer

msg = Printer()

hds=[{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},\
    {'User-Agent':'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},\
    {'User-Agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'},\
    {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'},\
    {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36'},\
    {'User-Agent':'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},\
    {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},\
    {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'},\
    {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},\
    {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},\
    {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'},\
    {'User-Agent':'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11'},\
    {'User-Agent':'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'}]

my_headers=["Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
"Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)"
]


headers = {
'Host': 'hz.lianjia.com',
'Connection': 'keep-alive',
'Pragma': 'no-cache',
'Cache-Control': 'no-cache',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
'Cookie': 'lianjia_uuid=cb2a0fd3-6643-4189-910f-ca15599c6d0b; UM_distinctid=1671698418d114-0701872d79e4b1-35607400-13c680-1671698418e1d3; _smt_uid=5bed3551.c56fe31; _ga=GA1.2.2030785885.1542272340; select_city=330100; all-lj=3d0b35ab17a07d475f1852d271de56f8; TY_SESSION_ID=10edd9a6-6dee-4b03-9634-bda2ac0d1583; Hm_lvt_9152f8221cb6243a53c83b956842be8a=1542272336,1543818706; _gid=GA1.2.1665893964.1543818708; lianjia_ssid=0bc2d231-1509-4d57-b1bf-3a203e94b7c2; Hm_lpvt_9152f8221cb6243a53c83b956842be8a=1543844246; CNZZDATA1253492436=1895528739-1542267920-https%253A%252F%252Fwww.baidu.com%252F%7C1543844076; CNZZDATA1254525948=2079920909-1542267101-https%253A%252F%252Fwww.baidu.com%252F%7C1543838825; CNZZDATA1255633284=1070304279-1542267901-https%253A%252F%252Fwww.baidu.com%252F%7C1543843173; CNZZDATA1255604082=1045275370-1542270732-https%253A%252F%252Fwww.baidu.com%252F%7C1543842156; _gat=1; _gat_past=1; _gat_global=1; _gat_new_global=1; _gat_dianpu_agent=1'}

def get_source_code(url):
    try:
        result = requests.get(url, headers=headers, timeout=5)
        source_code = result.content
        msg.info(url)
    except Exception as e:
        print (e)
        return

    return source_code

def get_total_pages(url):
    source_code = get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')
    total_pages = 0
    try:
        page_info = soup.find('div',{'class':'page-box house-lst-page-box'})
    except AttributeError as e:
        page_info = None

    if page_info == None:
        return None
    page_info_str = page_info.get('page-data').split(',')[0]  #'{"totalPage":5,"curPage":1}'
    total_pages = int(page_info_str.split(':')[1])
    return total_pages

def get_sh_total_pages(url):
    source_code = get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')
    total_pages = 0
    try:
        page_info = soup.find('a',{'gahref':'results_totalpage'})
    except AttributeError as e:
        page_info = None

    if page_info == None:
        return 1
    total_pages = int(page_info.get_text().strip('')) #<a href="/xiaoqu/putuo/d58" gahref="results_totalpage">58</a>
    return total_pages

#===========proxy ip spider, we do not use now because it is not stable===========
proxys_src = []
proxys = []

def spider_proxyip():
    try:
        for i in range(1,4):
            url='http://www.xicidaili.com/nt/' + str(i)
            req = requests.get(url,headers=hds[random.randint(0, len(hds) - 1)])
            source_code = req.content
            soup = BeautifulSoup(source_code,'lxml')
            ips = soup.findAll('tr')

            for x in range(1,len(ips)):
                ip = ips[x]
                tds = ip.findAll("td")
                proxy_host = "http://" + tds[1].contents[0]+":"+tds[2].contents[0]
                proxy_temp = {"http":proxy_host}
                proxys_src.append(proxy_temp)
    except Exception as e:
        print ("spider_proxyip exception:")
        print (e)

def test_proxyip_thread(i):
    socket.setdefaulttimeout(5)
    url = "http://bj.lianjia.com"
    try:
        proxy_support = urllib.request.ProxyHandler(proxys_src[i])
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)
        res = urllib.request.Request(url,headers=hds[random.randint(0, len(hds) - 1)])
        source_cod = urllib.request.urlopen(res,timeout=10).read()
        if source_cod.find(b'\xe6\x82\xa8\xe6\x89\x80\xe5\x9c\xa8\xe7\x9a\x84IP') == -1:
            proxys.append(proxys_src[i])
    except Exception as e:
        return
       # print(e)

def test_proxyip():
    print ("proxys before:"+str(len(proxys_src)))
    threads = []
    try:
        for i in range(len(proxys_src)):
            thread = threading.Thread(target=test_proxyip_thread, args=[i])
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
    except Exception as e:
        print (e)
    print ("proxys after:" + str(len(proxys)))

def prepare_proxy():
    spider_proxyip()
    test_proxyip()

def readurl_by_proxy(url):
    try:
        tet = proxys[random.randint(0, len(proxys) - 1)]
        proxy_support = urllib.request.ProxyHandler(tet)
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)
        req = urllib.request.Request(url, headers=hds[random.randint(0, len(hds) - 1)])
        source_code = urllib.request.urlopen(req, timeout=10).read()
        if source_code.find(b'\xe6\x82\xa8\xe6\x89\x80\xe5\x9c\xa8\xe7\x9a\x84IP') != -1:
            proxys.remove(tet)
            print('proxys remove by IP traffic, new length is:' + str(len(proxys)))
            return None

    except Exception as e:
        proxys.remove(tet)
        print('proxys remove by exception:')
        print (e)
        print ('proxys new length is:' + str(len(proxys)))
        return None

    return source_code 
