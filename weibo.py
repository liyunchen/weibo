# -*- coding: utf-8 -*-
"""
Created on Sun Jul 19 12:03:56 2020

@author: 李运辰
"""
import requests
import time
import os
import json
from stylecloud import gen_stylecloud 
import jieba
from flask_cors import CORS
from flask import Flask,render_template,request,Response,redirect,url_for
#内网ip
app = Flask(__name__)
###此处改为自己的ip地址，在index.html中两次也记得更改
ip="192.168.0.112"
###
root="static/data/"
pagedata="pagedata/"
textdata="textdata/"

# 睡眠时间 传入int为休息时间，页面加载和网速的原因 需要给网页加载页面元素的时间
def s(int):
    time.sleep(int)
headers = {
        
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
      }
"""初始化"""
def initialization():
    #初始化爬取记录文本
    if not os.path.exists(root):
        os.mkdir(root)
    if not os.path.exists(root+pagedata):
        os.mkdir(root+pagedata)
    if not os.path.exists(root+textdata):
        os.mkdir(root+textdata)

def write(path,t):
    #记录当前爬取页数
    with open(path,"a+",encoding='utf8') as f:
        f.writelines(str(t))
        f.writelines("\n")
        
def search(name_s,url,since_id):
      
      #url = "https://m.weibo.cn/api/container/getIndex?uid=1566301073&t=0&luicode=10000011&lfid=100103type=1&q=贾玲&type=uid&value=1566301073&containerid=1076031566301073"
      start=1
      if since_id is not None and len(since_id)>1:
          url+="&since_id="+since_id
          start=0
      response = requests.get(url,headers = headers)
      
      datas = response.json()
      #print(data)
      ok = str(datas['ok'])
      try:
          with open(root+pagedata+name_s+".txt","r") as f:    #设置文件对象
              pagelist = f.read() 
      except:
          pagelist=[]
      
      if ok is not None and ok=='1':
          data = datas['data']
          since_ids = data['cardlistInfo']['since_id']
          print(since_ids)
          cards = data['cards']
          print(len(cards))
          for i in range(start,len(cards)):
               date = cards[i]['mblog']['created_at']
               if str(date) not in pagelist:
                   text1 = cards[i]['mblog']['text']
                   write(root+textdata+name_s+".txt",clean(text1))
                   write(root+pagedata+name_s+".txt",date)

"""去掉表情...,等html标签"""
def clean(s):
    istart=-1
    try:
        istart = s.index('<')
        iend = s.index('>')
        s = s[:istart]+s[iend+1:] 
    except:
        pass    
    try:
      istart = s.index('<')
    except:
        pass
    if istart>=0:
        return clean(s)
    else:
        #print(s)
        return(s)

def geturl(name_g):
    url1="https://m.weibo.cn/api/container/getIndex?containerid=100103type=1%26q="+name_g+"&page_type=searchall"
    response = requests.get(url1,headers = headers)          
    datas = response.json()
    uid = str(datas['data']['cards'][0]['card_group'][0]['user']['id'])
    newurl = "https://m.weibo.cn/api/container/getIndex?uid="+uid+"&t=0&luicode=10000011&lfid=100103type=1&q="+name_g+"&type=uid&value="+uid+"&containerid=107603"+uid
    return newurl

def jieba_cloud(file_name,icon):
    with open(file_name,'r',encoding='utf8') as f:
        word_list = jieba.cut(f.read())
        result = " ".join(word_list) #分词用 隔开
        #制作中文云词
        icon_name=""
        if icon=="1":
            icon_name=''
        elif icon=="2":
            icon_name='fas fa-dragon'
        elif icon=="3":
            icon_name='fas fa-dog'
        elif icon=="4":
            icon_name='fas fa-cat'
        elif icon=="5":
            icon_name='fas fa-dove'
        elif icon=="6":
            icon_name='fab fa-qq'
        """
        # icon_name='',#国旗
        # icon_name='fas fa-dragon',#翼龙
        icon_name='fas fa-dog',#狗
        # icon_name='fas fa-cat',#猫
        # icon_name='fas fa-dove',#鸽子
        # icon_name='fab fa-qq',#qq
        """
        picp=file_name.split('.')[0] +str(icon)+'.png'
        if icon_name is not None and len(icon_name)>0:
            gen_stylecloud(text=result,icon_name=icon_name,font_path='simsun.ttc',output_name=picp) #必须加中文字体，否则格式错误
        else:
            gen_stylecloud(text=result,font_path='simsun.ttc',output_name=picp) #必须加中文字体，否则格式错误
            
    return picp
############################flask路由
#进入首页
@app.route('/')
def index():
    return render_template('index.html')
#获取图片
@app.route('/find')
def find():
    #global history
    #采集数据
    name_i = request.args.get('name')
    
    if not os.path.exists(root+textdata+name_i+'.txt'):
        u = geturl(name_i)
        search(name_i,u,"")
    #制作词云
    file_name = root+textdata+name_i+'.txt'
    picpath = jieba_cloud(file_name,"1")
    
    return Response(json.dumps(picpath), mimetype='application/json')
#切换图标
@app.route('/switchs')
def switchs():
    #global history
    #采集数据
    name_i = request.args.get('name')
    icon = request.args.get('ic')
    #制作词云
    file_name = root+textdata+name_i+'.txt'
    picpath = jieba_cloud(file_name,str(icon))
    return Response(json.dumps(picpath), mimetype='application/json')
############################end
      
if __name__ == "__main__":    
    """初始化"""
    initialization()
    app.run(host=''+ip, port=5000,threaded=True)

