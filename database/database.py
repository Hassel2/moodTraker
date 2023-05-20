from datetime import datetime
from typing import Optional
from itertools import count
import logging

import yaml
from mysql.connector import connect, Error
from mysql.connector.abstracts import MySQLConnectionAbstract
from yoyo import read_migrations
from yoyo import get_backend


class Database:
    config = None
    connection: Optional[MySQLConnectionAbstract] = None
    _ids = count(0)

    def __init__(self):
        self.id = next(self._ids)
        if self.id > 1:
            logging.warning("There are more than one Database class instances")
        self.connect()
        

    def _validate_connection(self):
        if not self.connection.is_connected():
            self.connect()


    def form_answer(self, id_chat, rating, answer_comment=None):
        self._validate_connection()
        cursor = self.connection.cursor()
        insert = (
            """
            INSERT INTO `answer` (`id_chat`, `answer_time`, `rating`, `answer_comment`)
            VALUES (%s, %s, %s, %s)
            """
        )

        cursor.execute(insert, (id_chat, datetime.now(), rating, answer_comment))
        
        self.connection.commit()

        cursor.close()


    def insert_if_not_exist(self, id_chat: int) -> bool:
        """Insert new user into database if not exsit.
        Returns `False` if user it
        otherwise return `True`"""
        self._validate_connection()

        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT status FROM chat WHERE id_chat = {id_chat}")
            rows = cursor.fetchone()

            if rows == None:
                cursor.execute(f"INSERT INTO chat (id_chat, status) VALUES ({id_chat}, 'active')")
                self.connection.commit() #!
                return False

            elif len(rows) == 1:
                cursor.execute(f"UPDATE chat SET status='active' WHERE id_chat={id_chat}")
            
            self.connection.commit()

        return True

    def add_notification(self, id_chat, hours, minutes):
        self._validate_connection()

        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM notification \
                           WHERE id_chat={id_chat} AND time='{hours}:{minutes}'")
            rows = cursor.fetchone()

            if rows and rows[0] == 0:
                cursor.execute(f"INSERT INTO notification \
                               VALUES ({id_chat}, '{hours}:{minutes}')")
            else:
                return False

        self.connection.commit()
        return True


    def connect(self):
        try:
            self.connection =  connect(
                host=str(self.config["host"]),
                user=str(self.config["user"]),
                password=str(self.config["password"]),
                database=str(self.config["dbname"])
            )
        except Error as e:
            print(e)

    @staticmethod
    def parse_config(config_path: str):
        with open(config_path, 'r') as stream:
            try:
                Database.config = yaml.safe_load(stream)["database"]
            except yaml.YAMLError as exc:
                print(exc)


    @staticmethod
    def migrate(migrations_path: str):
        backend = get_backend('mysql://{}:{}@{}/{}'.format(
            Database.config["user"],
            Database.config["password"],
            Database.config["host"],
            Database.config["dbname"]
        ))
        migrations = read_migrations(migrations_path)

        with backend.lock():
            # Apply any outstanding migrations
            backend.apply_migrations(backend.to_apply(migrations))

