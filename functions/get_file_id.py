import time
import math
import os
import asyncio
import re
from config import Config 
from typing import List
from pyrogram.types import InlineKeyboardButton
from pyrogram.types import Message

def get_file_id(msg: Message):
    if msg.media:
        for message_type in ("photo", "animation", "audio", "document", "video", "video_note", "voice", "sticker"):
            if obj = getattr(msg, message_type):
                setattr(obj, "message_type", message_type)
                return obj
