import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler

# Константы для состояний
WAITING_FOR_PACKAGE_NAME = 1


# Команда для получения списка всех установленных пакетов
def get_apt_list():
    try:
        result = subprocess.run(['apt', 'list', '--installed'], stdout=subprocess.PIPE)
        return result.stdout.decode('utf-8')
    except Exception as e:
        return f"Ошибка при выполнении команды: {str(e)}"


# Команда для получения информации о конкретном пакете
def get_package_info(package_name):
    try:
        result = subprocess.run(['apt', 'show', package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return result.stdout.decode('utf-8')
        else:
            return f"Пакет '{package_name}' не найден."
    except Exception as e:
        return f"Ошибка при выполнении команды: {str(e)}"


# Обработка команды /get_apt_list
def start_command(update: Update, context):
    keyboard = [
            [InlineKeyboardButton("Все пакеты", callback_data='all_packages')],
            [InlineKeyboardButton("Поиск пакета", callback_data='search_package')]
            ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите опцию:', reply_markup=reply_markup)
    return ConversationHandler.END


# Обработка нажатия кнопок
def button_handler(update: Update, context):
    query = update.callback_query
    query.answer()

    if query.data == 'all_packages':
        apt_list = get_apt_list()
        query.edit_message_text(text=f"Установленные пакеты:\n{apt_list[:4096]}")  # Ограничение на длину сообщения
    elif query.data == 'search_package':
        query.edit_message_text(text="Введите название пакета:")
        return WAITING_FOR_PACKAGE_NAME


# Обработка ввода названия пакета
def handle_message(update: Update, context):
    if context.user_data.get('state') == WAITING_FOR_PACKAGE_NAME:
        package_name = update.message.text
        package_info = get_package_info(package_name)
        update.message.reply_text(package_info[:4096])  # Ограничение на длину сообщения
        context.user_data['state'] = None
        return ConversationHandler.END
    else:
        update.message.reply_text("Используйте команду /get_apt_list для выбора действия.")
        return ConversationHandler.END


# Основная функция для запуска бота
def main():
    # Замените 'YOUR_API_KEY' на токен вашего Telegram бота
    updater = Updater("YOUR_API_KEY", use_context=True)
    dp = updater.dispatcher

    # Создание ConversationHandler
    conv_handler = ConversationHandler(
            entry_points=[CommandHandler('get_apt_list', start_command)],
            states={
                    WAITING_FOR_PACKAGE_NAME: [MessageHandler(Filters.text & ~Filters.command, handle_message)]
                    },
            fallbacks=[]
            )

    # Добавляем обработчики
    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(button_handler))

    # Запуск бота
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
