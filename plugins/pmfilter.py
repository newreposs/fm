import os
import re
import io
import pyrogram

from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import Config
from database.filters_helper import(
   add_filter,
   find_filter,
   get_filters,
   delete_filter,
   count_filters, 
   del_all
)
from pyrogram.enums import ParseMode
from functions.tools import add_user, all_users

from functions.tools import parser, split_quotes, get_file_id 



@Client.on_message(filters.command('add') & filters.user(Config.OWNERS))
async def addfilter(client, message):
      
    userid = message.from_user.id
    chat_type = message.chat.type
    args = message.text.html.split(None, 1)
    grp_id = Config.BOT_USERNAME
    chat = await client.get_users(grp_id)
    title = chat.first_name
        

    if len(args) < 2:
        await message.reply_text("Komut Eksik :(", quote=True)
        return
    
    extracted = split_quotes(args[1])
    text = extracted[0].lower()
   
    if not message.reply_to_message and len(extracted) < 2:
        await message.reply_text("Filtrenizi kaydetmek için bazı içerikler eklemelisin!", quote=True)
        return

    if (len(extracted) >= 2) and not message.reply_to_message:
        reply_text, btn, alert = parser(extracted[1], text)
        fileid = None
        if not reply_text:
            await message.reply_text("Tek başına butonlara sahip olamazsınız, onunla birlikte gitmek için biraz metin ver!", quote=True)
            return

    elif message.reply_to_message and message.reply_to_message.reply_markup:
        try:
            rm = message.reply_to_message.reply_markup
            btn = rm.inline_keyboard
            msg = message.reply_to_message.document or\
                  message.reply_to_message.video or\
                  message.reply_to_message.photo or\
                  message.reply_to_message.audio or\
                  message.reply_to_message.animation or\
                  message.reply_to_message.sticker
            if msg:
                fileid = msg.file_id
                reply_text = message.reply_to_message.caption.html
            else:
                reply_text = message.reply_to_message.text.html
                fileid = None
            alert = None
        except:
            reply_text = ""
            btn = "[]" 
            fileid = None
            alert = None

    elif message.reply_to_message and message.reply_to_message.photo:
        try:
            fileid = message.reply_to_message.photo.file_id
            reply_text, btn, alert = parser(message.reply_to_message.caption.html, text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None

    elif message.reply_to_message and message.reply_to_message.video:
        try:
            fileid = message.reply_to_message.video.file_id
            reply_text, btn, alert = parser(message.reply_to_message.caption.html, text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None

    elif message.reply_to_message and message.reply_to_message.audio:
        try:
            fileid = message.reply_to_message.audio.file_id
            reply_text, btn, alert = parser(message.reply_to_message.caption.html, text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None
   
    elif message.reply_to_message and message.reply_to_message.document:
        try:
            fileid = message.reply_to_message.document.file_id
            reply_text, btn, alert = parser(message.reply_to_message.caption.html, text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None

    elif message.reply_to_message and message.reply_to_message.animation:
        try:
            fileid = message.reply_to_message.animation.file_id
            reply_text, btn, alert = parser(message.reply_to_message.caption.html, text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None
if len(args) < 2:

        return await message.reply_text("Ne yazdın anlamadım. Örnek: `/filter esenlikler size de esenlikler`", quote=True)

    extracted = split_quotes(args[1])
    text = unicode_tr(extracted[0]).lower()

    if not message.reply_to_message and len(extracted) < 2:
        return await message.reply_text("Add some content to save your filter!", quote=True)

    if (len(extracted) >= 2) and not message.reply_to_message:
        reply_text, btn, alert = parser(extracted[1], text)
        fileid = None
        if not reply_text:
            return await message.reply_text("Butonları yazısız mı yaratayım? Yazı ver onlara çabuk.", quote=True)

    elif message.reply_to_message and message.reply_to_message.reply_markup:
        try:
            rm = message.reply_to_message.reply_markup
            btn = rm.inline_keyboard
            msg = get_file_id(message.reply_to_message)
            if msg:
                fileid = msg.file_id
                reply_text = message.reply_to_message.caption.html
            else:
                reply_text = message.reply_to_message.text.html
                fileid = None
            alert = None
        except Exception:
            reply_text = ""
            btn = "[]"
            fileid = None
            alert = None

    elif message.reply_to_message and message.reply_to_message.media:
        try:
            msg = get_file_id(message.reply_to_message)
            fileid = msg.file_id if msg else None
            reply_text, btn, alert = parser(message.reply_to_message.caption.html, text)
        except Exception:
            reply_text = ""
            btn = "[]"
            alert = None
    elif message.reply_to_message and message.reply_to_message.text:
        try:
            fileid = None
            reply_text, btn, alert = parser(message.reply_to_message.text.html, text)
        except Exception:
            reply_text = ""
            btn = "[]"
            alert = None
    else: return

    await add_filter(grp_id, text, reply_text, btn, fileid, alert)    

    await message.reply_text(
        f"Filtre  `{text}` için  **{title}** botuna eklendi!",
        quote=True,
        parse_mode=ParseMode.MARKDOWN
    )


@Client.on_message(filters.command('viewfilters') & filters.user(Config.OWNERS))
async def get_all(client, message):
    
    chat_type = message.chat.type
    userid = message.from_user.id
    grp_id = Config.BOT_USERNAME
    chat = await client.get_users(grp_id)
    title = chat.first_name

    texts = await get_filters(grp_id)
    count = await count_filters(grp_id)

    if count:
        filterlist = f"**{title}** için tüm filterlar: {count}\n\n"

        for text in texts:
            keywords = " ×  `{}`\n".format(text)
            
            filterlist += keywords

        if len(filterlist) > 4096:
            with io.BytesIO(str.encode(filterlist.replace("`", ""))) as keyword_file:
                keyword_file.name = "keywords.txt"
                await message.reply_document(
                    document=keyword_file,
                    quote=True
                )
            return
    else:
        filterlist = "**{title}** için hiç filter yok!"
    await message.reply_text(
        text=filterlist,
        quote=True,
        parse_mode=ParseMode.MARKDOWN
    )
        
@Client.on_message(filters.command('del') & filters.user(Config.OWNERS))
async def deletefilter(client, message):
    userid = message.from_user.id
    chat_type = message.chat.type

    grp_id = Config.BOT_USERNAME
    chat = await client.get_users(grp_id)
    title = chat.first_name

    try:
        cmd, text = message.text.split(" ", 1)
    except:
        await message.reply_text(
            "<i>Silmek istediğiniz filtre adını belirtin!</i>\n\n"
            "<code>/del filterismi</code>\n\n"
            "Tüm filterları görmek için /viewfilters ı kulan!",
            quote=True
        )
        return

    query = text.lower()

    await delete_filter(message, query, grp_id)
        

@Client.on_message(filters.command('delall') & filters.user(Config.OWNERS))
async def delallconfirm(client, message):
    userid = message.from_user.id
    chat_type = message.chat.type
    group_id = Config.BOT_USERNAME
    chat = await client.get_users(group_id)
    title = chat.first_name
    await del_all(client, message, group_id, title)

@Client.on_message(filters.private & filters.text)
async def give_filter(client,message):
    group_id = Config.BOT_USERNAME
    name = message.text

    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            await message.reply_text(reply_text, disable_web_page_preview=True)
                        else:
                            button = eval(btn)
                            await message.reply_text(
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button)
                            )
                    else:
                        if btn == "[]":
                            await message.reply_cached_media(
                                fileid,
                                caption=reply_text or ""
                            )
                        else:
                            button = eval(btn) 
                            await message.reply_cached_media(
                                fileid,
                                caption=reply_text or "",
                                reply_markup=InlineKeyboardMarkup(button)
                            )
                except Exception as e:
                    print(e)
                    pass
                break 
                
    if Config.SAVE_USER == "yes":
        try:
            await add_user(
                str(message.from_user.id),
                str(message.from_user.username),
                str(message.from_user.first_name + " " + (message.from_user.last_name or "")),
                str(message.from_user.dc_id)
            )
        except:
            pass
      
