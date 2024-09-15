import requests
import re
import os
import datetime
import logging

logging.disable(logging.CRITICAL)

if logging.getLogger().isEnabledFor(logging.CRITICAL):
    logging.basicConfig(filename=f'log-telegram-bot-{os.path.basename(__file__)}-{datetime.datetime.now()}.txt',
                        level=logging.INFO,
                        format=' %(asctime)s - %(levelname)s - %(message)s'
                        )

from dotenv import load_dotenv
from pathlib import Path

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self):
        dotenv_path = Path('.env')
        load_dotenv(dotenv_path=dotenv_path)

        self.tm_token = os.getenv('TM_TOKEN')

    @staticmethod
    def start(update: Update, context):
        user = update.effective_user
        update.message.reply_text(f'Привет {user.full_name}!')

    @staticmethod
    def helpCommand(update: Update, context):
        update.message.reply_text('Help!')

    @staticmethod
    def findPhoneNumbersCommand(update: Update, context):
        update.message.reply_text('Введите текст для поиска телефонных номеров: ')

        return 'findPhoneNumbers'

    @staticmethod
    def findPhoneNumbers(update: Update, context):
        user_input = update.message.text  # Получаем текст, содержащий (или нет) номера телефонов

        phoneNumRegex = re.compile(r'8 \(\d{3}\) \d{3}-\d{2}-\d{2}')  # формат 8 (000) 000-00-00

        phoneNumberList = phoneNumRegex.findall(user_input)  # Ищем номера телефонов

        if not phoneNumberList:  # Обрабатываем случай, когда номеров телефонов нет
            update.message.reply_text('Телефонные номера не найдены')
            return  # Завершаем выполнение функции

        phoneNumbers = ''  # Создаем строку, в которую будем записывать номера телефонов
        for i in range(len(phoneNumberList)):
            phoneNumbers += f'{i + 1}. {phoneNumberList[i]}\n'  # Записываем очередной номер

        update.message.reply_text(phoneNumbers)  # Отправляем сообщение пользователю
        return ConversationHandler.END  # Завершаем работу обработчика диалога

    @staticmethod
    def echo(update: Update, context):
        update.message.reply_text(update.message.text)

    def main(self):
        updater = Updater(self.tm_token, use_context=True)

        # Получаем диспетчер для регистрации обработчиков
        dp = updater.dispatcher
        # Обработчик диалога
        convHandlerFindPhoneNumbers = ConversationHandler(
                entry_points=[CommandHandler('findPhoneNumbers', self.findPhoneNumbersCommand)],
                states={
                        'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, self.findPhoneNumbers)],
                        },
                fallbacks=[]
                )

        # Регистрируем обработчики команд
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("help", self.helpCommand))
        dp.add_handler(convHandlerFindPhoneNumbers)

        # Регистрируем обработчик текстовых сообщений
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.echo))

        # Запускаем бота
        updater.start_polling()

        # Останавливаем бота при нажатии Ctrl+C
        updater.idle()


if __name__ == '__main__':
    bot = TelegramBot()
    bot.main()
