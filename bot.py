import telebot
import key
import connect
from telebot import types


bot = telebot.TeleBot(key.tg)


connection = connect.NewConnection()

# main markup
markup = types.InlineKeyboardMarkup()
balance_button = types.InlineKeyboardButton(text='Баланс', callback_data='баланс')
quantity_button = types.InlineKeyboardButton(text='Наличие Товара', callback_data='наличие товара')
markup.add(balance_button, quantity_button)

# come back to main menu
menu = types.InlineKeyboardMarkup()
menu_button = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='меню')
menu.add(menu_button)

# change city
city_markup = types.InlineKeyboardMarkup()
city_button = types.InlineKeyboardButton(text='Изменить город', callback_data='изменить город')
city_markup.add(city_button)

# show city markup
markets_markup = types.InlineKeyboardMarkup()
markets_button = types.InlineKeyboardButton(text='Показать магазины', callback_data='показать магазины')
markets_markup.add(markets_button)


def new_user(id, first_name, _city, last_search):
    connection.add_new_user(id, first_name, _city, last_search)
    print('new user')


def balance(card):
    return connection.show_balance(card)


def show_shops(user_id):
    barcode = connection.show_user_search(user_id)[0][0]    # last user search
    user_city = connection.show_users_city(user_id)
    print(barcode, user_city)
    text = ''
    for i in connection.show_products():
        if i[0] == barcode:
            markets = connection.show_products_in_shops(i[0], user_city[0][0])
            for market in markets:
                title = market[0].split(':')
                url = market[1]
                # add market in message
                new_line = f'<a href="{url}">{title[0]}</a> {title[1]}\n'
                text += new_line

    connection.new_user_position(user_id, 'menu')
    # send markets
    bot.send_message(user_id, text, parse_mode='html', disable_web_page_preview=True)
    # show main markup
    bot.send_message(user_id, 'Выберите действие', reply_markup=markup)


@bot.message_handler(commands=['start'])
def start_message(message):
    print(message.chat.id)
    users = connection.show_users_id()
    users = [i[0] for i in users]
    if message.chat.id not in users:
        # added new user in db
        connection.add_new_user(message.chat.id, message.from_user.first_name, 'None', 0)

    bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    # bot.answer_callback_query(callback_query_id=call.id, text='Баланс')
    if call.data == 'баланс':
        bot.send_message(call.message.chat.id, 'Укажите номер карты')
        connection.new_user_position(call.message.chat.id, 'balance')

    if call.data == 'наличие товара':
        # connection.new_user_position(call.message.chat.id, 'pre_check')
        _city = connection.show_users_city(call.message.chat.id)
        print(_city)
        if _city[0][0] == 'None':
            bot.send_message(call.message.chat.id, 'Укажите город')
            connection.new_user_position(call.message.chat.id, 'new_city')
        else:
            connection.new_user_position(call.message.chat.id, 'check_products')
            bot.send_message(call.message.chat.id, 'Укажите штрих-код', reply_markup=city_markup)

    # return to main menu
    if call.data == 'меню':
        connection.new_user_position(call.message.chat.id, 'menu')
        bot.send_message(call.message.chat.id, 'Выберите действие', reply_markup=markup)

    # change city
    if call.data == 'изменить город':
        bot.send_message(call.message.chat.id, 'Укажите город')
        connection.new_user_position(call.message.chat.id, 'new_city')

    if call.data == 'показать магазины':
        show_shops(call.message.chat.id)


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'меню':
        connection.new_user_position(message.chat.id, 'main')

    if connection.show_user_position(message.chat.id)[0][0] == 'check_products':
        connection.new_user_search(message.chat.id, int(message.text))
        users = connection.show_users()
        for i in connection.show_products():
            if str(i[0]) == message.text:
                msg = f'{i[1]}\n\n{i[2]}'   # title product and description
                bot.send_message(message.chat.id, msg, reply_markup=markets_markup)
            else:
                bot.send_message(message.chat.id, 'Такого товара нет в БД')
    
    # show balance for card with input id
    if connection.show_user_position(message.chat.id)[0][0] == 'balance':
        try:
            bot.send_message(message.chat.id, connection.show_balance(message.text))
            connection.new_user_position(message.chat.id, 'main')
            bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)
        except:
            bot.send_message(message.chat.id, 'Неверный номер карты', reply_markup=menu)

    # check balance
    if message.text.lower() == 'баланс' and connection.show_user_position(message.chat.id)[0][0] == 'main':
        bot.send_message(message.chat.id, 'Укажите номер карты')
        connection.new_user_position(message.chat.id, 'balance')    # update row position in 'user_position'

    # change city
    if connection.show_user_position(message.chat.id)[0][0] == 'new_city':
        connection.add_user_city(message.chat.id, message.from_user.first_name, message.text)   # update row city in 'users'
        connection.new_user_position(message.chat.id, 'check_products')     # update row position in 'user_position'
        bot.send_message(message.chat.id, 'Укажите штрих-код', reply_markup=city_markup)

    # check products
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
