import logging
import requests

from configuration.config import get_api_key
from configuration.platforms import Platforms


class MessagesRepository:
    URL_THREAD = 'https://api.altur.io/api/v1.0/message/THREAD_ID'

    def __init__(self, platform: Platforms):
        self.TOKEN = get_api_key(platform)
        self.HEADERS = { 'Authorization': f'api-key {self.TOKEN}'}

    def get_messages(self, id):
        url = self.URL_THREAD.replace('THREAD_ID', id)
        try:
            response = requests.get(url, headers=self.HEADERS)
 
            if response.status_code == 200:
                return response.json()
            else:
                logging.warning(f"Failed downloading thread {id}. Error: {response.status_code}, message: {response.text}")
                return None
        except Exception as e:
            logging.error(f"Error downlanding record {id}. Error: {e}", stack_info=True)
            return None