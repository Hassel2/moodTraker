import yaml
from mysql.connector import connect, Error
from yoyo import read_migrations
from yoyo import get_backend


class Database:
    def __init__(self):
        with open("./database/cfg.yaml", "r") as stream:
            try:
                self.config = yaml.safe_load(stream)["database"]
            except yaml.YAMLError as exc:
                print(exc)

        try:
            self.connetion =  connect(
                host=str(self.config["host"]),
                user=str(self.config["user"]),
                password=str(self.config["password"]),
            )
        except Error as e:
            print(e)


    def migrate(self):
        backend = get_backend(f'mysql://{self.config["user"]}:{self.config["password"]}@{self.config["host"]}/mood')
        migrations = read_migrations('./database/migrations')

        with backend.lock():
            # Apply any outstanding migrations
            backend.apply_migrations(backend.to_apply(migrations))
            
            # Rollback all migrations
            backend.rollback_migrations(backend.to_rollback(migrations))


