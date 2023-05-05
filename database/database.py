from datetime import datetime
import yaml
from mysql.connector import connect, Error
from mysql.connector.abstracts import MySQLConnectionAbstract
from typing import Optional
from yoyo import read_migrations
from yoyo import get_backend


class Database:
    config = None
    connection: Optional[MySQLConnectionAbstract] = None

    @staticmethod
    def _validate_connection():
        if not Database.connection.is_connected():
            Database.connect()
    

    @staticmethod
    def form_answer(id_chat, rating, answer_comment=None):
        Database._validate_connection()
        cursor = Database.connection.cursor()
        insert = (
            """
            INSERT INTO `answer` (`id_chat`, `answer_time`, `rating`, `answer_comment`)
            VALUES (%s, %s, %s, %s)
            """
        )

        cursor.execute(insert, (id_chat, datetime.now(), rating, answer_comment))
        
        Database.connection.commit()

        cursor.close()


    @staticmethod
    def insert_if_not_exist(id_chat: int) -> bool:
        """Insert new user into database if not exsit.
        Returns `False` if user it
        otherwise return `True`"""
        Database._validate_connection()

        with Database.connection.cursor() as cursor:
            cursor.execute(f"SELECT status FROM chat WHERE id_chat = {id_chat}")
            rows = cursor.fetchone()

            if rows == None:
                cursor.execute(f"INSERT INTO chat (id_chat, status) VALUES ({id_chat}, 'active')")
                Database.connection.commit() #!
                return False

            elif len(rows) == 1:
                cursor.execute(f"UPDATE chat SET status='active' WHERE id_chat={id_chat}")
            
            Database.connection.commit()

        return True

    def add_notification(id_chat, time):
        Database._validate_connection()

        with Database.connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM notification WHERE id_chat={id_chat} AND time='{time}'")
            rows = cursor.fetchone()

            if rows and rows[0] == 0:
                cursor.execute(f"INSERT INTO notification VALUES ({id_chat}, '{time}')")

        Database.connection.commit()
        return True



    @staticmethod
    def new_chat(id_chat, gender, age, status='active'):
        cursor = Database.connection.cursor()
        select = (
            """
            SELECT * FROM `chat`
            WHERE `id_chat` = %s;
            """
        )

        cursor.execute(select, (id_chat, ))

        rows = cursor.fetchone()

        cursor.close()

        if rows == None:
            cursor = Database.connection.cursor()
            insert = (
                """
                INSERT INTO `chat` (`id_chat`, `gender`, `age`, `status`)
                VALUES (%s, %s, %s, %s);
                """
            )

            cursor.execute(insert, (id_chat, gender, age, status))

            Database.connection.commit()

            cursor.close()
        elif rows[1] == 'inactive':
            cursor = Database.connection.cursor()
            update = (
                """
                UPDATE `chat``
                SET `status`='active'
                WHERE %s
                """
            )

            cursor.execute(update, (id_chat, ))

            Database.connection.commit()

            cursor.close()
    

    @staticmethod
    def connect():
        try:
            Database.connection =  connect(
                host=str(Database.config["host"]),
                user=str(Database.config["user"]),
                password=str(Database.config["password"]),
                database=str(Database.config["dbname"])
            )
        except Error as e:
            print(e)

    
    @staticmethod 
    def parse_config():
        with open("./database/cfg.yaml", "r") as stream:
            try:
                Database.config = yaml.safe_load(stream)["database"]
            except yaml.YAMLError as exc:
                print(exc)


    @staticmethod
    def migrate():
        backend = get_backend(f'mysql://{Database.config["user"]}:{Database.config["password"]}@{Database.config["host"]}/{Database.config["dbname"]}')
        migrations = read_migrations('./database/migrations')

        with backend.lock():
            # Apply any outstanding migrations
            backend.apply_migrations(backend.to_apply(migrations))

