import pymongo

client = pymongo.MongoClient('mongodb://yc:yc@ycsin.cn:27017')
db = client['data']

ret = db['airbnb'].find()

for ab in ret:
    if "2019-06-19" in ab.keys():
        dic = dict(ab['2019-06-19'])
        dic['date'] = '2019-06-19'
        db['airbnb'].update_one(
            {'id': ab['id']},
            {'$push': {'calendar': dic}})
        # print ab['2019-06-17']
