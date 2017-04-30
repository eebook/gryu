#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os


class Config:
    DB_USER = os.getenv("DB_USER", 'postgres')
    DB_PASSWORD = os.getenv("DB_PASSWORD", None)
    DB_NAME = os.getenv("DB_NAME", "postgres")
    DB_HOST = os.getenv("DB_HOST", "db")
    DB_PORT = os.getenv("DB_PORT", 5432)
    DB_ENGINE = os.getenv("DB_ENGINE", "postgresql")
    SQLALCHEMY_DATABASE_URI = '{db_engine}://{user_name}:{password}@{hostname}/{database}'.\
                              format_map({
                                  'db_engine': DB_ENGINE,
                                  'user_name': DB_USER,
                                  'password': DB_PASSWORD,
                                  'hostname': DB_HOST,
                                  'database': DB_NAME
                              })
    print("SQLLCHEMY???{}".format(SQLALCHEMY_DATABASE_URI))

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    pass


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,

    "default": DevelopmentConfig
}
