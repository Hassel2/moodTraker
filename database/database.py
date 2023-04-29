import yaml
from mysql.connector import connect, Error
from yoyo import read_migrations
from yoyo import get_backend


class Database:
    config = None
    connection = None
    

    @staticmethod
    def connect():
        try:
            Database.connetion =  connect(
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

