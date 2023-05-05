import json


#读取json文件
with open('D:/content_ser1/info/猪头僧.json', 'r', encoding = 'utf8') as fp:
    json_data = json.load(fp)
print(json_data[4][0]['回答1'].keys())
