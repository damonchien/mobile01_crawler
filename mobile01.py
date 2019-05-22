import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import re
import time,datetime
import requests
from bs4 import BeautifulSoup
import pymysql
from sql_toolbox import SqlBase

def GetPageContent(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    res = requests.get(url, headers=headers)
    return res

def Geturl(topics=['台灣新聞','國際新聞','兩岸新聞']):
    res = GetPageContent('https://www.mobile01.com')
    soup = BeautifulSoup(res.text,'lxml')
    all_topic = soup.select_one('#top-menu').select('li')
    all_topic = [{'url1':each.find('a')['href'],'topic':each.text} for each in all_topic if 'topiclist' in each.find('a')['href']]

    topiclist=[]
    for topic in all_topic:
        if topic['topic'] in topics:
            topiclist.append(topic)
    return topiclist

def Getpage1(url1):
    res = GetPageContent('https://www.mobile01.com/'+url1)
    soup = BeautifulSoup(res.text,'lxml')
    return (int(soup.select('div.pagination')[-1].select('a')[-1].text))

def Getarticle1(url1,nums=1,auto=False,days=1):
    posts = list()
    if nums>Getpage1(url1):
        nums=Getpage1(url1)
    for num in range(1,nums+1):
        res = GetPageContent('https://www.mobile01.com/'+url1+'&p='+str(num))
        soup = BeautifulSoup(res.text,'lxml')
        url2s = soup.select('a.topic_gen')
        topics = soup.select('a.topic_gen')
        replys = soup.select('td.reply')
        authurs = soup.select('td.authur')
        latests = soup.select('td.latestreply')
        for i in range(len(soup.select('a.topic_gen'))):
            if auto:
                if pd.to_datetime(latests[i].text[:16]).date()<(datetime.date.today()-datetime.timedelta(days)):
                    return pd.DataFrame(posts)
            posts.append({'url2': url2s[i]['href'],
                          'topic': topics[i].text,
                          'reply': int(replys[i].text.replace(',','')),
                          'release': authurs[i].text[:16],
                          'authur': authurs[i].text[16:],
                          'latest': latests[i].text[:16] })
    return pd.DataFrame(posts)

def Getpage2(url2):
    res = GetPageContent('https://www.mobile01.com/'+url2)
    soup = BeautifulSoup(res.text,'lxml')
    return int(soup.select_one('div.contentfoot').select_one('p').text.split('共')[1][0])

def Getarticle2(url2,nums=1):
    posts = list()
    if nums>Getpage2(url2):
        nums=Getpage2(url2)
    for num in range(1,nums+1):
        res = GetPageContent('https://www.mobile01.com/'+url2+'&p='+str(num))
        soup = BeautifulSoup(res.text,'lxml')
        contents = soup.select('div.single-post-content')
        dates = soup.select('div.date')
        authurs = soup.select('div.fn')
        for i in range(len(soup.select('div.single-post-content'))):
            if len(contents[i].select('blockquote'))!=0:
                for con in contents[i].select('blockquote'):
                    con.decompose()
            posts.append({'url2': url2,
                          'date': dates[i].text.split()[0]+' '+dates[i].text.split()[1],
                          'floor':int(dates[i].text.split()[2][1:].replace(',','')),
                          'author': authurs[i].text.replace('樓主',''),
                          'content': contents[i].text.replace('\n','')})
    return pd.DataFrame(posts)

def Save2DB1(tb_name, df):
    sql = '''INSERT INTO {} VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE latest=VALUES(latest),reply=VALUES(reply)'''.format(tb_name)
    SqlBase().withoutResultMany(sql,df.values.tolist())
    return tb_name

def Save2DB2(tb_name, df):
    sql = '''INSERT INTO {} VALUES (%s, %s, %s , %s, %s) ON DUPLICATE KEY UPDATE author=VALUES(author),content=VALUES(content),datetime=VALUES(datetime)'''.format(tb_name)
    SqlBase().withoutResultMany(sql,df.values.tolist())
    return tb_name
