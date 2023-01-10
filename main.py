import openai
import telebot
import time
from settings import OPENAI_API_KEY, TELEGRAM_API_KEY

openai.api_key = OPENAI_API_KEY

bot = telebot.TeleBot(TELEGRAM_API_KEY)

last_message_time = {}


@bot.message_handler(commands=['start', 'restart'])
def start(prompt):
    message = f'Привет, я готов ответить на твои запросы, {prompt.from_user.first_name}'
    bot.send_message(prompt.chat.id, message)


def check_time_limit(user_id):
    # Получаем текущее время
    current_time = time.time()
    # Проверяем, есть ли пользователь в словаре
    if user_id in last_message_time:
        # Получаем время последнего сообщения
        last_message = last_message_time[user_id]
        # Проверяем, прошло ли больше минуты с момента последнего сообщения
        if current_time - last_message > 30:
            # Обновляем время последнего сообщения
            last_message_time[user_id] = current_time
            return True
        else:
            return False
    else:
        # Добавляем пользователя в словарь
        last_message_time[user_id] = current_time
        return True


@bot.message_handler()
def handle_message(prompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        temperature=0.5,
        prompt=prompt.text,
        max_tokens=1000,
        top_p=1.0,
        frequency_penalty=0.5,
        presence_penalty=0.0
    ) if check_time_limit(prompt.chat.id) else False

    message = response.choices[0].text if response else 'Интервал между запросами не должен быть менее 30 секунд. Повторите позже!'
    bot.send_message(chat_id=prompt.chat.id, text=message)


bot.infinity_polling()
