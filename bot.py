import telebot
import key
import connect
from telebot import types


bot = telebot.TeleBot(key.tg)


connection = connect.NewConnection()

markup = types.InlineKeyboardMarkup()
balance_button = types.InlineKeyboardButton(text='Баланс', callback_data='баланс')
quantity_button = types.InlineKeyboardButton(text='Наличие Товара', callback_data='наличие товара')
markup.add(balance_button, quantity_button)

menu = types.InlineKeyboardMarkup()
menu_button = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='меню')
menu.add(menu_button)


def new_user(id, first_name, city):
    connection.add_new_user(id, first_name, city)
    print('new user')


def balance(card):
    return connection.show_balance(card)


@bot.message_handler(commands=['start'])
def start_message(message):
    print(message.chat.id)
    users = connection.show_users_id()
    users = [i[0] for i in users]
    if message.chat.id not in users:

        new_user(message.chat.id, message.from_user.first_name, 'None')

    bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    # bot.answer_callback_query(callback_query_id=call.id, text='Баланс')
    if call.data == 'баланс':
        bot.send_message(call.message.chat.id, 'Укажите номер карты')
        connection.new_user_position(call.message.chat.id, 'balance')

    if call.data == 'наличие товара':
        # connection.new_user_position(call.message.chat.id, 'pre_check')
        city = connection.show_users_city(call.message.chat.id)
        if  city == 'None':
            bot.send_message(call.message.chat.id, 'Укажите город')
            connection.new_user_position(call.message.chat.id, 'new_city')
        else:
            connection.new_user_position(call.message.chat.id, 'check_products')
            bot.send_message(call.message.chat.id, 'Укажите штрих-код')

    if call.data == 'меню':
        connection.new_user_position(call.message.chat.id, 'menu')
        bot.send_message(call.message.chat.id, 'Выберите действие', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'меню':
        connection.new_user_position(message.chat.id, 'main')

    if connection.show_user_position(message.chat.id)[0][0] == 'check_products':

        users = connection.show_users()
        for i in connection.show_products():
            if str(i[0]) == message.text:
                msg = f'{i[1]}\n\n{i[2]}'
                user_city = [i[2] for i in users if i[0] == message.chat.id]
                markets = connection.show_products_in_shops(i[0], user_city[0])
                bot.send_message(message.chat.id, msg)
                for market in markets:
                    print(market[0])
                    print(market[1])
                    text = f"[{market[0].split(' - ')[0]}]({market[1]})"
                    bot.send_message(message.chat.id, text, parse_mode='MarkdownV2')
                    # bot.send_message(message.chat.id, market)
            else:
                bot.send_message(message.chat.id, 'Такого товара нет в БД')

        bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)

        connection.new_user_position(message.chat.id, 'main')

    if connection.show_user_position(message.chat.id)[0][0] == 'balance':
        try:
            bot.send_message(message.chat.id, connection.show_balance(message.text))

            connection.new_user_position(message.chat.id, 'main')

            bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)
        except:
            bot.send_message(message.chat.id, 'Неверный номер карты', reply_markup=menu)

    if message.text.lower() == 'баланс' and connection.show_user_position(message.chat.id)[0][0] == 'main':
        bot.send_message(message.chat.id, 'Укажите номер карты')
        connection.new_user_position(message.chat.id, 'balance')

    if connection.show_user_position(message.chat.id)[0][0] == 'new_city':
        connection.add_user_city(message.chat.id, message.from_user.first_name, message.text)
        connection.new_user_position(message.chat.id, 'check_products')
        bot.send_message(message.chat.id, 'Укажите штрих-код')

    if message.text == 'наличие товара':
        # connection.new_user_position(call.message.chat.id, 'pre_check')
        city = connection.show_users_city(message.chat.id)
        if city == 'None':
            bot.send_message(message.chat.id, 'Укажите город')
            connection.new_user_position(message.chat.id, 'new_city')
        else:
            connection.new_user_position(message.chat.id, 'check_products')
            bot.send_message(message.chat.id, 'Укажите штрих-код')



bot.polling(none_stop=True)
