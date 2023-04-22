from database.database import Database

def main():
    db = Database()
    db.migrate()

if __name__ == "__main__":
    main()
