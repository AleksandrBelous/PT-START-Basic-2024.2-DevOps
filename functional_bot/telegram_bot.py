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

logger = logging.getLogger(__name__)

from dotenv import load_dotenv
from pathlib import Path

from telegram import Update, ForceReply, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler


class DotDict(dict):
    """Позволяет обращаться к элементам словаря через точку."""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class TelegramBot:
    def __init__(self):
        logger.info(f'Start {self.__init__.__name__}')
        dotenv_path = Path('.env')
        load_dotenv(dotenv_path=dotenv_path)

        self.tm_token__ = os.getenv('TM_TOKEN')
        logger.info('Get TM_TOKEN')
        self.chat_id = os.getenv('CHAT_ID')
        logger.info('Get CHAT_ID')

        self.commands = DotDict(
                {
                        'start'           : DotDict(
                                {
                                        'command'    : 'start',
                                        'button'     : '/start',
                                        'state_point': None,
                                        'callback'   : self.command_Start,
                                        }
                                ),
                        'help'            : DotDict(
                                {
                                        'command'    : 'help',
                                        'button'     : '/help',
                                        'state_point': None,
                                        'callback'   : self.command_Help,
                                        }
                                ),
                        'echo'            : DotDict(
                                {
                                        'command'    : 'echo',
                                        'button'     : '/echo',
                                        'state_point': None,
                                        'callback'   : self.command_Echo,
                                        }
                                ),
                        'findPhoneNumbers': DotDict(
                                {
                                        'command'    : 'findPhoneNumbers',
                                        'button'     : '/findPhoneNumbers',
                                        'state_point': 'findPhoneNumbers',
                                        'callback'   : self.command_FindPhoneNumbers,
                                        }
                                ),
                        'cancel'          : DotDict(
                                {
                                        'command'    : 'cancel',
                                        'button'     : '/cancel',
                                        'state_point': None,
                                        'callback'   : self.command_Cancel,
                                        }
                                ),
                        },
                )
        logger.info(f'Stop {self.__init__.__name__}')

    # Функция для создания кнопок
    def keyboard_menu_main(self):
        logger.info(f'Start {self.keyboard_menu_main.__name__}')
        return ReplyKeyboardMarkup([
                [KeyboardButton(self.commands.start.button)],
                [KeyboardButton(self.commands.help.button)],
                [KeyboardButton(self.commands.findPhoneNumbers.button)],
                ], resize_keyboard=True
                )

    def keyboard_menu_cancel(self):
        logger.info(f'Start {self.keyboard_menu_cancel.__name__}')
        return ReplyKeyboardMarkup([
                [KeyboardButton(self.commands.cancel.button)],
                ], resize_keyboard=True
                )

    def command_Start(self, update: Update = None, context=None):
        logger.info(f'Start {self.command_Start.__name__}')
        if update:
            user = update.effective_user
            update.message.reply_text(
                    f'Привет {user.full_name}!',
                    reply_markup=self.keyboard_menu_main()  # Отправляем клавиатуру с кнопками
                    )
        else:
            context.bot.send_message(
                    chat_id=self.chat_id,
                    text="Бот запущен! Вот ваша стартовая кнопка:",
                    reply_markup=self.keyboard_menu_main()
                    )
        logger.info(f'Stop {self.command_Start.__name__}')

    def command_Help(self, update: Update, context):
        logger.info(f'Start {self.command_Help.__name__}')
        update.message.reply_text('Help!', reply_markup=self.keyboard_menu_main())
        logger.info(f'Stop {self.command_Help.__name__}')

    def command_FindPhoneNumbers(self, update: Update, context):
        logger.info(f'Start {self.command_FindPhoneNumbers.__name__}')
        update.message.reply_text('Введите текст для поиска телефонных номеров: ',
                                  # reply_markup=self.main_menu_keyboard()
                                  reply_markup=self.keyboard_menu_cancel()
                                  # Кнопка для отмены поиска
                                  )
        logger.info(f'Stop {self.command_FindPhoneNumbers.__name__}')
        return self.commands.findPhoneNumbers.state_point

    def command_Cancel(self, update: Update, context):
        logger.info(f'Start {self.command_Cancel.__name__}')
        update.message.reply_text('Запрос отменен.', reply_markup=self.keyboard_menu_main())
        logger.info(f'Stop {self.command_Cancel.__name__}')
        return ConversationHandler.END

    def findPhoneNumbers(self, update: Update, context):
        logger.info(f'Start {self.findPhoneNumbers.__name__}')
        user_input = update.message.text  # Получаем текст, содержащий (или нет) номера телефонов

        phoneNumRegex = re.compile(r'8 \(\d{3}\) \d{3}-\d{2}-\d{2}')  # формат 8 (000) 000-00-00

        phoneNumberList = phoneNumRegex.findall(user_input)  # Ищем номера телефонов

        if not phoneNumberList:  # Обрабатываем случай, когда номеров телефонов нет
            update.message.reply_text('Телефонные номера не найдены', reply_markup=self.keyboard_menu_cancel())
            return  # Завершаем выполнение функции

        phoneNumbers = ''  # Создаем строку, в которую будем записывать номера телефонов
        for i in range(len(phoneNumberList)):
            phoneNumbers += f'{i + 1}. {phoneNumberList[i]}\n'  # Записываем очередной номер

        update.message.reply_text(phoneNumbers)  # Отправляем сообщение пользователю
        logger.info(f'Stop {self.findPhoneNumbers.__name__}')
        return ConversationHandler.END  # Завершаем работу обработчика диалога

    def command_Echo(self, update: Update, context):
        logger.info(f'Start {self.command_Echo.__name__}')
        update.message.reply_text(update.message.text, reply_markup=self.keyboard_menu_main())
        logger.info(f'Stop {self.command_Echo.__name__}')

    def main(self):
        logger.info(f'Start {self.main.__name__}')
        updater = Updater(self.tm_token__, use_context=True)

        # Получаем диспетчер для регистрации обработчиков
        dp = updater.dispatcher

        ### Регистрируем обработчики команд ###

        # Обработчик команды /start
        dp.add_handler(CommandHandler(self.commands.start.command, self.commands.start.callback))
        # Обработчик команды /help
        dp.add_handler(CommandHandler(self.commands.help.command, self.commands.help.callback))
        # Обработчик команды /findPhoneNumbers
        dp.add_handler(ConversationHandler(
                entry_points=[CommandHandler(self.commands.findPhoneNumbers.state_point,
                                             self.commands.findPhoneNumbers.callback
                                             )],
                states={
                        self.commands.findPhoneNumbers.state_point: [
                                MessageHandler(Filters.text & ~Filters.command, self.findPhoneNumbers)],
                        },
                fallbacks=[CommandHandler(self.commands.cancel.command, self.commands.cancel.callback)]
                )
                )

        # Регистрируем обработчик текстовых сообщений
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.commands.echo.callback))

        # Запускаем бота
        updater.start_polling()

        # Отправляем кнопку автоматически при запуске бота
        self.command_Start(context=updater)

        # Останавливаем бота при нажатии Ctrl+C
        updater.idle()
        logger.info(f'Stop {self.main.__name__}')


if __name__ == '__main__':
    logger.info('Start Script')
    bot = TelegramBot()
    bot.main()
    logger.info('Stop Script')
