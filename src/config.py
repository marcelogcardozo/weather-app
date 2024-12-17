from os import environ

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))

DB_HOST = environ.get("DB_HOST")
DB_PORT = environ.get("DB_PORT")
DB_USER = environ.get("DB_USER")
DB_PASSWORD = environ.get("DB_PASS")
DB_NAME = environ.get("DB_NAME")
DB_DRIVER = environ.get("DB_DRIVER")
