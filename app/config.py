# coding=utf-8
import datetime
import os

secretkey = ""
with open("secretkey.txt", 'r') as sk:
    content = sk.readlines()
    secretkey = content[0]

from dotenv import load_dotenv, find_dotenv

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
LOCAL_ENV_FILE = find_dotenv('.env.local')
if LOCAL_ENV_FILE:
    load_dotenv(LOCAL_ENV_FILE)


class Config(object):
    """
    Initial Configurations for the Flask App
    """
    CSRF_ENABLED = True
    DEBUG = False

    SECRET_KEY = os.environ.get("SECRET_KEY",
                                secretkey)
    expires = datetime.timedelta(days=30)
    SQLALCHEMY_TRACK_MODIFICATIONS = None
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DB')
    PRODUCTION = False


class DevelopmentConfig(Config):
    """
    Developmental Configurations
    """
    DEBUG = True
    LOCALE_DEFAULT = "en_US"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'


# Start 3:31:50
# 3:39


class ProductionConfig(Config):
    """
    Production Configurations
    """
    PRODUCTION = True
    DEBUG = False
    LOCALE_DEFAULT = 'en_US.utf8'
    JWT_COOKIE_SECURE = True


class TestingConfig(Config):
    """
    Testing Configurations
    """
    TESTING = True
    CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
