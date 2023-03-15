import logging
import asyncio

from pyrogram import Client
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, FloodWait
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from pyrogram.enums import ChatMemberStatus
from database.database import db
from database.add import add_user_to_database
from translation import Translation
from config import Config


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)


async def handle_force_subscribe(client, message):
    user_id = message.from_user.id
    start_time = datetime.now()
    await add_user_to_database(client, message)
    try:
        user = await client.get_chat_member(Config.AUTH_CHANNEL, user_id)
        if user.status == ChatMemberStatus.BANNED:
            await client.delete_messages(
                chat_id=message.chat.id,
                message_ids=message.id,
                revoke=True
            )
            return 400
    except UserNotParticipant:
        pass
        date = start_time + timedelta(seconds=120)
        try:
            invite_link = await client.create_chat_invite_link(chat_id=Config.AUTH_CHANNEL, creates_join_request=True, expire_date=60)
        except ChatAdminRequired:
            LOGGER.error("Bot'un Forcesub kanalında yönetici olduğundan emin olun.")
            return
        btn = [
            [
                InlineKeyboardButton(
                    Translation.BUTTON_TEXT, url=invite_link.invite_link
                )
            ]
        ]
        await client.send_message(
            chat_id=user_id,
            text=f"Bu Botu Kullanabilmek İçin Kanalıma Katılma Gerekir Lütfen katıldıktan sonra tekrar dene.\n\n{invite_link.invite_link}",
            reply_markup=InlineKeyboardMarkup(btn),
            reply_to_message_id=message.id,
        )
        return 400
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return 400
    except Exception as e:
        await client.send_message(
            chat_id=user_id,
            text="Bir şeyler ters gitti.",
            disable_web_page_preview=True,
            reply_to_message_id=message.id,
        )
        LOGGER.info(e)
        return 400
