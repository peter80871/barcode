import mysql.connector


class NewConnection():
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Pe8t9i1a",
            database="test"
        )

        self.cursor = self.conn.cursor()

    # return bot users id, name, city
    def show_users(self):
        users = []
        self.cursor.execute("select * from users;")
        for user in self.cursor.fetchall():
            users.append(user)

        return users

    def show_users_id(self):
        self.cursor.execute("select user_id from users;")

        return self.cursor.fetchall()

    def show_users_city(self, user_id):
        self.cursor.execute(f"select city from users where user_id = {user_id};")

        return self.cursor.fetchall()

    def show_user_position(self, user_id):
        self.cursor.execute(f"select position from user_position where user_id = {user_id}")

        return self.cursor.fetchall()

    def new_user_position(self, user_id, position):
        self.cursor.execute(f"update user_position set position = '{position}' where user_id = {user_id}")

        self.conn.commit()

    def new_url(self, url, id):
        self.cursor.execute(f"update shops set urls = '{url}' where id = {id}")

        self.conn.commit()

    def show_balance(self, card):
        self.cursor.execute(f"select balance from users_card where card = {card}")

        return self.cursor.fetchall()

    # return products barcode, title, description
    def show_products(self):
        self.cursor.execute("select * from products;")

        return self.cursor.fetchall()

    # return products id market, barcode, coast, quantity
    def show_products_in_shops(self, barcode, city):
        self.cursor.execute(f"select * from shops where city = '{city}'")

        markets = self.cursor.fetchall()
        shops_and_coast = []

        for market in markets:
            self.cursor.execute(f"select * from products_in_shops where product_barcode = {barcode} and id_shop = {market[0]}")

            # add shop street and coast
            if self.cursor is not None:
                css = self.cursor.fetchall()
                for cs in css:
                    shops_and_coast.append((f'{market[2]} - {cs[2]}р', market[4]))

        return shops_and_coast

    def show_url_shop(self, id):
        self.cursor.execute(f"select urls from shops where id = {id}")

        markets = self.cursor.fetchall()

    # function for bot
    def add_new_user(self, user_id, user_name, city):
        self.cursor.execute('insert into users (user_id, user_name, city) values (%s, %s, %s)',
                            (user_id, user_name, city))
        self.cursor.execute("insert into user_position (user_id, position) values (%s, %s)",
                            (user_id, 'main'))
        self.conn.commit()

    def add_user_city(self, user_id, user_name, city):
        self.cursor.execute(f"update users set city = '{city}' where user_id = {user_id}")

        self.conn.commit()

    # append product
    def add_new_product(self, barcode, title, description):
        self.cursor.execute('insert into products (barcode, title, description) values (%s, %s, %s)',
                            (barcode, title, description))

        self.conn.commit()

    def add_card(self, card):
        self.cursor.execute('insert into users_card (card, balance) values (%s, %s)',
                            (card, 500))

        self.conn.commit()

    # append photo for product with barcode
    def add_photo_product(self, barcode, photo):
        self.cursor.execute('insert into products_photo (barcode, product_image) values (%s, %s)',
                            (barcode, photo))

        self.conn.commit()

    # new shop
    def add_shop(self, id, name, address, city):
        self.cursor.execute('insert into shops (id, name, address, city) values (%s, %s, %s, %s)',
                            (id, name, address, city))

        self.conn.commit()

    # add product in shop
    def add_product_in_shop(self, id_shop, barcode, coast, quantity):
        self.cursor.execute('insert into products_in_shops (id_shop, product_barcode, coast, quantity) values (%s, %s, %s, %s)',
                            (id_shop, barcode, coast, quantity))

        self.conn.commit()

    def create_tables(self):
        pass
        # self.cursor.execute('create table users (user_id int, user_name varchar(30), city varchar(30))')
        # self.cursor.execute('create table users_card (card bigint, balance int)')

        # self.cursor.execute('create table products (barcode bigint, title varchar(100), description text)')
        # self.cursor.execute('create table products_photo (barcode bigint, product_image blob)')

        # self.cursor.execute('create table shops (id int, name varchar(40), address varchar(70), city varchar(20))')
        # self.cursor.execute('create table products_in_shops (id_shop int, product_barcode bigint, coast float, quantity int)')
        # self.cursor.execute('create table user_position (user_id int, position varchar(20))')


# a = NewConnection().new_url('https://yandex.ru/maps/org/okean/48819044748/?ll=124.709884%2C56.662294&z=17.58', 0)
# print(a.new_user_position())
# a.add_new_product(4605246001970, 'Принцесса Нури Чор.Високогир 25пак', 'Принцесса Нури\nМягкий гармоничный вкус и приятный свежий аромат – вот что ждут ценители от цейлонского чая. Идеальное воплощение этих ожиданий – чай «Принцесса Нури».')
# a.add_photo_product(4605246001970, )
# a.add_shop(2, 'Название магазина', 'Ленина 2', 'Алдан')

