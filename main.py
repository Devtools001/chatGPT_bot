import openai
import telebot
from settings import OPENAI_API_KEY, TELEGRAM_API_KEY

openai.api_key = OPENAI_API_KEY

bot = telebot.TeleBot(TELEGRAM_API_KEY)


@bot.message_handler(commands=['start', 'restart'])
def start(prompt):
    message = f'Привет, я готов ответить на твои запросы, брат {prompt.from_user.first_name}'
    bot.send_message(prompt.chat.id, message)
    print(prompt)


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
    )
    bot.send_message(chat_id=prompt.chat.id, text=response.choices[0].text)


bot.polling()
