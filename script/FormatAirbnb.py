import pymongo

client = pymongo.MongoClient('mongodb://yc:yc@localhost:27017')
db = client['data']

ret = db['airbnb'].find()

for ab in ret:
    if "2019-06-17" in ab.keys():
        db['airbnb'].update_one(
            {'id': ab['id']},
            {'$push': {'calendar': {'2019-06-17': ab['2019-06-17']}}})
        # print ab['2019-06-17']
