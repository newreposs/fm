import logging
from database.database import db
from pyrogram import Client
from pyrogram.types import Message
from config import Config
from translation import Translation

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('log.txt'), logging.StreamHandler()],
                    level=logging.INFO)
LOGGER = logging.getLogger(__name__)


async def add_user_to_database(client, message):
    ben = await client.get_me()
    BOT_USERNAME = ben.username
    user = message.from_user
    dc_id = user.dc_id or "[DC'si Yok]"
    username = user.username or "Yok"
    if not await db.is_user_exist(user.id):
        if Config.LOG_CHANNEL:
            await client.send_message(Config.LOG_CHANNEL,
                                 Translation.LOG_TEXT_P.format(user.id,
                                                               user.mention,
                                                               user.language_code,
                                                               username,
                                                               dc_id,
                                                               BOT_USERNAME
                                                               ))
        else:
            LOGGER.info(f"#YeniKullanıcı :- Ad : {user.first_name} ID : {user.id}")
        await db.add_user(user.id)
