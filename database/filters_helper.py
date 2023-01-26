import os
import re
import pymongo
from config import Config
from pyrogram.enums import ParseMode 

myclient = pymongo.MongoClient(Config.DATABASE_URL)
mydb = myclient[Config.SESSION_NAME]



async def add_filter(grp_id, text, reply_text, btn, file, alert):
    mycol = mydb[str(grp_id)]
    # mycol.create_index([('text', 'text')])

    data = {
        'text':str(text),
        'reply':str(reply_text),
        'btn':str(btn),
        'file':str(file),
        'alert':str(alert)
    }

    try:
        mycol.update_one({'text': str(text)},  {"$set": data}, upsert=True)
    except:
        print('Kaydedilmedi Logu kontor et')
             
     
async def find_filter(group_id, name):
    mycol = mydb[str(group_id)]
    
    query = mycol.find( {"text":name})
    # query = mycol.find( { "$text": {"$search": name}})
    try:
        for file in query:
            reply_text = file['reply']
            btn = file['btn']
            fileid = file['file']
            try:
                alert = file['alert']
            except:
                alert = None
        return reply_text, btn, alert, fileid
    except:
        return None, None, None, None


async def get_filters(group_id):
    mycol = mydb[str(group_id)]

    texts = []
    query = mycol.find()
    try:
        for file in query:
            text = file['text']
            texts.append(text)
    except:
        pass
    return texts


async def delete_filter(message, text, group_id):
    mycol = mydb[str(group_id)]
    
    myquery = {'text':text }
    query = mycol.count_documents(myquery)
    if query == 1:
        mycol.delete_one(myquery)
        await message.reply_text(
            f"`'`{text}`'  Silindi.`",
            quote=True,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await message.reply_text("Böyle Bişi yok aq!", quote=True)


async def del_all(client, message, group_id, title):
    if str(group_id) not in mydb.list_collection_names():
        await client.send_message(
            chat_id=message.chat.id,
            text=f"Nothing to remove in {title}!")
        return
        
    mycol = mydb[str(group_id)]
    try:
        mycol.drop()
        await client.send_message(
            chat_id=message.chat.id, 
            text=f"{title} için tüm filterlar silindi!")
    except:
        await client.send_message(
            chat_id=message.chat.id, 
            text=f"Couldn't remove all filters from group!")
        return


async def count_filters(group_id):
    mycol = mydb[str(group_id)]

    count = mycol.count_documents({})
    if count == 0:
        return False
    else:
        return count


async def filter_stats():
    collections = mydb.list_collection_names()

    if "CONNECTION" in collections:
        collections.remove("CONNECTION")
    if "USERS" in collections:
        collections.remove("USERS")

    totalcount = 0
    for collection in collections:
        mycol = mydb[collection]
        count = mycol.count_documents({})
        totalcount = totalcount + count

    totalcollections = len(collections)

    return totalcollections, totalcount
