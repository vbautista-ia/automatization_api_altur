import logging
import httpx
import requests

from configuration.enviroments import START_ENV, get_env
from configuration.platforms import Platforms


class CallRepository:
    URL_DOWNLOAD_CALL = 'https://api.altur.io/api/v1.0/call/ID/recording'
    URL_RETRIVE_CALL = 'https://api.altur.io/api/v1.0/call/ID'
    
    def __init__(self, platform: Platforms):
        self.TOKEN = get_env(f"{START_ENV}{platform.name}")
        self.HEADERS = { 'Authorization': f'api-key {self.TOKEN}'}

    async def retrive_call_recording(self, id, client: httpx.AsyncClient):
        url = self.URL_DOWNLOAD_CALL.replace('ID', str(id))
        try:
            response = await client.get(url=url, headers=self.HEADERS)
            if response.status_code == 200:
                return response
            logging.warning(f"Failed downloading record, id {id}. Error: {response.status_code}, message: {response.text}")
            return None
        except Exception as e:
            logging.error(f"Error fetching record {id} from API. Error: {e}", exc_info=True)
            return None

    def retive_call(self, id):
        url = self.URL_RETRIVE_CALL.replace('ID', id)
        
        try:
            response = requests.get(url, headers=self.HEADERS)

            if response.status_code == 200:
                logging.info(f"Retrive call {id}")
                return response.json()
            logging.warning(f"Failed retrive call {id}. Error {response.status_code}, message: {response.text}")
            return None
        
        except Exception as e:
            logging.error(f"Error retive call {id} . Error: {e.with_traceback()}", stack_info=True)


