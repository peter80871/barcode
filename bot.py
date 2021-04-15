import telebot
import key
import connect
from telebot import types
from pyzbar.pyzbar import decode
from PIL import Image


bot = telebot.TeleBot(key.tg)


user = connect.Users()
product = connect.Products()

cities = list(set([i[3] for i in product.show_shops_address()]))

# main markup
markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=1)
balance_button = types.InlineKeyboardButton(text='Баланс', callback_data='баланс')
quantity_button = types.InlineKeyboardButton(text='Наличие Товара', callback_data='наличие товара')
city_button = types.InlineKeyboardButton(text='Изменить город', callback_data='изменить город')
markup.add(balance_button, quantity_button, city_button)

# come back to main menu
menu = types.ReplyKeyboardMarkup(resize_keyboard=1)
menu_button = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='меню')
menu.add(menu_button)

# change city
# city_markup = types.ReplyKeyboardMarkup(resize_keyboard=1)
# city_button = types.InlineKeyboardButton(text='Изменить город', callback_data='изменить город')
# city_markup.add(city_button)

# show city markup
markets_markup = types.InlineKeyboardMarkup()
markets_button = types.InlineKeyboardButton(text='Показать магазины', callback_data='показать магазины')
markets_markup.add(markets_button)

cities_markup = types.InlineKeyboardMarkup()
for _city in cities:
    new_city = types.InlineKeyboardButton(text=f'{_city}', callback_data=f'{_city}')
    cities_markup.add(new_city)


def balance(card):
    return user.show_balance(card)


def show_shops(user_id):
    try:
        barcode = user.show_user_search(user_id)[0][0]    # last user search
        user_city = user.show_users_city(user_id)
        print(barcode, user_city)
        text = ''
        for i in product.show_products():
            if i[0] == barcode:
                markets = product.show_products_in_shops(i[0], user_city[0][0])
                for market in markets:
                    title = market[0].split(':')
                    url = market[1]
                    # add market in message
                    new_line = f'<a href="{url}">{title[0]}</a> {title[1]}\n'
                    text += new_line

        user.new_user_position(user_id, 'main')
        # send markets
        bot.send_message(user_id, text, parse_mode='html', disable_web_page_preview=True)
        # show main markup
        bot.send_message(user_id, 'Выберите действие', reply_markup=markup)
    except:
        print('err')


@bot.message_handler(commands=['start'])
def start_message(message):
    print('start', message.chat.id)
    users = user.show_users_id()
    users = [i[0] for i in users]
    if message.chat.id not in users:
        # added new user in db
        user.add_new_user(message.chat.id, message.from_user.first_name, 'None', 0)
    user.new_user_position(message.chat.id, 'main')
    bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)


@bot.message_handler(content_types=['photo'])
def photo(message):
    _city = user.show_users_city(message.chat.id)
    print(_city[0][0])
    if _city[0][0] == 'None':
        bot.send_message(message.chat.id, 'Выберите действие', reply_markup=cities_markup)
        user.new_user_position(message.chat.id, 'new_city')
    else:
        try:
            print(1)
            raw = message.photo[2].file_id
            name = raw + ".png"
            file_info = bot.get_file(raw)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(name, 'wb') as new_file:
                new_file.write(downloaded_file)
            img = open(name, 'rb')
            print(Image.open(img))
            _barcode = str(decode(Image.open(img))[0][0]).split("'")[1]
            bot.send_message(message.chat.id, _barcode, reply_markup=markup)
        except:
            bot.send_message(message.chat.id, 'Штрих код не распознан', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if call.data == 'показать магазины':
        show_shops(call.message.chat.id)

    print(user.show_user_position(call.message.chat.id)[0][0], call.data, call.message.chat.id)
    if user.show_user_position(call.message.chat.id)[0][0] == 'new_city' and call.data in cities:
        user.add_user_city(call.message.chat.id, call.message.from_user.first_name, call.data)  # update row city in 'users'
        user.new_user_position(call.message.chat.id, 'main')     # update row position in 'user_position'
        bot.send_message(call.message.chat.id, 'Город изменен')


@bot.message_handler(content_types=['text'])
def send_text(message):
    # CHECK PRODUCTS
    if user.show_user_position(message.chat.id)[0][0] == 'pre_check_products':
        try:
            barcode = int(user.show_user_search(message.chat.id)[0][0])  # last user search
            user_city = user.show_users_city(message.chat.id)
            print('pre_check', barcode, user_city[0][0])
            quantity_shops = 0
            average_coast = 0
            user.new_user_search(message.chat.id, int(message.text))
            for _product in product.show_products():
                if str(_product[0]) == message.text:
                    for t in product.show_products():
                        if _product[0] == barcode:
                            markets = product.show_products_in_shops(int(_product[0]), user_city[0][0])
                            for market in markets:
                                title = market[0].split(':')
                                quantity_shops += 1
                                average_coast += float(title[1])
                    try:
                        msg = f'{_product[1]}\nСредняя цена: {average_coast / quantity_shops}\nЕсть в {quantity_shops} магазинах\n{_product[2]}'
                        bot.send_message(message.chat.id, msg, reply_markup=markets_markup)
                    except:
                        bot.send_message(message.chat.id, 'Такого товара нет в БД', reply_markup=markup)
                else:
                    bot.send_message(message.chat.id, 'Такого товара нет в БД', reply_markup=markup)
                    user.new_user_position(message.chat.id, 'main')
        except:
            if message.text.lower() == 'изменить город':
                pass
            else:
                # bot.send_message(message.chat.id, 'Нет такого товара', reply_markup=markup)
                user.new_user_position(message.chat.id, 'main')

    if message.text.lower() == 'наличие товара':
        _city = user.show_users_city(message.chat.id)
        print(_city[0][0])
        if _city[0][0] == 'None':
            bot.send_message(message.chat.id, 'Выберите действие', reply_markup=cities_markup)
            user.new_user_position(message.chat.id, 'new_city')
        else:
            bot.send_message(message.chat.id, 'Введите штрих код или отправьте фото')
            user.new_user_position(message.chat.id, 'pre_check_products')
    # END CHECK PRODUCTS

    if message.text.lower() == 'сканировать штрихкод':
        user.new_user_position(message.chat.id, 'scan')
    # BALANCE
    # show balance for card with input id
    if user.show_user_position(message.chat.id)[0][0] == 'balance':
        try:
            bot.send_message(message.chat.id, user.show_balance(message.text))
            user.new_user_position(message.chat.id, 'main')
            bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)
        except:
            if message.text.lower() == 'вернуться в меню' or message.text.lower() == 'баланс':
                bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)
            else:
                bot.send_message(message.chat.id, 'Неверный номер карты', reply_markup=menu)

    # check balance
    if message.text.lower() == 'баланс' and user.show_user_position(message.chat.id)[0][0] == 'main':
        bot.send_message(message.chat.id, 'Укажите номер карты')
        user.new_user_position(message.chat.id, 'balance')    # update row position in 'user_position'

    # END BALANCE

    # return to main menu
    if message.text.lower() == 'вернуться в меню':
        user.new_user_position(message.chat.id, 'main')
        bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)

    # change city
    if message.text.lower() == 'изменить город':
        bot.send_message(message.chat.id, 'Укажите город', reply_markup=cities_markup)
        user.new_user_position(message.chat.id, 'new_city')


bot.polling(none_stop=True)
