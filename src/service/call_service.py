from collections import defaultdict
from datetime import datetime, timedelta
import logging
import os
import time

from configuration.bots import Bots
from configuration.platforms import Platforms
from repository.call_repository import CallRepository
from repository.campaigns_repository import CampaignRepository
from status import StatusCampaign


class CallService:
    
    def __init__(self, platform: Platforms):
        self.PLATFORM = platform
        self.call_repository = CallRepository(self.PLATFORM)
        self.campaign_repository = CampaignRepository(self.PLATFORM)

    def download_recording(self, id, name_file, path_download, id_bot):
        recording = self.call_repository.retrive_call_recording(id)

        if not recording:
            logging.warning(f"Not found response recording {id}")
            return False
        
        try:
            bots = Bots[self.PLATFORM.name].value
            campaign = ''
            if id_bot:
                campaign = bots[id_bot]

            path_root = os.path.join(self.PLATFORM.value, campaign, path_download)
            os.makedirs(path_root, exist_ok=True)
            path = os.path.join(path_root, f"{name_file}.wav")                

            with open(path, 'wb') as record:
                for chunk in recording.iter_content(chunk_size=8192):
                    record.write(chunk)
            
            logging.info(f"Download record, id {id} in {path}")
        except Exception as e:
            logging.error(f"Error saving record {id} in {path}. Error: {e}", exc_info=True)
            return 
        
    def download_all_recording_by_account(self, accounts_search: dict):
        logging.info(f"Start downloads {len(accounts_search)}")
        # {'fecha': [{'el numero de cuenta': la fecha de inicio}, ]}
        for key, value in accounts_search.items():
            cursor = ''
            has_next_campaign = True
            accounts = {k: v for d in value for k, v in d.items()}
            # min_hour, max_hour = self.max_and_min_hour_whit_margen(value)

            while has_next_campaign:
                cursor = None if cursor == '' else cursor
                # result = self.campaign_repository.list_campigns(cursor=cursor, startDate=f"{key}T{min_hour}", endDate=f"{key}T{max_hour}")
                result = self.campaign_repository.list_campigns(cursor=cursor, startDate=f"{key}T00:00:00", endDate=f"{key}T23:59:59", archived=True)
                for campaign in result['campaigns']:
                    page_index = 0
                    has_next_page = True
                    while has_next_page:
                        campaigns_call = self.campaign_repository.get_campaign_calls(campaign['id'], page_index)
                        time.sleep(0.1)
                        for call in campaigns_call['calls']:
                            if call['contact']['f_id'] in accounts and call['billed_duration'] > 0:
                                self.download_recording(call['id'], f"{call['id']}_{self.format_time(call['started_at'])}",f"{key}/{call['contact']['f_id']}", campaign['agent']['id'])
                        
                        has_next_page = campaigns_call['pagination']['has_next']
                        page_index += 1
                has_next_campaign = result['pagination']['has_next']
                cursor = result['pagination']['next_cursor']
        logging.info(f"End downloads campaigns")

    def to_iso_date(self, date, time):
        date_time = f"{date} {time}"
        dt_obj = datetime.strptime(date_time, "%m/%d/%Y %H:%M:%S")
        return dt_obj.strftime("%Y-%m-%dT%H:%M:%SZ")

    def format_time(self, time_str):
        clean_time_str = time_str.replace('Z', '+00:00')
        return datetime.fromisoformat(clean_time_str).strftime("%H_%M_%S")

    def max_and_min_hour_whit_margen(self, lista_registros):
        if not lista_registros:
            return None, None

        formato = '%H:%M:%S'
        tiempos_dt = [datetime.strptime(hora, formato)
                      for registro in lista_registros
                      for hora in registro.values()]
        
        tiempo_min = min(tiempos_dt)
        tiempo_max = max(tiempos_dt)
        
        margen = timedelta(minutes=5)
        
        min_con_margen = tiempo_min - margen
        max_con_margen = tiempo_max + margen
        
        return min_con_margen.strftime(formato), max_con_margen.strftime(formato)        



