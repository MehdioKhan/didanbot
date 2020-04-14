import os


class SqliteConfig:
    db_name = os.environ.get('DB_NAME','db')
    database_url = "sqlite:///{}.sqlite".format(db_name)

class BotConfig:
    CHANNEL = '@whitexx'