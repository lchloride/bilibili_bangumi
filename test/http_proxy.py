from urllib import request
# 121.193.143.249:80
proxy_handler = request.ProxyHandler({'http': '118.144.154.253:3128'})
opener = request.build_opener(proxy_handler)
r = opener.open('http://www.bilibili.com/video/av10184012/')
print(r.read().decode('utf-8'))