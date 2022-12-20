# https://github.com/odysseusmax/animated-lamp/blob/master/bot/database/database.py
import time
import motor.motor_asyncio
from info import DATABASE_NAME, DATABASE_URI, IMDB, IMDB_TEMPLATE, MELCOW_NEW_USERS, P_TTI_SHOW_OFF, SINGLE_BUTTON, SPELL_CHECK_REPLY, PROTECT_CONTENT
from datetime import datetime

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups


    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
        )


    def new_group(self, id, title):
        return dict(
            id = id,
            title = title,
            shortener_api= None, 
            shortener_domain=None, 
            access_days=0, 
            last_verified=datetime(2020, 5, 17),
            has_access=False,
            chat_status=dict(
                is_disabled=False,
                reason="",
            ),
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        return await self.col.count_documents({})
    
    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_reason=''
        )
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})
    
    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = dict(
            is_banned=True,
            ban_reason=ban_reason
        )
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_reason=''
        )
        user = await self.col.find_one({'id':int(id)})
        return user.get('ban_status', default) if user else default

    async def get_all_users(self, offset=0):
        return self.col.find({}).skip(offset)
    
    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        chats = self.grp.find({'chat_status.is_disabled': True})
        b_chats = [chat['id'] async for chat in chats]
        b_users = [user['id'] async for user in users]
        return b_users, b_chats
    

    async def add_chat(self, chat, title):
        chat = self.new_group(chat, title)
        await self.grp.insert_one(chat)
    

    async def get_chat(self, chat):
        chat = await self.grp.find_one({'id':int(chat)})
        return chat.get('chat_status') if chat else False
    

    async def re_enable_chat(self, id):
        chat_status=dict(
            is_disabled=False,
            reason="",
            )
        await self.grp.update_one({'id': int(id)}, {'$set': {'chat_status': chat_status}})
        
    async def update_settings(self, id, settings):
        await self.grp.update_one({'id': int(id)}, {'$set': {'settings': settings}})
        
    
    async def get_settings(self, id):
        default = {
            'button': SINGLE_BUTTON,
            'botpm': P_TTI_SHOW_OFF,
            'file_secure': PROTECT_CONTENT,
            'imdb': IMDB,
            'spell_check': SPELL_CHECK_REPLY,
            'welcome': MELCOW_NEW_USERS,
            'template': IMDB_TEMPLATE
        }
        chat = await self.grp.find_one({'id':int(id)})
        return chat.get('settings', default) if chat else default
    

    async def disable_chat(self, chat, reason="No Reason"):
        chat_status=dict(
            is_disabled=True,
            reason=reason,
            )
        await self.grp.update_one({'id': int(chat)}, {'$set': {'chat_status': chat_status}})
    

    async def total_chat_count(self):
        return await self.grp.count_documents({})
    

    async def get_all_chats(self):
        return self.grp.find({})


    async def get_db_size(self):
        return (await self.db.command("dbstats"))['dataSize']


    async def set_group_api(self, api, domain, group_id):
        await self.grp.update_one({'id': group_id}, {'$set': {'shortener_api': api, "shortener_domain":domain}}, upsert=True)

    async def update_existing_groups(self, filter, update):
        return await self.grp.update_many(filter=filter,update=update)

    async def find_chat(self, group_id):
        return await self.grp.find_one({'id':int(group_id)})

    async def filter_chat(self, value):
        return self.grp.find(value)

    async def is_group_verified(self, group_id):
        group = await self.find_chat(group_id)
        access_days = datetime.fromtimestamp(time.mktime(group["last_verified"].timetuple()) + group['access_days'])
        return (access_days - datetime.now()).total_seconds() >= 0

    async def expiry_date(self, group_id):
        group = await self.find_chat(group_id)
        access_days = datetime.fromtimestamp(time.mktime(group["last_verified"].timetuple()) + group['access_days'])
        return access_days, int((access_days - datetime.now()).total_seconds())

    async def total_premium_groups_count(self):
        return await self.grp.count_documents({"has_access":True, "chat_status.is_disabled":False})

    async def update_group_info(self, group_id, value:dict, tag="$set"):
        group_id = int(group_id)
        myquery = {"id": group_id}
        newvalues = {tag : value }
        await self.grp.update_one(myquery, newvalues)

db = Database(DATABASE_URI, DATABASE_NAME)
