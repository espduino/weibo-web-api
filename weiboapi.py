import requests
import time
import re
import urllib.parse
import base64
import binascii
import execjs
import pymysql
import traceback

#加密js路径 自己修改
with open('C:/Users/espduino/Desktop/test3/sina.js') as f:  # 坑0x01 相对路径前面不带/，带/不报错但读不出数据
    jscode = f.read()
ctx = execjs.compile(jscode)

#取账号数据库
def consql():
    conn = pymysql.connect(host="localhost",port=3306,user="root",password="",database="weibo",charset="utf8")
    return conn


def gettimestr():
    t = time.time()
    timestr = str(int(round(t * 1000)))
    return timestr

def gettentimestr():
    t = time.time()
    timestr = str(int(t))
    return timestr

def connmysql():
    conn = pymysql.connect()


def bs64byteurl(text):
    test = str(text)
    test = urllib.parse.quote(test)
    test = base64.b64encode(bytes(test,'utf-8'))
    test = test.decode()
    return test

# 微博登录
def prelogin(username,password,proxyip):
    #预登录 获取登录需要的参数
    s = requests.session()
    proxies = {
      "https": "socks5://" + proxyip,
      "http":"socks5://" + proxyip
    }
    s.keep_alive = False
    timestr = gettimestr()
    uin = bs64byteurl(username)
    cookie = requests.cookies.RequestsCookieJar()
    preurl = "https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su="+ uin +"&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_=" + timestr
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
    response = requests.get(preurl,headers=headers,proxies=proxies,timeout=5)
    value = response.text
    servertime = ''.join(re.findall(r'servertime":(.*?),"pcid',value))
    print(servertime)
    pcid = ''.join(re.findall(r'pcid":"(.*?)","nonce',value))
    print(pcid)
    nonce = ''.join(re.findall(r'nonce":"(.*?)","pubkey',value))
    print(nonce)
    pubkey = ''.join(re.findall(r'pubkey":"(.*?)","rsakv',value))
    print(pubkey)
    rsakv = ''.join(re.findall(r'rsakv":"(.*?)",',value))
    print(rsakv)
    flag = ''.join(re.findall(r'showpin":"(.*?),',value))
    code = ''
    if (1==1):
        codeurl = 'https://login.sina.com.cn/cgi/pin.php?r=8735976&s=0&p=' + pcid
        response = requests.get(codeurl,headers=headers)
        # 获取验证码 打码网站处理
        response = requests.get(codeurl,headers=headers)
        #tem = ''.join(['%02X ' % b for b in response.content]).strip()
        temp = response.content
        img = binascii.b2a_hex(temp)
        #自己处理打验证码 我这边用的是chaorendama.com超人打码
        dmurl = 'http://api2.sz789.net:88/RecvByte.ashx'
        params={'username':'','password':'','softId':'','imgdata':img}
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(dmurl, data=params, headers=headers)
        code = response.json()['result']
    print("code:" + code)
    nowtime = gettimestr()
    nowtentime = gettentimestr()
    password = ctx.call('test',pubkey,servertime,nonce,password)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36','Accept-Language': 'zh-cn','Accept-Encoding': 'gzip, deflate','Accept': 'text/html, application/xhtml+xml, */*','Content-Type': 'application/x-www-form-urlencoded'}
    loginurl = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)&_=' + nowtime
    logindata = 'entry=weibo&gateway=1&from=&savestate=7&qrcode_flag=false&useticket=1&pagerefer=https%3A%2F%2Fpassport.weibo.com%2Fvisitor%2Fvisitor%3Fentry%3Dminiblog%26a%3Denter%26url%3Dhttps%253A%252F%252Fweibo.com%252F%26domain%3D.weibo.com%26ua%3Dphp-sso_sdk_client-0.6.28%26_rand%3D'+ nowtentime + '.124&pcid=' + pcid + '&door=' + code + '&vsnf=1&su=' + uin + '&service=miniblog&servertime=' + nowtentime + '&nonce=' + nonce + '&pwencode=rsa2&rsakv=' + rsakv + '&sp=' + password + '&sr=1920*1080&encoding=UTF-8&cdult=2&domain=weibo.com&prelt=212&returntype=TEXT'
    response = s.post(loginurl, data=logindata, headers=headers,proxies=proxies,timeout=5)
    cookie = response.cookies.get_dict()
    s.cookies.update(cookie)
    message = response.text
    overurl = str(response.json()['crossDomainUrlList'][0])
    response = s.get(overurl,headers=headers)
    overoverurl = "https://login.sina.com.cn/sso/login.php?url=https%3A%2F%2Fweibo.cn%2F&_rand=1551168974.2524&gateway=1&service=sinawap&entry=sinawap&useticket=1&returntype=META&sudaref=&_client_version=0.6.26"
    response = s.get(overoverurl,headers=headers,proxies=proxies,timeout=5)
    cookie = response.cookies.get_dict()
    s.cookies.update(cookie)
    savecookie = str(s.cookies.get_dict())
    print(savecookie)
    return savecookie



# 微博点赞
def starwb(url,cookie,proxyip):
    posturl = url
    cookie = eval(cookie)
    s = requests.session()
    proxies = {
      "https": "socks5://" + proxyip,
      "http":"socks5://" + proxyip
    }
    s.keep_alive = False
    postheader = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36','Content-Type': 'application/x-www-form-urlencoded; Charset=UTF-8','Accept': '*/*','Accept-Language': 'zh-cn','Referer': 'https://weibo.com/'}
    response = s.get(url,headers=postheader,cookies=cookie,proxies=proxies,timeout=5)
    text = response.text
    mid = ''.join(re.findall(r'&mid=(.*?)&src=',text)[0])
    posttime = gettimestr()
    posturl = "https://weibo.com/aj/v6/like/add?ajwvr=6&__rnd=" + posttime
    postdata = "location=page_100206_single_weibo&version=mini&qid=heart&mid=" + mid + "&loc=profile&cuslike=1&hide_multi_attitude=1&liked=0&_t=0"
    response = s.post(posturl,data=postdata,headers=postheader,cookies=cookie,proxies=proxies,timeout=5)
    print(response.text)
    code = response.json()['code']
    if (code == '100000'):
        print("点赞成功")
    else:
        print("点赞失败")


# 发布微博
def postwb(text,cookie):
    timestr = gettimestr()
    cookie = eval(cookie)
    postheader = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36','Content-Type': 'application/x-www-form-urlencoded; Charset=UTF-8','Accept': '*/*','Accept-Language': 'zh-cn','Referer': 'https://weibo.com/'}
    posturl = 'https://weibo.com/aj/mblog/add?ajwvr=6&__rnd=' + timestr
    postdata = urllib.parse.quote(text)
    data = 'location=v6_content_home&text='+ postdata + '&appkey=&style_type=1&pic_id=&tid=&pdetail=&mid=&isReEdit=false&rank=0&rankid=&module=stissue&pub_source=main_&pub_type=dialog&isPri=0&_t=0'
    response = requests.post(posturl,data=data,headers=postheader,cookies=cookie)
    print(response.text)


# 微博评论 //自己的uid 别人微博的mid
def commentwb(text,cookie,url,uid,proxy):
    posturl = url
    cookie = eval(cookie)
    s = requests.session()
    s.keep_alive = False
    postheader = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36','Content-Type': 'application/x-www-form-urlencoded; Charset=UTF-8','Accept': '*/*','Accept-Language': 'zh-cn','Referer': 'https://weibo.com/'}
    response = s.get(url,headers=postheader,cookies=cookie)
    value = response.text
    mid = ''.join(re.findall(r'&mid=(.*?)&src=',value)[0])
    posttime = gettimestr()
    text = urllib.parse.quote(text)
    posturl = "https://weibo.com/aj/v6/comment/add?ajwvr=6&__rnd=" + posttime
    postdata = "act=post&mid=" + mid + "&uid=" + uid + "&forward=0&isroot=0&content=" + text + "&location=page_100505_single_weibo&module=bcommlist&pdetail=1005051496952253&_t=0"
    response = requests.post(posturl,data=postdata,headers=postheader,cookies=cookie)
    print(response.json())

#获得uid
def getmyuin(cookie,proxyip):
    cookie = eval(cookie)
    s = requests.session()
    proxies = {
      "https": "socks5://" + proxyip,
      "http":"socks5://" + proxyip
    }
    s.keep_alive = False
    postheader = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36','Content-Type': 'application/x-www-form-urlencoded; Charset=UTF-8','Accept': '*/*','Accept-Language': 'zh-cn','Referer': 'https://weibo.com/'}
    response = s.get('https://account.weibo.com/set/index?topnav=1&wvr=6',headers=postheader,cookies=cookie,proxies=proxies,timeout=5)
    text = response.text
    uid = ''.join(re.findall(r'uid\':\'(.*?)\'',text)[0])
    return uid

#存储uid
def saveuid(csql,username,uid):
    count = csql.execute("UPDATE `user` SET uin=%s WHERE username=%s",(uid,username))
    if (count == 1):
        print("写数据正确")
    else:
        print("写数据错误")

#存储cookie
def savecookie(csql,username,cookie):
    count = csql.execute("UPDATE `user` SET cookie=%s WHERE username=%s",(cookie,username))
    if (count == 1):
        print("写数据正确")
    else:
        print("写数据错误")


def getcookie(csql,username):
    count = csql.execute("SELECT cookie FROM `user` WHERE username=%s",(username))
    cookie = csql.fetchall()
    cookie = cookie[0]['cookie']
    return cookie

def getuid(csql,username):
    count = csql.execute("SELECT uin FROM `user` WHERE username=%s",(username))
    cookie = csql.fetchall()
    cookie = cookie[0]['uin']
    return cookie
#微博登录
def listlogin(csql,userlist):
    for user in userlist:
        username = user['username']
        userpassword = user['password']
        cookie = prelogin(username,userpassword,'test')
        savecookie(csql,username,cookie)



def main():
    conn = consql()
    test = conn.cursor(pymysql.cursors.DictCursor)
    cookie = getcookie(test,'')
    uid = getuid(test,'')
    commentwb('确实很不错',cookie,'https://weibo.com//HqvEhgm1P?type=comment',uid,"test")
    postwb("小螺号 滴滴的吹",cookie)
    count = test.execute("SELECT * from  user where id = 1")
    userlist = test.fetchall()
    listlogin(test,userlist)
    starwb('https://weibo.com//HqvEhgm1P?type=comment',cookie)
    conn.commit()

if __name__ == "__main__":
    main()
