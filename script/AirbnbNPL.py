# -*- coding: utf-8 -*-
import jieba
import jieba.posseg
import pymongo
import sys
import re

reload(sys)
sys.setdefaultencoding('utf-8')

client = pymongo.MongoClient('mongodb://yc:yc@ycsin.cn:27017')
db = client['data']

dataset = db['airbnb'].find()

for data in dataset:
    if ("location" in data.keys()) and ("tags" not in data.keys()):
        location = data['location'].encode('utf8')
        if location == 'None':
            continue

        words_list = jieba.posseg.cut(location)
        tags = []
        for segment, flag in words_list:
            if flag in ['uj', 'p', 'c', 'm', 'd', 'x', 'r', 'ul', 'u', 'eng']:  # 过滤部分词性
                continue
            if segment in ['是', '有', 'the', '可', '请']:
                continue

            tags.append({
                'flag': flag,
                'segment': segment
            })

        db['airbnb'].update_one({'id': data['id']}, {'$set': {'tags': tags}})

# print ' '.join(seg_list)
