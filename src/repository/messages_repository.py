import asyncio
import logging
import re
import httpx

from config.enviroments import START_ENV, get_env
from config.platforms import Platforms


class MessagesRepository:
    URL_THREAD = 'https://api.altur.io/api/v1.0/message/THREAD_ID'

    def __init__(self, platform: Platforms):
        self.TOKEN = get_env(f"{START_ENV}{platform.name}")
        self.HEADERS = { 'Authorization': f'api-key {self.TOKEN}'}

    async def get_messages(self, id, client: httpx.AsyncClient):
        url = self.URL_THREAD.replace('THREAD_ID', id)
        try:
            response = await client.get(url, headers=self.HEADERS)
            
            if response.status_code == 429:
                seconds = re.search(r"(\d+)\s*seconds", response.json()['detail'])
                if seconds:
                    await asyncio.sleep(float(seconds.group(1)))
                    response = await client.get(url, headers=self.HEADERS)
 
            if response.status_code == 200:
                return response.json()
            else:
                logging.warning(f"Failed downloading thread {id}. Error: {response.status_code}, message: {response.text}")
                return None
        except Exception as e:
            logging.error(f"Error downlanding record {id}. Error: {e}", stack_info=True)
            return None