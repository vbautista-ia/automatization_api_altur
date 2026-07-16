import logging
import time

from configuration.bots import Bots
from configuration.platforms import Platforms
from repository.call_repository import CallRepository
from service.call_service import CallService
from service.messages_service import MessagesService


class CallAssetsService:

    def __init__(self, platform: Platforms):
        self.messages_service = MessagesService(platform)
        self.call_service = CallService(platform)
        self.call_repository = CallRepository(platform)
        self.PLATFORM = platform
    
    def  download_resourses_by_id_call(self, calls:list):
        bots = Bots[self.PLATFORM.name].value
        for call_id in calls:
            call = self.call_repository.retive_call(call_id)
            
            campaign = bots[call['thread']['agent']['id']]
            end_user = call['thread']['enduser']['display_name']
            path = f"{campaign}/{end_user}"
            
            time.sleep(0.1)
            self.call_service.download_recording(call_id, call['id'], path)
            
            time.sleep(0.1)
            self.messages_service.get_transciption(call['thread']['id'], path)
        logging.info('Downloads complete')

