from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import numpy as np
from selenium.webdriver.chrome.options import Options
import os
from  selenium.webdriver.common.by  import  By
import re
#显式等待模块
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from lxml import etree
import json
import threading 

user_agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36 Edg/110.0.1587.63'


#主要函数：使用qq完成登陆
def login(driver):
    driver.get(url)
    try:            
        # 打开的QQ登陆界面    
        driver.find_element(By.XPATH,'//*[@id="root"]/div/main/div/div/div/div/div[2]/div/div[3]/span/button[2]').click()
        time.sleep(2)
       
        allhandles = driver.window_handles #获取所有窗口句柄
        zhihuHandle = driver.current_window_handle #获取知乎登陆句柄
        qqHandle = allhandles[1]   #获取QQ登陆句柄
        driver.switch_to.window(qqHandle) #控制权转换到QQ登陆窗口
        driver.switch_to.frame(driver.find_element(By.XPATH,value='/html/body/div[2]/div[1]/div/iframe')) #切换到frame内
        print('切换frame……')
        login_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[4]/div[8]/div/a/span[4]'))).click()
        time.sleep(3)
        #显示等待 ----判断是否登陆成功
        driver.switch_to.window(zhihuHandle)
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/header/div[2]/div[2]/div[3]/div[1]/button/img"))).click()
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[5]/div/div/div/div/a[1]"))).click()
        ###此处修改为跳转到个人页面
        print('login successfully!')
    except: print('error!')
    finally:
        pass

# 缺省信息补充，应对爬取目标为公众机构
def supplement(basic_information):
    if basic_information == {}:
        basic_information['昵称'] = '#'
        basic_information['文章数']='#'
        basic_information['回答数']='#'
        basic_information['提问数']='#'
        basic_information['粉丝数']='#'
        basic_information['偶像数']='#'
        basic_information['链接']='#'
        for i in range(10):
            basic_information.append('#')
        return basic_information
    else: 
        return basic_information
    

#主要函数：采集一个用户的基本信息
def get_basic_information(main_url,driver):
    '''
    parameter
    :main_url: 某博主的主界面,即people/**
    :driver:使用的浏览器->应对多线程
    :return: [昵称, 性别，个人简介，居住地，所在行业，职业经历, 文章数, 回答问题数,提问数 粉丝数, 链接地址]
    '''
    driver.get(main_url)
    #以字典形式存储基本信息
    basic_information = {} 

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/main/div/div[1]/div/div[2]/div/div[2]/div[3]/button'))).click() # 点击“查看详细资料”按钮
    except:
        return supplement(basic_information) #出错，缺省补充
    name = driver.find_element(By.XPATH, '/html/body/div[1]/div/main/div/div[1]/div/div[2]/div/div[2]/div[1]/h1/span[1]').text 
    basic_information['昵称'] = name

    #性别，个人简介，居住地，所在行业，职业经历
    get_top_info(basic_information,driver)

    #回答问题数、提问数、文章数、关注者人数,偶像数,url
    articles_num, answer_num,question_num = get_answers_num(main_url,driver)
    fans_num, idol_num = get_hit_num(driver.current_url,driver)
    basic_information['文章数']=articles_num
    basic_information['回答数']=answer_num
    basic_information['提问数']=question_num
    basic_information['粉丝数']=fans_num
    basic_information['偶像数']=idol_num
    basic_information['链接']=driver.current_url
    return supplement(basic_information)

#辅助函数：获取某人关注的人的url
def get_hit_url(num,main_url,driver):
    '''
    :main_url:我的主页
    :num:所要获取的url的数量
    !!未对num进行检查，可能存在越界
    '''
    num = int(num)
    href = []
    for i in range(1,21):
        href.append('/html/body/div[1]/div/main/div/div[2]/div[1]/div/div[3]/div/div[2]/div[%d]/div/div/div[2]/h2/span/div/span/div/a/@href'%i)
    
    hit_url = [] #存放大v主页url
    page_num = num // 20 
    num_mod = num % 20 
    for i in range(1,page_num+1):
        url = main_url + '?page=%d'%i
        driver.get(url)
        content = driver.page_source #获取源码
        selector = etree.HTML(content) #解析为html
        for j in href:
            tmp = "https:" + str(selector.xpath(j)[0])
            hit_url.append(tmp)

    try:
    #获取最后一页的大v
        url = main_url + '?page=%d'%(page_num+1)
        driver.get(url)
        content = driver.page_source #获取源码
        selector = etree.HTML(content) #解析为html
        for i in range(num_mod):
            tmp = "https:" + str(selector.xpath(href[i])[0])
            hit_url.append(tmp)
    except: pass
    return hit_url

#获取10个粉丝的url
def get_fans_url(main_url,driver):
    follower_url = main_url + '/followers'
    driver.get(follower_url)
    fans_url = []
    for i in range(1,11):
        try:
            tmp = driver.find_element(By.XPATH,'//*[@id="Profile-following"]/div[2]/div[%d]//div[@class="css-1gomreu"]/a'%i).get_attribute('href')
            fans_url.append(tmp)
        except:
            break
    return fans_url

#辅助函数：获取我的粉丝数和偶像数
def get_hit_num(main_url,driver):
    '''
    parameter
    :main_url: 主页urlfans_url.append
    return 
    :fans_num:粉丝数
    :idol_num:偶像数
    '''
    driver.get(main_url)
    tmp = driver.find_elements(By.CLASS_NAME,'NumberBoard-itemValue')
    idol_num = tmp[0].text
    fans_num = tmp[1].text
    return fans_num, idol_num

#辅助函数：获取顶部信息栏的信息
def get_top_info(basic_information,driver):
    '''
    本函数用于处理顶部信息栏数据
    传入信息列表，直接修改
    '''
    tmp = driver.find_element(By.XPATH,'/html/body/div[1]/div/main/div/div[1]/div/div[2]/div/div[2]/div[2]/div/div').get_attribute('innerText')
    temp = tmp.split('\n')
    info_list = [s for s in temp if s] #生成列表
    get_gender(basic_information,driver)
    add_str('个人简介',info_list,basic_information,driver)
    add_str('居住地',info_list,basic_information,driver)
    add_str('所在行业',info_list,basic_information,driver)
    add_str('职业经历',info_list,basic_information,driver)

#get_top_info的辅助函数
def add_str(st,info_list,basic_information,driver):
    '''
    :st: 待搜索的字符串
    :info_list: 待搜索的列表
    :basic_information:目标列表
    从顶部信息栏获取一堆数据，进行数据清洗筛查
    '''
    if st not in info_list:
        result = '#'
    else: 
        try:
            result = info_list[info_list.index(st)+1]
        except:
            result = '#'
    basic_information[st] = result

#get_top_info辅助函数：获取性别信息    
def get_gender(basic_information,driver):
    try:
        tmp = driver.find_element(By.XPATH,'/html/body/div[1]/div/main/div')
        temp = tmp.find_element(By.XPATH,"//*[@itemprop='gender']").get_attribute('content')
        result = '男' if temp == 'Male' else '女'
    except:
        result = '#'
    basic_information['性别'] = result

#get_social_info的辅助函数：获取粉丝或者偶像的关注者人数、回答数、文章数
def finds_num(index,driver):
    '''
    parameter
    :index:粉丝或偶像的编号
    :driver:浏览器引擎
    return
    文章数、回答数、关注者人数
    '''
    articles_num = 0
    answers_num  = 0
    followers_num = 0
    for i in range(1,4):
        try:
            tmp = driver.find_element(By.XPATH,'//*[@id="Profile-following"]/div[2]/div[%d]/div/div/div[2]/div/div/div[2]/span[%d]'%(index,i)).text
            if '文章' in tmp:
                ii = tmp.index('文')
                articles_num = tmp[0:ii]
            elif '回答' in tmp:
                ii = tmp.index('回')
                answers_num = tmp[0:ii]
            elif '关注者' in tmp:
                ii = tmp.index('关')
                followers_num = tmp[0:ii]
        except:
            pass
    return articles_num,answers_num,followers_num

#主函数，爬取社交关系信息
def get_social_info(main_url,driver):
    #爬取粉丝信息
    driver.get(main_url + '/followers')
    time.sleep(1.5)
    follower_info = []
    for i in range(1,11):
        follower_tmp = {}
        try:
            name = driver.find_element(By.XPATH,'//*[@id="Profile-following"]/div[2]/div[%d]/div/div/div[2]/h2/span/div/span/div/a'%i).text
            link = driver.find_element(By.XPATH,'//*[@id="Profile-following"]/div[2]/div[%d]/div/div/div[2]/h2/span/div/span/div/a'%i).get_attribute('href')
            head_link = driver.find_element(By.XPATH,'//*[@id="Profile-following"]/div[2]/div[%d]//img'%i).get_attribute('src')
        except:
            follower_tmp['粉丝名称'] ='#'
            follower_tmp['链接'] ='#'
            follower_tmp['文章数']='#'
            follower_tmp['回答数'] ='#'
            follower_tmp['关注者人数'] ='#'
            follower_tmp['头像链接'] = 'static/picture/noname.jpg'
            follower_info.append(follower_tmp)
            continue
        articles_num,answes_num,followers_num = finds_num(i,driver)
        follower_tmp['粉丝名称'] = name
        follower_tmp['链接'] = link
        follower_tmp['文章数'] =articles_num
        follower_tmp['回答数'] = answes_num
        follower_tmp['关注者人数'] = followers_num
        follower_tmp['头像链接'] = head_link

        follower_info.append(follower_tmp)


    #爬取偶像的社交信息
    driver.get(main_url+'/following')
    time.sleep(1)
    idol_info = []
    for j in range(1,11):
        idol_tmp = {}
        try:
            name = driver.find_element(By.XPATH,'//*[@id="Profile-following"]/div[2]/div[%d]/div/div/div[2]/h2/span/div/span/div/a'%j).text
            link = driver.find_element(By.XPATH,'//*[@id="Profile-following"]/div[2]/div[%d]/div/div/div[2]/h2/span/div/span/div/a'%j).get_attribute('href')
            head_link = driver.find_element(By.XPATH,'//*[@id="Profile-following"]/div[2]/div[%d]//img'%j).get_attribute('src')
        except:
            idol_tmp['偶像名称'] = '#'
            idol_tmp['链接'] = '#'
            idol_tmp['文章数'] ='#'
            idol_tmp['回答数'] = '#'
            idol_tmp['关注者人数'] = '#'
            idol_tmp['头像链接'] = 'static/picture/noname.jpg'
            continue
        articles_num,answes_num,idol = finds_num(j,driver)
        idol_tmp['偶像名称'] = name
        idol_tmp['链接'] = link
        idol_tmp['文章数'] =articles_num
        idol_tmp['回答数'] = answes_num
        idol_tmp['关注者人数'] = idol
        idol_tmp['头像链接'] = head_link

        #print(idol_tmp)
        idol_info.append(idol_tmp)
    return follower_info,idol_info
        

#cookis登陆
def cookies_login(driver):
    driver.get(url)
    f = open('./cookies.json','r')
    cookie = f.read()
    cookies = json.loads(cookie)
    for i in cookies:
        driver.add_cookie(i)
    driver.refresh()

#辅助函数:获得博主文章数、回答数、提问数
def get_answers_num(main_url,driver):
    driver.get(main_url)
    # 博主文章数目
    articles_num = driver.find_element(By.XPATH, "//li[@aria-controls='Profile-posts']/a/span").get_attribute('innerText')
    # 博主问题回答数 
    answers_num = driver.find_element(By.XPATH, "//*[@id='root']/div/main/div/meta[7]").get_attribute('content')
    question_num = driver.find_element(By.XPATH, "//li[@aria-controls='Profile-asks']/a/span").get_attribute('innerText')
    return articles_num, answers_num,question_num

#下拉窗口-上拉窗口-下拉窗口
def roll_window(driver):
    #driver.execute_script("document.body.style.zoom='50%'")
    driver.execute_script("window.scrollTo(0,100000)")  # 将滚动条拖动到元素可见的地方
    time.sleep(1)
    driver.execute_script("window.scrollTo(0,-100000)")  # 将滚动条拖动到元素可见的地方
    driver.execute_script("window.scrollTo(0,100000)")  # 将滚动条拖动到元素可见的地方

#上拉窗口-下拉窗口  避免长时间在底部等待的情况
def reroll_window(driver):
    #driver.execute_script("document.body.style.zoom='50%'")
    driver.execute_script("window.scrollTo(0,-100000)")  # 将滚动条拖动到元素可见的地方
    driver.execute_script("window.scrollTo(0,100000)")  # 将滚动条拖动到元素可见的地方

#主要函数：完成任务三，获取动态信息，执行前需要执行get_answers_num
def get_all_comment(main_url,question_num,answer_num,driver):
    '''
    完成动态信息的获取
    1. 获取每个回答的点赞数、评论数、发布时间、内容
    2. 获取每个回答评论信息 min(10,answers_num)
    parameter
    :main_url: 博主主页
    :question_num: 提问数
    :answer_num:回答数
    return
    :result(list): [{'点赞数','评论数','发布时间','内容','评论1':{评论者,评论时间,评论内容}} ……]  存放十个回答信息
    :result_2(list): [{'标题','发布时间','回答数','关注数','回答1':{回答者ID、回答时间、回答点赞数、回答内容} ……}] 存放十个提问信息
    '''
    #获取回答信息
    result = [] #用来存放回答信息
    driver.get(main_url + '/answers')
    for i in range(1,min(11,int(answer_num)+1)):
        every_ans_tmp = {}
        #获取回答信息：标题、点赞数、评论数、发布时间、内容
        element1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="Profile-answers"]/div[2]/div[%d]/div/div/div[2]/span/div/button'%i)))#显式等待
        driver.execute_script("arguments[0].click();",element1) #点击阅读全文
        #time.sleep(1)#等待加载改 
        element1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='Profile-answers']/div[2]/div[%d]/div/div/div[2]/span[1]/div/div/span"%i))) #增加
        time.sleep(1)
        content = driver.find_element(By.XPATH,"//*[@id='Profile-answers']/div[2]/div[%d]/div/div/div[2]/span[1]/div/div/span"%i).text
        publish_time = driver.find_element(By.XPATH, "//*[@id='Profile-answers']/div[2]/div[%d]/div/div/meta[@itemprop='dateCreated']"%i).get_attribute("content")
        upvote_num = driver.find_element(By.XPATH,"//*[@id='Profile-answers']/div[2]/div[%d]/div/div/meta[@itemprop='upvoteCount']"%i).get_attribute('content')
        comment_num = driver.find_element(By.XPATH,"//*[@id='Profile-answers']/div[2]/div[%d]/div/div/meta[@itemprop='commentCount']"%i).get_attribute('content')
        title = driver.find_element(By.XPATH,"//*[@id='Profile-answers']/div[2]/div[%d]//a[@data-za-detail-view-element_name='Title']"%i).text
        every_ans_tmp["发布时间"] = publish_time
        every_ans_tmp["点赞数"] = upvote_num
        every_ans_tmp["评论数"] = comment_num
        every_ans_tmp["内容"] = content
        every_ans_tmp['标题'] = title
        #print(every_ans_tmp)
        #获取回答的评论信息：评论人昵称、评论点赞次数、评论时间、评论内容
        #print('评论数:',comment_num)
        time.sleep(1) #改为1-》0.5
        if int(comment_num) != 0:
                button=driver.find_element(By.XPATH, '//*[@id="Profile-answers"]/div[2]/div[%d]/div/div/div[2]/div/button[1]'%i)
                driver.execute_script("arguments[0].click();",button)     
                #print('点击成功')
        else:
            #print('无需点击')
            result.append(every_ans_tmp)
            #print(every_ans_tmp['评论数'])
            continue
        try:
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,("//*[@id='Profile-answers']/div[2]/div[%d]//div[@class='CommentContent css-1ygdre8']"%i))))#显式
            all_comments =  driver.find_elements(By.XPATH, ("//*[@id='Profile-answers']/div[2]/div[%d]//div[@class='CommentContent css-1ygdre8']"%i)) # 取出所有评论
            all_comment_nickname =  driver.find_elements(By.XPATH, ("//*[@id='Profile-answers']/div[2]/div[%d]//a[@class='css-1rd0h6f']"%i)) # 取出所有评论者昵称
            all_comments_date =  driver.find_elements(By.XPATH, "//*[@id='Profile-answers']/div[2]/div[%d]//span[@class='css-12cl38p']"%i) #取出所有评论时间
        except:
            pass
               
        for j in range(min(10,int(comment_num))): #取评论
            try:
                comment_tmp = {}
                comment = all_comments[j].text
                comment_date = all_comments_date[j].text
                commentator = all_comment_nickname[j].text
                comment_tmp['评论时间'] = comment_date 
                comment_tmp['评论者'] = commentator
                comment_tmp['评论内容'] = comment if comment != '' else '评论内容无法以文本显示'
                every_ans_tmp['评论%d'%(j+1)] = comment_tmp
            except:
                pass
        result.append(every_ans_tmp)
    #print(result[1]['评论1'])

    #收集提问信息:result_2 = [{'标题','发布时间','回答数','关注数',{回答1},{回答2}}]
    result_2 = []
    driver.get(main_url + '/asks')
    if question_num == 0:
        return result, result_2
    elements = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="Profile-asks"]/div[2]/div[1]/div/div/h2/span/div/a')))
    href_list = ['0']
    #获得提问链接
    for i  in range(1,min(11,int(question_num)+1)):
        href = driver.find_element(By.XPATH,'//*[@id="Profile-asks"]/div[2]/div[%d]/div/div/h2/span/div/a'%i).get_attribute('href') #获取提问url
        href_list.append(href)
    #依次打开提问链接，获取信息
    for i in range(1,min(11,int(question_num)+1)): 
        every_que_tmp = {} 
        driver.get(href_list[i])
        element2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='root']/div/main/div/div/meta[@itemprop='name']")))#显式等待
        title = driver.find_element(By.XPATH,"//*[@id='root']/div/main/div/div/meta[@itemprop='name']").get_attribute('content') #标题
        publish_time2 = driver.find_element(By.XPATH,"//*[@id='root']/div/main/div/div/meta[@itemprop='dateCreated']").get_attribute('content')
        answerCount = driver.find_element(By.XPATH,"//*[@id='root']/div/main/div/div/meta[@itemprop='answerCount']").get_attribute('content')
        subscribeCount = driver.find_element(By.XPATH,"//*[@id='root']/div/main/div/div/meta[@itemprop='zhihu:followerCount']").get_attribute('content')
        every_que_tmp['标题'] = title
        every_que_tmp['发布时间'] =publish_time2
        every_que_tmp['回答数'] =answerCount
        every_que_tmp['关注数'] =subscribeCount
        #print(every_que_tmp)
        driver.execute_script("document.body.style.zoom='0.5'")
        roll_window(driver)
        #driver.execute_script("document.body.style.zoom='0.5'")
        #爬取回答:回答者ID，回答时间,回答点赞数，回答内容
        for j in range(2,min(12,int(answerCount)+2)):
            answer_tmp = {}
            try:
                element2 = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "//*[@id='QuestionAnswers-answers']/div/div/div/div[2]/div/div[%d]/div/div/div[1]/div[1]//*[@itemprop='name']"%j)))
            except:
                    reroll_window(driver) #先往上翻，再往下翻  
            element3 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='QuestionAnswers-answers']/div/div/div/div[2]/div/div[%d]/div/div/div[1]/div[1]//*[@itemprop='name']"%j)))
            que_answerer_ID = driver.find_element(By.XPATH,"//*[@id='QuestionAnswers-answers']/div/div/div/div[2]/div/div[%d]/div/div/div[1]/div[1]//*[@itemprop='name']"%j).get_attribute('content')
            try:
                que_answer_content = driver.find_element(By.XPATH,'//*[@id="QuestionAnswers-answers"]/div/div/div/div[2]/div/div[%d]/div/div//span[@itemprop="text"]'%j).get_attribute('innerText')
            except:
                que_answer_content = '该回答无法以文本显示'
            que_answer_date = driver.find_element(By.XPATH,'//*[@id="QuestionAnswers-answers"]/div/div/div/div[2]/div/div[%d]/div/div/meta[@itemprop="dateCreated"]'%j).get_attribute('content') #获得回答时间
            que_answer_upvotenum = driver.find_element(By.XPATH,'//*[@id="QuestionAnswers-answers"]/div/div/div/div[2]/div/div[%d]/div/div/meta[@itemprop="upvoteCount"]'%j).get_attribute('content') #获得回答的点赞数
            answer_tmp['回答者ID'] = que_answerer_ID
            answer_tmp['回答时间']=que_answer_date
            answer_tmp['回答点赞数'] = que_answer_upvotenum
            answer_tmp['回答内容'] = que_answer_content
            every_que_tmp['回答%d'%(j-1)] = answer_tmp
        result_2.append(every_que_tmp)
    #print(result_2[0]['回答2'])
    return result, result_2 #返回回答信息，提问信息


#完成对一个大V的所有信息采集，便于后续开启多线程
def single_hit_collection(main_url):
    #启动浏览器，并设置参数
    options = webdriver.EdgeOptions()
    path = Service('C:\\Users\\杨建哲\\AppData\\Local\\Programs\\Python\\Python38\\msedgedriver.exe')
    options.add_argument('-log-level=3')
    options.add_argument('-ignore-certificate-errors')
    options.add_argument('-ignore -ssl-errors')
    #规避被检测到的风险
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) #使用开发者模式
    options.add_argument("--disable-blink-features=AutomationControlled") #禁用启用blink模式
    driver = webdriver.Edge(service=path,options=options,service_log_path=os.devnull)

    #cookies登陆
    cookies_login(driver)

    all_infomation = [] 

    #任务一： 基本信息采集
    #basic_info:  [昵称, 性别，个人简介，居住地，所在行业，职业经历, 文章数, 回答数, 提问数、粉丝数, 链接地址]
    basic_info = get_basic_information(main_url,driver)
    all_infomation.append(basic_info)

    #任务二： 社交关系采集
    follower_info, idol_info = get_social_info(main_url,driver)
    all_infomation.append(follower_info)
    all_infomation.append(idol_info)

    #任务三：动态信息采集
    '''
    answer_information:[{'点赞数','评论数','发布时间','内容','评论1':{评论者,评论时间,评论内容}} ……]
    question_information: [{'标题','发布时间','回答数','关注数','回答1':{回答者ID、回答时间、点赞数、回答内容} ……}]
    '''
    answer_information, question_information = get_all_comment(main_url,int(basic_info['提问数']),int(basic_info['回答数']),driver)
    all_infomation.append(answer_information)
    all_infomation.append(question_information)

    #写入json文件
    print(basic_info['昵称'] + '----已收集完毕')
    js = open('D:/content_ser1/info/{}.json'.format(basic_info['昵称']),'w')
    json.dump(all_infomation,js,indent=4)
    js.close()
    #更新索引列表
    with open('D:/content_ser1/info/all.json', 'r+', encoding = 'utf8') as fp:
        data = json.load(fp)
        if basic_info['昵称'] in data:
            data.remove(basic_info['昵称'])
        data.append(basic_info['昵称'])
    with open('D:/content_ser1/info/all.json', 'w', encoding = 'utf8') as fp:
        json.dump(data,fp,indent=4)
    print(basic_info['昵称'] + '----已写入文件')
    return 

if __name__ == '__main__':
    url='https://www.zhihu.com/signin?next=%2F'


    #获得我关注的大V的主页网址（十个大V）
    #hit_url = get_hit_url(10,driver.current_url + '/following') #获取我关注的前十个大V，为后续要爬取的对象

    hit_url = ['https://www.zhihu.com/people/sizhuren','https://www.zhihu.com/people/bo-cai-28-7','https://www.zhihu.com/people/zhu-tou-seng','https://www.zhihu.com/people/magie','https://www.zhihu.com/people/zhu-xuan-86','https://www.zhihu.com/people/zhang-xiao-bei','https://www.zhihu.com/people/kaifulee','https://www.zhihu.com/people/carlzhou','https://www.zhihu.com/people/qing-ren-feng','https://www.zhihu.com/people/hongsang','https://www.zhihu.com/people/xiao-er-gou-zhe']
    hit_url = ['https://www.zhihu.com/people/zhu-xuan-86']
    single_hit_collection(hit_url[0])
    #开启多线程加速
    #for i in range(1,11,2):
    #    thread0 = threading.Thread(target=single_hit_collection,args=[hit_url[i]],name=i)
    #    thread1 = threading.Thread(target=single_hit_collection,args=[hit_url[i+1]],name=i+1)
    #    thread0.start()
    #    thread1.start()
    #    thread0.join()
    #    thread1.join()
        



    
