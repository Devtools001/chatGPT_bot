import os
import openai
import telebot
import pathlib
import requests
import time
import torch
from settings import OPENAI_API_KEY, TELEGRAM_API_KEY
from convert import audioconvert
from stt import speech2text

WORKDIR = str(pathlib.Path(__file__).parent.absolute())
openai.api_key = OPENAI_API_KEY
bot = telebot.TeleBot(TELEGRAM_API_KEY)
TEMODEL = "/home/cb/v2_4lang_q.pt"
tmodel = torch.package.PackageImporter(TEMODEL).load_pickle("te_model", "model")

last_message_time = {}


def ai_response(prompt, chat_id):
    response = openai.Completion.create(
        model="text-davinci-003",
        temperature=0.5,
        prompt=prompt,
        max_tokens=1000,
        top_p=1.0,
        frequency_penalty=0.5,
        presence_penalty=0.0
    ) if check_time_interval(chat_id) else False

    return response


@bot.message_handler(commands=['start', 'restart'])
def start(prompt):
    message = f'Привет, я готов ответить на твои запросы, {prompt.from_user.first_name}'
    bot.send_message(prompt.chat.id, message)


def check_time_interval(user_id):
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
    message = ai_response(prompt.text).choices[0].text if ai_response else 'Интервал между запросами не должен быть менее 30 секунд. Повторите позже!'
    bot.reply_to(prompt, text=message)


@bot.message_handler(content_types=["voice", "video_note"])
def voice_decoder(prompt):
    if prompt.voice:
        file = prompt.voice
        file = prompt.voice
    elif prompt.video_note:
        file = prompt.video_note
    else:
        return False

    finfo = bot.get_file(file.file_id)
    try:
        contents = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TELEGRAM_API_KEY, finfo.file_path))
    except Exception:
        return False

    downpath = WORKDIR + "/" + file.file_unique_id
    with open(downpath, 'wb') as dest:
        dest.write(contents.content)

    path = audioconvert(downpath)
    if not path:
        return False

    text = speech2text(path)
    os.remove(path)
    if not text or text == "" or text == " ":
        return False
    else:
        text = tmodel.enhance_text(text, 'ru')

    response = ai_response(text, prompt.chat.id).choices[0].text if ai_response else 'Интервал между запросами не должен быть менее 30 секунд. Повторите позже!'
    bot.reply_to(prompt, text=response)


if __name__ == '__main__':
    bot.infinity_polling()
