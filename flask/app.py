from flask import Flask
from flask import render_template
import json

app = Flask(__name__)
data_list = [0]
with open('D:/content_ser1/info/all.json', 'r', encoding='utf-8') as fp:
    info = json.load(fp)
with open('D:/content_ser1/info/{}.json'.format(info[-9]),'r',encoding='utf-8') as fp1:
    data1 = json.load(fp1)
    data_list.append(data1)
with open('D:/content_ser1/info/{}.json'.format(info[-8]),'r',encoding='utf-8') as fp2:
    data2 = json.load(fp2)
    data_list.append(data2)

with open('D:/content_ser1/info/{}.json'.format(info[-7]),'r',encoding='utf-8') as fp3:
    data3 = json.load(fp3)
    data_list.append(data3)

with open('D:/content_ser1/info/{}.json'.format(info[-6]),'r',encoding='utf-8') as fp4:
    data4 = json.load(fp4)
    data_list.append(data4)

with open('D:/content_ser1/info/{}.json'.format(info[-5]),'r',encoding='utf-8') as fp5:
    data5 = json.load(fp5)
    data_list.append(data5)

with open('D:/content_ser1/info/{}.json'.format(info[-4]),'r',encoding='utf-8') as fp6:
    data6 = json.load(fp6)
    data_list.append(data6)

with open('D:/content_ser1/info/{}.json'.format(info[-3]),'r',encoding='utf-8') as fp7:
    data7 = json.load(fp7)
    data_list.append(data7)

with open('D:/content_ser1/info/{}.json'.format(info[-2]),'r',encoding='utf-8') as fp8:
    data8 = json.load(fp8)
    data_list.append(data8)

with open('D:/content_ser1/info/{}.json'.format(info[-1]),'r',encoding='utf-8') as fp9:
    data9 = json.load(fp9)
    data_list.append(data9)


@app.route('/')
def show_basic_information():  # put application's code here
    return render_template('index.html',data1=data1,data2=data2,data3=data3,data4=data4,data5=data5,data6=data6,data7=data7,data8=data8,data9=data9)

#第一种路由方式，url变化，展示网页结构不变，内容根据参数改变,<index>由点击时触发的herf传参传入
@app.route('/<index>')
def show_social_information(index):  # put application's code here
    ind = int(index)
    cur_data = data_list[ind]

    return render_template('show_1.html',data=cur_data,index=ind)

@app.route('/<index1>/question_<index2>')
def show_answer(index1,index2):
    ind1 = int(index1)
    ind2 = int(index2)-1
    cur_data = data_list[ind1]
    return render_template('question_index.html',data=cur_data,index = ind2)

@app.route('/<index1>/answer_<index2>')
def show_comment(index1,index2):
    ind1 = int(index1)
    ind2 = int(index2)-1
    cur_data = data_list[ind1]
    return render_template('answer_index.html',data=cur_data,index = ind2)



if __name__ == '__main__':
    app.run()
