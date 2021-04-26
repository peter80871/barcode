import time
import random
import telebot
import key
import connect
from telebot import types
from pyzbar.pyzbar import decode
from PIL import Image


bot = telebot.TeleBot(key.tg)

user = connect.Users()
product = connect.Products()

cities = list(set(product.show_shops_address()))

# main markup
markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=1)
balance_button = types.InlineKeyboardButton(text='Баланс', callback_data='баланс')

quantity_button = types.InlineKeyboardButton(text='Наличие Товара', callback_data='наличие товара')
city_button = types.InlineKeyboardButton(text='Изменить город', callback_data='изменить город')

positive_button = types.InlineKeyboardButton(text='Предложения', callback_data='изменить город')
negative_button = types.InlineKeyboardButton(text='Жалоба', callback_data='изменить город')

markup.add(balance_button, quantity_button, positive_button, negative_button, city_button)

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
    if _city != 'Тында' and _city != 'Якутск у. Октябрьская 23':
        new_city = types.InlineKeyboardButton(text=f'{_city}', callback_data=f'{_city}')
        cities_markup.add(new_city)


def balance(card):
    return user.show_balance(card)


def show_shops(user_id):
    try:
        city = user.show_users_city(user_id)[0][0]
        shop_id = show_product(user_id, user.show_user_search(user_id)[0][0], 0)
        shops = ''
        try_connect = 1
        while 0 < try_connect < 3:
            try:
                print(try_connect)
                for shop in shop_id:
                    s = product.custom_command(f'select address from trm_in_store where nomenclature_id = {shop[0]};')[0][0]

                    c = s.split('г. ')[1].split(',')[0]

                    if len(c.split('ул.')) < 2:
                        if city == c:
                            shops += f'{s}\n'
                if len(shops) < 1:
                    shops = 'Нет в наличии в вашем городе'

                bot.send_message(user_id, shops, reply_markup=markup)
                try_connect = 5
            except:
                try_connect += 1
    except:
        print('err')


def show_product(user_id, msg_text, pos):
    try:
        user.new_user_search(user_id, int(msg_text))
        barcode = int(user.show_user_search(user_id)[0][0])  # last user search
        user_city = user.show_users_city(user_id)
        print('pre_check', barcode, user_city[0][0])

        try_connect = 1
        while 0 < try_connect < 4:
            try:
                print('try', try_connect)
                product_id = product.custom_command(f"select item from trm_in_var where id = '{barcode}'")
                shop_id = product.custom_command(f"select nomenclature_id from trm_in_var where id = '{barcode}'")
                price = product.custom_command(f"select price from trm_in_pricelist_items where item = '{product_id[0][0]}'")
                print(product_id)
                print(price[0][0], shop_id)
                product_title = product.custom_command(f"select name from trm_in_items where id = '{product_id[0][0]}'")

                msg = f'{product_title[0][0]}\nСредняя цена: {int(price[0][0])}\nЕсть в {len(shop_id)} магазине(ax)'
                user.new_user_position(user_id, 'main')

                if pos == 1:
                    bot.send_message(user_id, msg, reply_markup=markets_markup)

                try_connect = 5

                return shop_id

            except:
                try_connect += 1

        if try_connect != 5:
            user.new_user_position(user_id, 'main')
            bot.send_message(user_id, 'Такого товара нет', reply_markup=markup)

    except:
        pass


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

            show_product(message.chat.id, _barcode, 1)

        except:
            bot.send_message(message.chat.id, 'Штрих код не распознан', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if call.data == '134':

        bot.send_message(call.message.chat.id, 'Введите обращение')
        user.new_user_position(call.message.chat.id, 'after_negative')

    if call.data == 'показать магазины':
        show_shops(call.message.chat.id)

    # print(user.show_user_position(call.message.chat.id)[0][0], call.data, call.message.chat.id)

    if user.show_user_position(call.message.chat.id)[0][0] == 'new_city' and call.data in cities:
        user.add_user_city(call.message.chat.id, call.data)  # update row city in 'users'
        user.new_user_position(call.message.chat.id, 'main')     # update row position in 'user_position'
        bot.send_message(call.message.chat.id, 'Город изменен')


@bot.message_handler(content_types=['text'])
def send_text(message):
    if user.show_user_position(message.chat.id)[0][0] == 'positive':
        if message.text.lower() != 'введите обращение' and message.text.lower() != 'предложения' and message.text.lower() != 'жалоба' and message.text.lower() != 'наличие товара' and message.text.lower() != 'баланс' and message.text.lower() != 'изменить город':
            bot.send_message(message.chat.id, f'Спасибо за обращение {random.randint(100000,999999)}', reply_markup=markup)

    if user.show_user_position(message.chat.id)[0][0] == 'after_negative':
        if message.text.lower() != 'введите обращение' and message.text.lower() != 'предложения' and message.text.lower() != 'жалоба' and message.text.lower() != 'наличие товара' and message.text.lower() != 'баланс' and message.text.lower() != 'изменить город':
            msg = f'Благодарим вас оставленную жалобу, ваша жалоба № {random.randint(100000,999999)}, мы Вас уведомим о нашем решении тут'
            bot.send_message(message.chat.id, msg ,reply_markup=markup)

    if message.text.lower() == 'предложения':
        bot.send_message(message.chat.id, 'Введите обращение')
        user.new_user_position(message.chat.id, 'positive')

    if message.text.lower() == 'жалоба':
        user.new_user_position(message.chat.id, 'negative')
        _city = user.show_users_city(message.chat.id)[0][0]
        s = product.custom_command(f'select address from trm_in_store;')
        shops = []
        for c in s:
            try:
                t = c[0].split('г. ')[1].split(',')[0]

                if len(t.split('ул.')) < 2:
                    if _city == t and c[0] != 'г. Нерюнгри, Ленина 4' and c[0] != 'г. Нерюнгри, ул. Карла Маркса, д. 23':
                        shops.append(c[0])
            except:
                pass

        n_cities_markup = types.InlineKeyboardMarkup()
        for _city in list(set(shops)):
                new_city = types.InlineKeyboardButton(text=f'{_city}', callback_data='134')
                n_cities_markup.add(new_city)

        bot.send_message(message.chat.id, 'Выберите магазин', reply_markup=n_cities_markup)

    # CHECK PRODUCTS
    if user.show_user_position(message.chat.id)[0][0] == 'pre_check_products':
        show_product(message.chat.id, message.text, 1)

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

    # BALANCE
    if user.show_user_position(message.chat.id)[0][0] == 'balance':
        try:
            bot.send_message(message.chat.id, user.show_balance(message.text), reply_markup=markup)
            user.new_user_position(message.chat.id, 'main')
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
