from datetime import datetime, timedelta
import io
import logging
import os
import time
import zipfile

import httpx
import pandas as pd

from models.call import AnsweredBy
from config.bots import Bots
from config.platforms import Platforms
from repository.call_repository import CallRepository
from repository.campaigns_repository import CampaignRepository
from utils.utils import get_bots_by_paltform, get_bots_contains, get_bots_start_with, to_date_iso

class MaxRecordsReached(Exception):
    pass

class CallService:
    
    def __init__(self, platform: Platforms):
        self.PLATFORM = platform
        self.call_repository = CallRepository(self.PLATFORM)
        self.campaign_repository = CampaignRepository(self.PLATFORM)

    async def download(self, input_start, input_end, tag, segmento, max_records = 5, content: str = None):
        start = to_date_iso(input_start)
        end = to_date_iso(input_end)
        bots = get_bots_by_paltform(self.PLATFORM)
        agents = get_bots_start_with(bots, segmento)
        agents_search = get_bots_contains(agents, content)

        zip_buffer = io.BytesIO()
        info_call = {
            'id': [],
            'id_campaign': [],
            'name_bot': [],
            'name_campaign': [],
            'started_at': [],
            'duration': [],
            'phone_number': [],
            'tags': [],
            'Cumple': []
        }

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            async with httpx.AsyncClient(timeout=30.0) as client:
                for key, name_bot in agents_search.items():
                    try:
                        count = 0
                        has_next = True
                        cursor = None
                        while has_next:
                            list_campaigns = await self.campaign_repository.list_campigns(client=client, started_after=start, started_before=end, cursor=cursor, agentId=key)
                            campaigns = list_campaigns.get('campaigns')
                            if campaigns:
                                for campaign in campaigns:
                                    page_index = 0
                                    has_next_calls = True
                                    while has_next_calls:
                                        campaign_calls = await self.campaign_repository.get_campaign_calls(client, campaign['id'], pageIndex=page_index, answeredBy=AnsweredBy.HUMAN)
                                        calls = campaign_calls.get('calls')
                                        if calls:
                                            for call in calls:
                                                if tag in call['tags']:
                                                    response = await self.call_repository.retrive_call_recording(call['id'], client)
                                                    if response.status_code == 200:
                                                        zip_file.writestr(f"{name_bot.replace(segmento, '')}/{call['id']}.mp3", response.content)

                                                        info_call['id'].append(call['id'])
                                                        info_call['id_campaign'].append(campaign['id'])
                                                        info_call['name_campaign'].append(campaign['name'])
                                                        info_call['name_bot'].append(campaign['agent']['name'])
                                                        info_call['started_at'].append(call['started_at'])
                                                        info_call['duration'].append(call['duration'])
                                                        info_call['phone_number'].append(call['contact']['phone_number'])
                                                        info_call['tags'].append(call['tags'])
                                                        info_call['Cumple'].append('SI')

                                                        count += 1
                                                        logging.info(f">>>>{name_bot}: {count} of {max_records} recordings were found <<<<")
                                                        if count >= max_records:
                                                            raise MaxRecordsReached()
                                                    else:
                                                        print(f"Error descargando {call['id']}, {response.status_code}")

                                        has_next_calls = campaign_calls.get('pagination', {}).get('has_next', False)
                                        page_index += 1

                            cursor = list_campaigns.get('pagination', {}).get('next_cursor')
                            has_next = list_campaigns.get('pagination', {}).get('has_next', False)
                    except MaxRecordsReached:
                        pass
        
            if len(info_call['id']) > 0:
                df = pd.DataFrame(info_call)
                df['tags_joined'] = df['tags'].apply(
                lambda x: '|'.join(x) if isinstance(x, list) else str(x))
            
                tags_df = df['tags_joined'].str.get_dummies()
                tags_df = tags_df.astype(bool)    
                df = df.join(tags_df)
                df = df.drop(columns=['tags', 'tags_joined'])

                excel_buffer = io.BytesIO()
                df.to_excel(excel_buffer, index=False, engine="openpyxl")
                file_name = f"reporte_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"                
                zip_file.writestr(file_name, excel_buffer.getvalue())
        
        zip_buffer.seek(0)
        return zip_buffer
    
    async def download_calls_by_id(self, calls: list[str]):
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    for call in calls:
                        response = await self.call_repository.retrive_call_recording(call, client)
                        if response:
                            zip_file.writestr(f"{call}.mp3", response.content)
            zip_buffer.seek(0)
            return zip_buffer

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



