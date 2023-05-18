#!/usr/bin/env python

import argparse
from database.database import Database
from app import App

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
    Database.parse_config("./database/cfg.yaml")
    App.build_and_listen()
    Database.connection.close()


def setup():
    Database.parse_config("./database/cfg.yaml")
    Database.migrate("'./database/migrations'")


if __name__ == "__main__":
    main()
