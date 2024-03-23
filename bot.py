import telebot
from telebot import types
bot = telebot.TeleBot('7053104867:AAHljQ_DzyJPMt6xdpoMbQlHQYeoeMLCXaU')


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Начать 👋")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "👋 Привет! Я твой бот-помошник!", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '👋 Начать 👋':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('🥣 Все рецепты 🥣')
        btn2 = types.KeyboardButton('✎ Создать рецепт ✎')
        btn3 = types.KeyboardButton('🏠 Домой 🏠')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, '❓ Задайте интересующий вас вопрос ❓', reply_markup=markup)
    elif message.text == '🥣 Все рецепты 🥣':
        bot.send_message(message.from_user.id, 'Все рецепты вы можете увидеть' + '[ здесь 🠔](http://127.0.0.1:8000)', parse_mode='Markdown')
    elif message.text == '✎ Создать рецепт ✎':
        bot.send_message(message.from_user.id, 'Создать рецепт вы можете' + '[ здесь 🠔](http://127.0.0.1:8000/recipe/create/)', parse_mode='Markdown')
    elif message.text == '🏠 Домой 🏠':
        bot.send_message(message.from_user.id, '[🏠 Домашняя страница🏠 ](http://127.0.0.1:8000)', parse_mode='Markdown')


bot.polling(none_stop=True, interval=0)
