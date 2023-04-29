import argparse
from database.database import Database

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--setup', action='store_true', help='create and migrate database schema')
    parser.add_argument('-r', '--run', action='store_true', help='run application')
    args = parser.parse_args()

    if args.setup and args.run:
        exit(1)

    if args.setup:
        setup()
        exit(0)

    if args.run:
        start()
        exit(0)


def start():
    pass


def setup():
    Database.parse_config()
    Database.migrate()


if __name__ == "__main__":
    main()
