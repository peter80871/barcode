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

    def show_tables(self):
        return self.cursor.execute('SHOW TABLES')

    def create(self):
        self.cursor.execute('create table users (user_id int, user_name varchar(30), city varchar(30));')


conn = NewConnection()
conn.create()