for i,name in enumerate(['tw','in','ts']):
    topiclist = Geturl()
    url1 = topiclist[i]['url1']
    df = Getarticle1(url1=url1,nums=Getpage1(url1),auto=True,days=1)
    Save2DB1(name+'list',df)
    
    url2list = df.url2.tolist()
    df = pd.concat(list(map(Getarticle2,url2list,[1]*len(url2list))))
    Save2DB2(name+'news',df)
