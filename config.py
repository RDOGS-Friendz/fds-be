import os
from datetime import datetime, timedelta

from dotenv import dotenv_values

env_values = {
    **dotenv_values(".env"),
    **os.environ,
}


class DBConfig:
    host = env_values.get('PG_HOST')
    port = env_values.get('PG_PORT')
    username = env_values.get('PG_USERNAME')
    password = env_values.get('PG_PASSWORD')
    db_name = env_values.get('PG_DBNAME')


class AppConfig:
    title = env_values.get('APP_TITLE')
    docs_url = env_values.get('APP_DOCS_URL')
    redoc_url = env_values.get('APP_REDOC_URL')


class JWTConfig:
    jwt_secret = env_values.get('JWT_SECRET', 'aaa')
    jwt_encode_algorithm = env_values.get('JWT_ENCODE_ALGORITHM', 'HS256')


db_config = DBConfig()
app_config = AppConfig()
jwt_config = JWTConfig()