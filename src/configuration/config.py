import os
from dotenv import load_dotenv

from configuration.platforms import Platforms

START_ENV = 'API_KEY_'
URL = 'URL_BASE'
load_dotenv()

# Carga las variables desde el archivo .env
def get_api_key(platform: Platforms):
    # load_dotenv()
    return os.getenv(f'{START_ENV}{platform.name}')

def get_url_base():
    return os.getenv(URL)