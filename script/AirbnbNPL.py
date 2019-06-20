# -*- coding: utf-8 -*-
import jieba
import jieba.posseg
import pymongo
import sys
import re

reload(sys)
sys.setdefaultencoding('utf-8')


def sort_by_value(d):
    items = d.items()
    backitems = [[v[1], v[0]] for v in items]
    backitems.sort()
    return [backitems[i][1] for i in range(0, len(backitems))]


client = pymongo.MongoClient('mongodb://yc:yc@ycsin.cn:27017')
db = client['data']
dataset = db['airbnb'].find()

file = open('words', 'w')

words_frequency = {}

for data in dataset:
    if "location" in data.keys():
        location = data['location'].encode('utf8')
        if location == 'None':
            continue
        file.write(location)
        file.write('\r')

        words_list = jieba.posseg.cut(location)
        for word, flag in words_list:
            key = '%s[%s]' % (word, flag)
            if key not in words_frequency.keys():
                words_frequency[key] = 1
            else:
                words_frequency[key] += 1

file.flush()
file.close()

file = open('words_freq', 'w')
list = sorted(words_frequency.items(), key=lambda d: d[1], reverse=True)

for item in list:
    flag = re.findall('\[(.*)\]', item[0])[0]
    if flag in ['uj', 'p', 'c', 'm', 'd', 'x', 'r', 'ul', 'u', 'eng']:  # 过滤部分词性
        continue
    flag = re.findall('^(.*)\[.*\]', item[0])[0]
    if flag in ['是', '有', 'the', '可', '请']:
        continue
    file.write('%s : %s' % (item[0], item[1]))
    file.write('\r')

file.flush()
file.close()

# print ' '.join(seg_list)
