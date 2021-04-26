import mysql.connector


class Users:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Pe8t9i!a",
            database="test"
        )
        self.cursor = self.conn.cursor()
        print('connect')

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

    def show_user_search(self, user_id):
        self.cursor.execute(f"select last_search from users where user_id = {user_id}")

        return self.cursor.fetchall()

    def show_balance(self, card):
        self.cursor.execute(f"select balance from users_card where card = {card}")

        return self.cursor.fetchall()

    def new_user_position(self, user_id, position):
        self.cursor.execute(f"update user_position set position = '{position}' where user_id = {user_id}")

        self.conn.commit()

    # function for bot
    def add_new_user(self, user_id, user_name, city, last_search):
        self.cursor.execute('insert into users (user_id, user_name, city, last_search) values (%s, %s, %s, %s)',
                            (user_id, user_name, city, last_search))
        self.cursor.execute("insert into user_position (user_id, position) values (%s, %s)",
                            (user_id, 'main'))
        self.conn.commit()

    def add_user_city(self, user_id, city):
        self.cursor.execute(f"update users set city = '{city}' where user_id = {user_id}")

        self.conn.commit()

    def new_user_search(self, user_id, search):
        self.cursor.execute(f"update users set last_search = '{search}' where user_id = {user_id}")

        self.conn.commit()


class Products:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Pe8t9i!a",
            database="test"
        )
        self.cursor = self.conn.cursor()
        print('connect')

    def custom_command(self, command):
        self.cursor.execute(command)

        return self.cursor.fetchall()

    def show_shops_address(self):
        self.cursor.execute("select address from trm_in_store;")

        c = self.cursor.fetchall()
        _cs = []
        for i in c:
            try:
                _cs.append(i[0].split('г. ')[1].split(',')[0])
            except:
                pass
        cs = []
        for i in _cs:
            if len(i.split('ул.')) < 2:
                cs.append(i)

        return cs

''' def __init__(self):
        self.conn = mysql.connector.connect(
            host="5.23.50.131",
            user="redesupar_botogr",
            password="1N5FrpJn",
            database="redesupar_botogr"
        )
        self.cursor = self.conn.cursor()
        print('connect')'''