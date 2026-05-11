from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()

class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

config = {
    "dev": BaseConfig,
}


