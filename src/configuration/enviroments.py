import os
from dotenv import load_dotenv


class EnvNotFound(Exception):
    pass

START_ENV = 'API_KEY_'
URL = 'URL_BASE'

load_dotenv()

def get_env(name_env: str):
    ENV = os.getenv(name_env)
    if not ENV:
        raise EnvNotFound(f"Env {name_env} not found")
    print(ENV)
    return ENV