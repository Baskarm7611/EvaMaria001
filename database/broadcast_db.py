import pymongo

from info import DATABASE_URI, DATABASE_NAME

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

myclient = pymongo.MongoClient(DATABASE_URI)
mydb = myclient[DATABASE_NAME]
mycol = mydb['broadcast_config']   

async def new_broadcast(broadcast_id, total_users,msg_id, chat_id):
    mycol.insert_one({
        'broadcast_id': broadcast_id,
        'ongoing': True,
        'total_users':total_users,
        'broadcast_message_id': msg_id,
        'chat_id': chat_id,
        'total_users_done': 0
    })

async def get_broadcast_info(broadcast_id):
    return mycol.find_one({"broadcast_id": broadcast_id})

async def update_broadcast(broadcast_id, value:dict):
    myquery = {"broadcast_id": broadcast_id,}
    newvalues = { "$set": value }
    return mycol.update_one(myquery, newvalues)

async def filter_broadcast(dict):
    return mycol.find(dict)