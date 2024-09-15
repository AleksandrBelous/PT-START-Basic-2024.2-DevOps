import requests
import re
import os
import datetime
import logging

logging.disable(logging.CRITICAL)

if logging.getLogger().isEnabledFor(logging.CRITICAL):
    logging.basicConfig(filename=f'log-t-bot-{os.path.basename(__file__)}-{datetime.datetime.now()}.txt',
                        level=logging.DEBUG,
                        format=' %(asctime)s - %(levelname)s - %(message)s'
                        )

from dotenv import load_dotenv
from pathlib import Path

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


def send_message(text):
    dotenv_path = Path('.env')
    load_dotenv(dotenv_path=dotenv_path)

    # host = os.getenv('HOST')
    # port = os.getenv('PORT')
    # username = os.getenv('USER')
    # password = os.getenv('PASSWORD')
    tm_token = os.getenv('TM_TOKEN')
    chat_id = os.getenv('CHAT_ID')

    url = f"https://api.telegram.org/bot{tm_token}/sendMessage"
    payload = {
            "chat_id": chat_id,
            "text"   : text
            }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Сообщение успешно отправлено!")
    else:
        print("Ошибка при отправке сообщения:", response.text)


message_text = "Привет, мир! Это сообщение отправлено через Telegram Bot API."

send_message(message_text)
