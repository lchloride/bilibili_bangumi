# bilibili_bangumi
A tool for querying anime information and downloading bangumi videos especially for overseas users.

**This documentation is mainly designed for users of bilibili.com who use Simplified Chinese mostly. For English support, please leave message at issue.**

本项目意在提供一个获取bilibili番剧信息与视频的工具，设计的初衷是解决海外党无法直接观看b站番剧的问题。项目仍在开发中，有建议与意见请在issue中留言。

**目前，项目开发在Windows平台下，其他平台不保证运行的稳定性。**

## 环境依赖
Python(>=3.2)

Selenium(可使用pip安装)
```bash 
pip install selenium
```

浏览器Kit，目前支持PhantomJS(推荐,下载：http://phantomjs.org/download.html )、ChromeDriver

## 基本使用
目录：
* 初始化配置
* 代理库设置
* 剧集相关操作(获取视频地址/下载视频)
* 番剧信息获取
* 发现番剧(方式：新番时间表/番剧搜索/番剧索引)

### 初始化配置
目前配置方法为手动修改配置文件，命令行设置方法正在开发。

设置文件为根目录下的`settings.conf`文件，通常需要配置3项，如下所示。
```conf
[path]
phantomjs_exec_path = 
chrome_driver_path = 

[time]
page_load_timeout = 60

[parameters]
browser = 
```
path部分中两个参数为PhantomJS与ChromeDriver两个WebKits的**可执行文件**绝对路径，且Windows下的路径分隔符需要用两个反斜杠`\\`表示(如`E:\\PhantomJS\\bin\\phantomjs.exe`)。time部分的page_load_timeout参数可以不变。网络较好的用户可以减小该值；建议使用代理访问的海外用户不要减小该值。parameters部分的browser参数根据想使用的WebKit选择`phantomjs`或`chrome`。
### 代理库
目前修改代理库的方法为手动修改文件，命令行设置方法正在开发。该部分的设置主要面向海外用户。

代理库文件为根目录下的`proxy.json`文件，存储格式为JSON字符串，如下所示。
```json
[{"ip": "61.191.41.130", "port": 80},{"ip": "118.144.154.253", "port": 3128}]
```
代理库中`{}`之间的内容为一个代理服务器的信息，包括IP地址(ip)和端口(port)两个域。如需添加新的代理服务器，只需复制`,{"ip": "118.144.154.253", "port": 3128}`信息，粘贴到字符串末尾的`}]`之间，然后将新代理服务器的IP地址和端口替换掉即可。
### 剧集相关操作(bangumi目录下bilibili_bangumi.py)
* 根据剧集链接获取视频实际链接
>使用方法：
```bash
bilibili_bangumi.py -f URL
```
>URL为剧集的链接，形如https://bangumi.bilibili.com/anime/5997/play#103920 或 https://www.bilibili.com/video/av10184012 。

>获取的结果为视频的实际链接，可能有多个。
* 根据视频实际链接下载视频
>使用方法：
```bash
bilibili_bangumi.py -d URL
```
>URL为视频的实际链接，形如http://cn-jsks2-dx.acgvideo.com/vg8/2/dc/16824755-1-hd.mp4?...(参数略) 。

>视频将下载到项目根目录下。
* 根据剧集链接一步下载视频
>本操作相当于前两个操作的结合。使用方法：
```bash
bilibili_bangumi.py -fd URL
```
>URL为剧集的链接，形如https://bangumi.bilibili.com/anime/5997/play#103920 或 https://www.bilibili.com/video/av10184012 。

>视频将下载到项目根目录下。如果存在多个视频，所有视频均会被下载。
* 使用代理
>对于海外用户，获取视频实际链接的操作需要使用**中国大陆地区**的代理服务器(*限港澳台地区播放的番剧请使用对应地区的代理*)；下载视频的操作不需要使用代理。

>使用方法(以一步下载视频的操作为例)：
```bash
bilibili_bangumi.py -fd URL -rp
bilibili_bangumi.py -fd URL -p IDX
```
>第一条命令`-rp`表示使用代理服务器库(proxy.json)中的随机一个代理；第二条命令`-p IDX`表示使用代理服务器库(proxy.json)中的第IDX(从0开始计数)个代理。不指定`-p IDX`或`-rp`参数表示不使用代理。
### 番剧信息获取(anime目录下parser.py)
* 基本用法
```bash
parser.py URL
```
>URL为番剧的详情信息页面，形如https://bangumi.bilibili.com/anime/5997 。
* 输出形式
```bash
parser.py URL -j
parser.py URL -l
```
>第一条命令`-j`表示以json字符串的格式输出(便于后续处理)；第二条命令`-l`表示以列表的形式输出(便于阅读)。如果不指定输出方法，默认采用列表形式输出。
* 使用代理
>对于海外用户，获取番剧信息的操作需要使用**中国大陆地区**的代理服务器(*限港澳台地区播放的番剧请使用对应地区的代理*)。

>使用方法：
```bash
parser.py URL -l -rp
parser.py URL -l -p IDX
```
>第一条命令`-rp`表示使用代理服务器库(proxy.json)中的随机一个代理；第二条命令`-p IDX`表示使用代理服务器库(proxy.json)中的第IDX(从0开始计数)个代理。不指定`-p IDX`或`-rp`参数表示不使用代理。
### 发现番剧(anime目录下finder.py)
发现番剧部分所使用的网页没有访问限制，设计本功能主要是考虑解决在浏览器和程序之间切换的麻烦。本部分通过三种方式来发现番剧：新番时间表、番剧搜索和番剧索引。
* 新番时间表
>使用方法:
```bash
finder.py -t
```
* 番剧搜索
>使用方法：
```bash
finder.py -s KEYWORD
```
>KEYWORD为搜索关键词
* 番剧索引
```bash
finder.py -i PARAs
```
>PARAs为筛选项的参数，为JSON格式字符串。PARAs由9个域组成，它们的键分别是：p：页码，t：结果排序依据，sort：结果排序方式，v：类型，area：地区，stat：状态，y：时间，q：季度，tag：风格。每个域的值为一个标签的value属性，通常是一个字符串形式的数字如`"1"`。如果一个域没有被指定，该域将使用默认值；如果PARAs未指定，则全部域均使用默认值。

>p用来指定结果显示页码，如第1页("p":"1")

>t指定了结果排序依据，如追番人数("t":"1")

>sort指定了结果排序依据，如降序排序("sort":"0")

>v指定了番剧类型，如正片("v":"1")、剧场版("v":"3")

>area指定了地区，如日本("area":"2")

>stat指定了番剧状态，如连载中("stat":"1")

>y指定了番剧的播出年，如2017年("y":"2017")

>q指定了番剧的播出季度，如4月("q":"2")

>tag指定了番剧的风格，如轻小说改编("tag":"117")、萌系("tag":"81")

>**筛选项以及可以选择的值请使用命令`finder.py -ft`查看**

>默认查询参数为
```json
{"p": "1", "sort": "0", "t": "1", "v": "0", "area": "0", "stat": "0", "y": "0", "q": "0", "tag": ""}
```
* 输出形式
>使用方法(以获取新番时间表为例)：
```bash
finder.py -t -j
finder.py -t -l
```
>第一条命令`-j`表示以json字符串的格式输出(便于后续处理)；第二条命令`-l`表示以列表的形式输出(便于阅读)。如果不指定输出方法，默认采用列表形式输出。
* 显示番剧筛选项列表(针对番剧索引页)
>使用方法：
```bash
finder.py -ft
```
>在该操作中，`-j/-l`的输出形式参数将无效。
## 许可
bilibili_bangumi采用Apache 2.0许可协议。
