import subprocess

import re
import os
import datetime
import logging

# logging.disable(logging.CRITICAL)

if logging.getLogger().isEnabledFor(logging.CRITICAL):
    logging.basicConfig(filename=f'log-telegram-bot-{os.path.basename(__file__)}-{datetime.datetime.now()}.txt',
                        level=logging.INFO,
                        format=' %(asctime)s - %(levelname)s - %(message)s'
                        )

logger = logging.getLogger(__name__)

import paramiko
from dotenv import load_dotenv
from pathlib import Path

from telegram import Update, ForceReply, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram.error import BadRequest


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
                        'cancel'          : DotDict(
                                {
                                        'command'    : 'cancel',
                                        'button'     : '/cancel',
                                        'state_point': None,
                                        'callback'   : self.command_Cancel,
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

                        ### 1. Поиск информации в тексте и её вывод.
                        'findEmails'      : DotDict(
                                {
                                        'command'    : 'find_email',
                                        'button'     : '/find_email',
                                        'state_point': 'find_email',
                                        'callback'   : self.command_FindEmails,
                                        }
                                ),
                        'findPhoneNumbers': DotDict(
                                {
                                        'command'    : 'find_phone_number',
                                        'button'     : '/find_phone_number',
                                        'state_point': 'find_phone_number',
                                        'callback'   : self.command_FindPhoneNumbers,
                                        }
                                ),

                        ### 2. Проверка сложности пароля регулярным выражением.
                        'verifyPassword'  : DotDict(
                                {
                                        'command'    : 'verify_password',
                                        'button'     : '/verify_password',
                                        'state_point': 'verify_password',
                                        'callback'   : self.command_VerifyPassword,
                                        }
                                ),
                        ### 3. Мониторинг Linux-системы.

                        ## 3.1. Сбор информации о системе.

                        # 3.1.1. О релизе.
                        'getRelease'      : DotDict(
                                {
                                        'command'    : 'get_release',
                                        'button'     : '/get_release',
                                        'state_point': 'get_release',
                                        'callback'   : self.command_GetRelease,
                                        }
                                ),

                        # 3.1.2. Об архитектуры процессора, имени хоста системы и версии ядра.
                        'getUname'        : DotDict(
                                {
                                        'command'    : 'get_uname',
                                        'button'     : '/get_uname',
                                        'state_point': 'get_uname',
                                        'callback'   : self.command_GetUname,
                                        }
                                ),

                        # 3.1.3. О времени работы.
                        'getUptime'       : DotDict(
                                {
                                        'command'    : 'get_uptime',
                                        'button'     : '/get_uptime',
                                        'state_point': 'get_uptime',
                                        'callback'   : self.command_GetUptime,
                                        }
                                ),

                        ## 3.2. Сбор информации о состоянии файловой системы.
                        'getDF'           : DotDict(
                                {
                                        'command'    : 'get_df',
                                        'button'     : '/get_df',
                                        'state_point': 'get_df',
                                        'callback'   : self.command_GetDF,
                                        }
                                ),

                        ## 3.3. Сбор информации о состоянии оперативной памяти.
                        'getFree'         : DotDict(
                                {
                                        'command'    : 'get_free',
                                        'button'     : '/get_free',
                                        'state_point': 'get_free',
                                        'callback'   : self.command_GetFree,
                                        }
                                ),

                        ## 3.4. Сбор информации о производительности системы.
                        'getMpstat'       : DotDict(
                                {
                                        'command'    : 'get_mpstat',
                                        'button'     : '/get_mpstat',
                                        'state_point': 'get_mpstat',
                                        'callback'   : self.command_GetMpstat,
                                        }
                                ),

                        ## 3.5. Сбор информации о работающих в данной системе пользователях.
                        'getW'            : DotDict(
                                {
                                        'command'    : 'get_w',
                                        'button'     : '/get_w',
                                        'state_point': 'get_w',
                                        'callback'   : self.command_GetW,
                                        }
                                ),

                        ## 3.6. Сбор логов.

                        # 3.6.1. Последние 10 входов в систему.
                        'getAuths'        : DotDict(
                                {
                                        'command'    : 'get_auths',
                                        'button'     : '/get_auths',
                                        'state_point': 'get_auths',
                                        'callback'   : self.command_GetAuths,
                                        }
                                ),
                        # 3.6.2. Последние 5 критических событий.
                        'getCritical'     : DotDict(
                                {
                                        'command'    : 'get_critical',
                                        'button'     : '/get_critical',
                                        'state_point': 'get_critical',
                                        'callback'   : self.command_GetCritical,
                                        }
                                ),

                        ## 3.7 Сбор информации о запущенных процессах.
                        'getPS'           : DotDict(
                                {
                                        'command'    : 'get_ps',
                                        'button'     : '/get_ps',
                                        'state_point': 'get_ps',
                                        'callback'   : self.command_GetPS,
                                        }
                                ),

                        ## 3.8 Сбор информации об используемых портах.
                        'getSS'           : DotDict(
                                {
                                        'command'    : 'get_ss',
                                        'button'     : '/get_ss',
                                        'state_point': 'get_ss',
                                        'callback'   : self.command_GetSS,
                                        }
                                ),

                        ## 3.9 Сбор информации об установленных пакетах.
                        'getAptList'      : DotDict(
                                {
                                        'command'    : 'get_apt_list',
                                        'button'     : '/get_apt_list',
                                        'state_point': 'get_apt_list',
                                        'callback'   : self.command_GetAptList,
                                        }
                                ),
                        ## 3.10 Сбор информации о запущенных сервисах.
                        'getServices'     : DotDict(
                                {
                                        'command'    : 'get_services',
                                        'button'     : '/get_services',
                                        'state_point': 'get_services',
                                        'callback'   : self.command_GetServices,
                                        },
                                ),
                        }
                )

        logger.info(f'Stop {self.__init__.__name__}')

    # Функция для создания кнопок основных запросов
    def keyboard_menu_main(self):
        logger.info(f'Start {self.keyboard_menu_main.__name__}')

        return ReplyKeyboardMarkup([
                [KeyboardButton(self.commands.start.button)],
                [KeyboardButton(self.commands.help.button)],
                [KeyboardButton(self.commands.findEmails.button)],
                [KeyboardButton(self.commands.findPhoneNumbers.button)],
                [KeyboardButton(self.commands.verifyPassword.button)],
                [KeyboardButton(self.commands.getRelease.button)],
                [KeyboardButton(self.commands.getUname.button)],
                [KeyboardButton(self.commands.getUptime.button)],
                [KeyboardButton(self.commands.getDF.button)],
                [KeyboardButton(self.commands.getFree.button)],
                [KeyboardButton(self.commands.getMpstat.button)],
                [KeyboardButton(self.commands.getW.button)],
                [KeyboardButton(self.commands.getAuths.button)],
                [KeyboardButton(self.commands.getCritical.button)],
                [KeyboardButton(self.commands.getPS.button)],
                [KeyboardButton(self.commands.getSS.button)],
                [KeyboardButton(self.commands.getAptList.button)],
                [KeyboardButton(self.commands.getServices.button)],
                ], resize_keyboard=True
                )

    # Функция для создания кнопки отмены запроса
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
                    text="Бот запущен!",
                    reply_markup=self.keyboard_menu_main()
                    )
        logger.info(f'Stop {self.command_Start.__name__}')

    def command_Cancel(self, update: Update, context):
        logger.info(f'Start {self.command_Cancel.__name__}')
        update.message.reply_text('Запрос отменен.', reply_markup=self.keyboard_menu_main())
        logger.info(f'Stop {self.command_Cancel.__name__}')
        return ConversationHandler.END

    def command_Help(self, update: Update, context):
        logger.info(f'Start {self.command_Help.__name__}')

        text = (
                "В боте должен быть реализован функционал поиска необходимой информации и вывод ее пользователю. Поиск должен быть реализован с помощью регулярных выражений. "
                "Информация, которую бот должен уметь выделять из текста:"
                "а) Email-адреса."
                "Команда: /find_email"
                "б) Номера телефонов."
                "Команда: /find_phone_number"
                "❗ Стоит учесть различные варианты записи номеров телефона. 8XXXXXXXXXX, 8(XXX)XXXXXXX, 8 XXX XXX XX XX, 8 (XXX) XXX XX XX, 8-XXX-XXX-XX-XX. Также вместо ‘8’ на первом месте может быть ‘+7’."
                "Взаимодействия с этими командами происходит по следующему принципу:"
                "Пользователь выбирает команду"
                "Бот запрашивает текст"
                "Пользователь отправляет текст"
                "Бот вывод список найденных номеров телефона или email-адресов."
                "❗ Важно! Если номера телефонов или email-адреса найдены не были, необходимо сообщить об этом пользователю."
                "2. Проверка сложности пароля регулярным выражением."
                "В боте должен быть реализован функционал проверки сложности пароль с использованием регулярного выражения."
                "Команда: /verify_password"
                "Требования к паролю:"
                "Пароль должен содержать не менее восьми символов."
                "Пароль должен включать как минимум одну заглавную букву (A–Z)."
                "Пароль должен включать хотя бы одну строчную букву (a–z)."
                "Пароль должен включать хотя бы одну цифру (0–9)."
                "Пароль должен включать хотя бы один специальный символ, такой как !@#$%^&*()."
                "Взаимодействие с этой командой происходит по следующему принципу:"
                "Пользователь выбирает команду"
                "Бот запрашивает пароль"
                "Пользователь отправляет пароль"
                "Бот отвечает: ‘Пароль простой’ или ‘Пароль сложный’."
                "3. Мониторинг Linux-системы"
                "Бот должен реализовывать функционал для мониторинга Linux системы. Для этого будет устанавливаться SSH-подключение к удаленному серверу (в его роли может выступать собственная виртуальная машина, эта машина не должна участвовать в развертывании проекта), с помощью которого будет собираться метрики с системы. Мониторинг должен включать в себя следующий показатели:"
                "3.1 Сбор информации о системе:"
                "3.1.1 О релизе."
                "Команда: /get_release"
                "3.1.2 Об архитектуры процессора, имени хоста системы и версии ядра."
                "Команда: /get_uname"
                "3.1.3 О времени работы."
                "Команда: /get_uptime"
                "3.2 Сбор информации о состоянии файловой системы."
                "Команда: /get_df"
                "3.3 Сбор информации о состоянии оперативной памяти."
                "Команда: /get_free"
                "3.4 Сбор информации о производительности системы."
                "Команда: /get_mpstat"
                "3.5 Сбор информации о работающих в данной системе пользователях."
                "Команда: /get_w"
                "3.6 Сбор логов"
                "3.6.1 Последние 10 входов в систему."
                "Команда: /get_auths"
                "3.6.2 Последние 5 критических события."
                "Команда: /get_critical"
                "3.7 Сбор информации о запущенных процессах."
                "Команда: /get_ps"
                "3.8 Сбор информации об используемых портах."
                "Команда: /get_ss"
                "3.9 Сбор информации об установленных пакетах."
                "Команда: /get_apt_list"
                "❗ Стоит учесть два варианта взаимодействия с этой командой:"
                "Вывод всех пакетов;"
                "Поиск информации о пакете, название которого будет запрошено у пользователя. "
                "3.10 Сбор информации о запущенных сервисах."
                "Команда: /get_services"
                "Взаимодействия с этими командами происходит по следующему принципу:"
                "Пользователь выбирает команду"
                "Бот отправляет соответствующую информацию")

        update.message.reply_text(text, reply_markup=self.keyboard_menu_main())
        logger.info(f'Stop {self.command_Help.__name__}')

    def command_FindEmails(self, update: Update, context):
        """
        Бот вывод список найденных email-адресов
        """
        logger.info(f'Start {self.command_FindEmails.__name__}')
        update.message.reply_text('Введите текст для поиска email-адресов: ',
                                  reply_markup=self.keyboard_menu_cancel()
                                  # Кнопка для отмены поиска
                                  )
        logger.info(f'Stop {self.command_FindEmails.__name__}')
        return self.commands.findEmails.state_point

    def findEmails(self, update: Update, context):
        logger.info(f'Start {self.findEmails.__name__}')
        user_input = update.message.text  # Получаем текст, содержащий (или нет) email-адреса

        emailsRegex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,3}')  # формат email-адресов

        emailsList = emailsRegex.findall(user_input)  # Ищем номера телефонов

        if not emailsList:  # Обрабатываем случай, когда номеров телефонов нет
            update.message.reply_text('Email-адреса не найдены', reply_markup=self.keyboard_menu_cancel())
            return  # Завершаем выполнение функции

        emails = '\n'.join([f'{i + 1}. {emailsList[i]}' for i in range(len(emailsList))])

        update.message.reply_text(emails, reply_markup=self.keyboard_menu_cancel())  # Отправляем сообщение пользователю

        logger.info(f'Stop {self.findEmails.__name__}')
        return  # ConversationHandler.END  # Завершаем работу обработчика диалога

    def command_FindPhoneNumbers(self, update: Update, context):
        """
        Бот вывод список найденных номеров телефона
        """
        logger.info(f'Start {self.command_FindPhoneNumbers.__name__}')
        update.message.reply_text('Введите текст для поиска телефонных номеров: ',
                                  reply_markup=self.keyboard_menu_cancel()
                                  # Кнопка для отмены поиска
                                  )
        logger.info(f'Stop {self.command_FindPhoneNumbers.__name__}')
        return self.commands.findPhoneNumbers.state_point

    def findPhoneNumbers(self, update: Update, context):
        logger.info(f'Start {self.findPhoneNumbers.__name__}')
        user_input = update.message.text  # Получаем текст, содержащий (или нет) номера телефонов
        """
        Различные варианты записи номеров телефона.
        - 8XXXXXXXXXX,
        - 8(XXX)XXXXXXX,
        - 8 XXX XXX XX XX,
        - 8 (XXX) XXX XX XX,
        - 8-XXX-XXX-XX-XX.
        Также вместо ‘8’ на первом месте может быть ‘+7’.
        """
        phoneNumRegex = re.compile(r'(\+7|8)(\s?[(-]?\d{3}[)-]?\s?\d{3}-?\s?\d{2}-?\s?\d{2})')  # формат

        phoneNumberList = phoneNumRegex.findall(user_input)  # Ищем номера телефонов

        if not phoneNumberList:  # Обрабатываем случай, когда номеров телефонов нет
            update.message.reply_text('Телефонные номера не найдены', reply_markup=self.keyboard_menu_cancel())
            return  # Завершаем выполнение функции

        phoneNumbers = '\n'.join(
                [f'{i + 1}. {phoneNumberList[i][0] + phoneNumberList[i][1]}' for i in range(len(phoneNumberList))]
                )

        update.message.reply_text(phoneNumbers, reply_markup=self.keyboard_menu_cancel()
                                  )  # Отправляем сообщение пользователю

        logger.info(f'Stop {self.findPhoneNumbers.__name__}')
        return  # ConversationHandler.END  # Завершаем работу обработчика диалога

    def command_VerifyPassword(self, update: Update, context):
        """
        Бот выводит информацию о сложности пароля
        """
        logger.info(f'Start {self.command_VerifyPassword.__name__}')
        update.message.reply_text('Введите пароль для оценки сложности: ',
                                  reply_markup=self.keyboard_menu_cancel()
                                  # Кнопка для отмены поиска
                                  )
        logger.info(f'Stop {self.command_VerifyPassword.__name__}')
        return self.commands.verifyPassword.state_point

    def verifyPassword(self, update: Update, context):
        logger.info(f'Start {self.verifyPassword.__name__}')
        user_input = update.message.text  # Получаем текст, содержащий (или нет) номера телефонов

        """
        Требования к паролю:
        - Пароль должен содержать не менее восьми символов.
        - Пароль должен включать как минимум одну заглавную букву (A–Z).
        - Пароль должен включать хотя бы одну строчную букву (a–z).
        - Пароль должен включать хотя бы одну цифру (0–9).
        - Пароль должен включать хотя бы один специальный символ, такой как !@#$%^&*().
        """

        passwdRegex = re.compile(r'(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}')

        passwdList = passwdRegex.search(user_input)

        if not passwdList:  # Обрабатываем случай, когда совпадений нет
            update.message.reply_text('Пароль простой', reply_markup=self.keyboard_menu_cancel())
            return  # Завершаем выполнение функции

        update.message.reply_text('Пароль сложный', reply_markup=self.keyboard_menu_cancel()
                                  )  # Отправляем сообщение пользователю
        logger.info(f'Stop {self.verifyPassword.__name__}')
        return  # ConversationHandler.END  # Завершаем работу обработчика диалога

    def getHostInfo(self, command="uname -a"):
        logger.info(f"Start {self.getHostInfo.__name__}")

        host = os.getenv('HOST')
        logger.info('Get HOST')

        port = os.getenv('PORT')
        logger.info('Get PORT')

        username = os.getenv('USER')
        logger.info('Get USER')

        password = os.getenv('PASSWORD')
        logger.info('Get PASSWORD')

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password, port=int(port))

        stdin, stdout, stderr = client.exec_command(command)
        data = stdout.read() + stderr.read()
        client.close()
        data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

        logger.info(f"Stop {self.getHostInfo.__name__}")
        return data

    def general_TG_Output(self, update: Update, context, host_command=None, output_text=None):
        logger.info(f'Start {self.general_TG_Output.__name__} && {host_command} && {output_text[:100]}')
        data = self.getHostInfo(host_command) if host_command else output_text
        try:
            update.message.reply_text(data, reply_markup=self.keyboard_menu_main())
        except BadRequest as e:
            max_length = 4096
            parts = [data[i:i + max_length] for i in range(0, len(data), max_length)]
            for part in parts[:-1:]:
                update.message.reply_text(part)
            update.message.reply_text(parts[-1], reply_markup=self.keyboard_menu_main())
        logger.info(f'Stop {self.general_TG_Output.__name__} && {host_command} && {output_text[:100]}')

    def command_GetRelease(self, update: Update, context):
        logger.info(f'Start {self.command_GetRelease.__name__}')
        self.general_TG_Output(update, context, "lsb_release -a")
        logger.info(f'Stop {self.command_GetRelease.__name__}')

    def command_GetUname(self, update: Update, context):
        logger.info(f'Start {self.command_GetUname.__name__}')
        self.general_TG_Output(update, context, "uname -nmr")
        logger.info(f'Stop {self.command_GetUname.__name__}')

    def command_GetUptime(self, update: Update, context):
        logger.info(f'Start {self.command_GetUptime.__name__}')
        self.general_TG_Output(update, context, "uptime")
        logger.info(f'Stop {self.command_GetUptime.__name__}')

    def command_GetDF(self, update: Update, context):
        logger.info(f'Start {self.command_GetDF.__name__}')
        self.general_TG_Output(update, context, "df -h")
        logger.info(f'Stop {self.command_GetDF.__name__}')

    def command_GetFree(self, update: Update, context):
        logger.info(f'Start {self.command_GetFree.__name__}')
        self.general_TG_Output(update, context, "free -h")
        logger.info(f'Stop {self.command_GetFree.__name__}')

    def command_GetMpstat(self, update: Update, context):
        logger.info(f'Start {self.command_GetMpstat.__name__}')
        self.general_TG_Output(update, context, "mpstat -P ALL 1 1")
        logger.info(f'Stop {self.command_GetMpstat.__name__}')

    def command_GetW(self, update: Update, context):
        logger.info(f'Start {self.command_GetW.__name__}')
        self.general_TG_Output(update, context, "w")
        logger.info(f'Stop {self.command_GetW.__name__}')

    def command_GetAuths(self, update: Update, context):
        logger.info(f'Start {self.command_GetAuths.__name__}')
        self.general_TG_Output(update, context, "last -n 10")
        logger.info(f'Stop {self.command_GetAuths.__name__}')

    def command_GetCritical(self, update: Update, context):
        logger.info(f'Start {self.command_GetCritical.__name__}')
        text = self.getHostInfo("journalctl -p crit -n 5 | grep -E '^[A-Za-z]{3} [0-9]{2}'")
        # print([text])
        text = re.sub(r'nautilus', r'sevsu', text)
        # print([text])
        self.general_TG_Output(update, context, None, text)
        logger.info(f'Stop {self.command_GetCritical.__name__}')

    def command_GetPS(self, update: Update, context):
        logger.info(f'Start {self.command_GetPS.__name__}')
        self.general_TG_Output(update, context, "ps aux")
        logger.info(f'Stop {self.command_GetPS.__name__}')

    def command_GetSS(self, update: Update, context):
        logger.info(f'Start {self.command_GetSS.__name__}')
        self.general_TG_Output(update, context, "ss -tuln")
        logger.info(f'Stop {self.command_GetSS.__name__}')

    def command_GetAptList(self, update: Update, context):
        logger.info(f'Start {self.command_GetAptList.__name__}')

        reply_markup = InlineKeyboardMarkup(
                [
                        [InlineKeyboardButton("Все пакеты", callback_data='all_packages')],
                        [InlineKeyboardButton("Поиск пакета", callback_data='search_package')]
                        ]
                )
        update.message.reply_text('Выберите опцию:', reply_markup=reply_markup)

        logger.info(f'Stop {self.command_GetAptList.__name__}')
        return ConversationHandler.END

    # Команда для получения списка всех установленных пакетов
    def get_apt_list(self):
        logger.info(f'Start {self.get_apt_list.__name__}')
        text = self.getHostInfo("dpkg -l | cat")
        # print(text)
        text = re.compile(r'ii\s\s([a-z:.0-9-]+)\s').findall(text)
        # print(text)
        logger.info(f'Stop {self.get_apt_list.__name__}')
        return ', '.join(text)

    # Обработка нажатия кнопок
    def button_handler(self, update: Update, context):
        logger.info(f'Start {self.button_handler.__name__}')
        query = update.callback_query
        query.answer()

        if query.data == 'all_packages':
            self.general_TG_Output(update, context, None, self.get_apt_list())
            logger.info(f'Stop {self.button_handler.__name__} from IF')
        elif query.data == 'search_package':
            query.edit_message_text(text="Введите название пакета:")
            logger.info(f'Stop {self.button_handler.__name__} from ELSE')
            return self.commands.getAptList.state_point

    # Обработка ввода названия пакета
    def handle_message(self, update: Update, context):
        logger.info(f'Start {self.handle_message.__name__}')
        if context.user_data.get('state') == self.commands.getAptList.state_point:
            package_name = update.message.text
            self.general_TG_Output(update, context, f"dpkg -s {package_name}")
            # package_info = self.get_package_info(package_name)
            # update.message.reply_text(package_info[:2000])  # Ограничение на длину сообщения
            context.user_data['state'] = None
            logger.info(f'Stop {self.handle_message.__name__} from IF')
            return ConversationHandler.END
        else:
            update.message.reply_text(f"{update.message.text}. Используйте команду /start для выбора действия.")
            logger.info(f'Stop {self.handle_message.__name__} from ELSE')
            return ConversationHandler.END

    def command_GetServices(self, update: Update, context):
        logger.info(f'Start {self.command_GetServices.__name__}')
        self.general_TG_Output(update, context, "systemctl list-units --type=service --state=running")
        logger.info(f'Stop {self.command_GetServices.__name__}')

    def command_Echo(self, update: Update, context):
        logger.info(f'Start {self.command_Echo.__name__}')
        update.message.reply_text(update.message.text, reply_markup=self.keyboard_menu_main())
        logger.info(f'Stop {self.command_Echo.__name__}')

    def main(self):
        logger.info(f'Start {self.main.__name__}')

        updater = Updater(self.tm_token__, use_context=True)

        # Получаем диспетчер для регистрации обработчиков
        dp = updater.dispatcher

        ## Регистрируем обработчики команд

        # Обработчик команды /start
        dp.add_handler(CommandHandler(self.commands.start.command, self.commands.start.callback))

        # Обработчик команды /help
        dp.add_handler(CommandHandler(self.commands.help.command, self.commands.help.callback))

        # Обработчик команды /findEmails
        dp.add_handler(ConversationHandler(
                entry_points=[CommandHandler(self.commands.findEmails.state_point,
                                             self.commands.findEmails.callback
                                             )],
                states={
                        self.commands.findEmails.state_point: [
                                MessageHandler(Filters.text & ~Filters.command, self.findEmails)],
                        },
                fallbacks=[CommandHandler(self.commands.cancel.command, self.commands.cancel.callback)]
                )
                )

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

        # Обработчик команды /verifyPassword
        dp.add_handler(ConversationHandler(
                entry_points=[CommandHandler(self.commands.verifyPassword.state_point,
                                             self.commands.verifyPassword.callback
                                             )],
                states={
                        self.commands.verifyPassword.state_point: [
                                MessageHandler(Filters.text & ~Filters.command, self.verifyPassword)],
                        },
                fallbacks=[CommandHandler(self.commands.cancel.command, self.commands.cancel.callback)]
                )
                )

        # Обработчик команды /get_release
        dp.add_handler(CommandHandler(self.commands.getRelease.command, self.commands.getRelease.callback))

        # Обработчик команды /get_uname
        dp.add_handler(CommandHandler(self.commands.getUname.command, self.commands.getUname.callback))

        # Обработчик команды /get_uptime
        dp.add_handler(CommandHandler(self.commands.getUptime.command, self.commands.getUptime.callback))

        # Обработчик команды /get_df
        dp.add_handler(CommandHandler(self.commands.getDF.command, self.commands.getDF.callback))

        # Обработчик команды /get_free
        dp.add_handler(CommandHandler(self.commands.getFree.command, self.commands.getFree.callback))

        # Обработчик команды /get_mpstat
        dp.add_handler(CommandHandler(self.commands.getMpstat.command, self.commands.getMpstat.callback))

        # Обработчик команды /get_w
        dp.add_handler(CommandHandler(self.commands.getW.command, self.commands.getW.callback))

        # Обработчик команды /get_auths
        dp.add_handler(CommandHandler(self.commands.getAuths.command, self.commands.getAuths.callback))

        # Обработчик команды /get_critical
        dp.add_handler(CommandHandler(self.commands.getCritical.command, self.commands.getCritical.callback))

        # Обработчик команды /get_ps
        dp.add_handler(CommandHandler(self.commands.getPS.command, self.commands.getPS.callback))

        # Обработчик команды /get_SS
        dp.add_handler(CommandHandler(self.commands.getSS.command, self.commands.getSS.callback))

        # Обработчик команды /get_apt_list
        # dp.add_handler(CommandHandler(self.commands.getAptList.command, self.commands.getAptList.callback))

        dp.add_handler(ConversationHandler(
                entry_points=[CommandHandler(self.commands.getAptList.command,
                                             self.commands.getAptList.callback
                                             )],
                states={
                        self.commands.getAptList.state_point: [
                                MessageHandler(Filters.text & ~Filters.command, self.handle_message)]
                        },
                fallbacks=[CommandHandler(self.commands.cancel.command, self.commands.cancel.callback)]
                )
                )

        # Обработка нажатия кнопок
        dp.add_handler(CallbackQueryHandler(self.button_handler))

        # Обработка сообщения с названием пакета или для ЭХО-сообщений
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_message))

        # Обработчик команды /get_services
        dp.add_handler(CommandHandler(self.commands.getServices.command, self.commands.getServices.callback))

        # Обработчик текстовых сообщений /echo
        # dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.commands.echo.callback))

        # Запускаем бота
        updater.start_polling()

        # Отправляем кнопку /start автоматически при запуске бота
        self.command_Start(context=updater)

        # Останавливаем бота при нажатии Ctrl+C
        updater.idle()

        logger.info(f'Stop {self.main.__name__}')


if __name__ == '__main__':
    logger.info('Start Script')
    bot = TelegramBot()
    bot.main()
    logger.info('Stop Script')
