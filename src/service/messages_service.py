import asyncio
from datetime import datetime
import io
import logging
import pandas as pd
import zipfile

import httpx

from config.platforms import Platforms
from models.call import AnsweredBy
from repository.campaigns_repository import CampaignRepository
from repository.messages_repository import MessagesRepository
from utils.utils import get_bots_by_paltform, get_bots_contains, get_bots_start_with, iso_to_datetime, to_date_iso


tags = {
    'recordatoriodepromesa': 'RECORDATORIO DE PROMESA',
    'promesa': 'PROMESA',
    'nodefine': 'NO DEFINE',
    'reagenda': 'REAGENDA',
    'agenda': 'AGENDA',
    'familiar': 'FAMILIAR',
    'tercero': 'TERCERO',
    'terceros': 'TERCEROS',
    'cuelga': 'CUELGA',
    'ocupado': 'OCUPADO',
    'screeningios': 'Screening iOS',
    'screening¡os': 'Screening iOS',
    'equivocado': 'EQUIVOCADO',
    'buzon': 'BUZON',
    'contestadora': 'CONTESTADORA'
}

def get_highest_priority_tag(tags_call: list[str]):
    if tags_call:    
        clean_tags = [tag.strip().replace(' ', '').casefold() for tag in tags_call.copy()]
        
        for key, tag in tags.items():
            if key in clean_tags:
                return tag
    return 'SIN CLASIFICACION'

class MessagesService:
    ROLES = {
        'AI': 'AGENTE',
        'EU': 'CLIENTE',
        'SYS': 'SISTEMA'
    }

    def __init__(self, platform: Platforms):
        self.PLATFORM = platform
        self.messages_repository = MessagesRepository(self.PLATFORM)
        self.campaign_repository = CampaignRepository(self.PLATFORM)
        
    async def get_transcriptions(self, start_date: str, end_date: str, segmento, content):
        start = to_date_iso(start_date)
        end = to_date_iso(end_date)

        bots = get_bots_by_paltform(self.PLATFORM)
        agents = get_bots_contains(get_bots_start_with(bots, segmento), content)
        

        zip_buffer = io.BytesIO()
        
        info_call = {
            'id': [],
            'thread_id': [],
            'id_campaign': [],
            'name_bot': [],
            'name_campaign': [],
            'started_at': [],
            'duration': [],
            'phone_number': [],
            'result': [],
        }
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            async with httpx.AsyncClient(timeout=30) as client:
                for agent_id, agent_name in agents.items():
                    has_next_campaings = True
                    cursor = None
                    while has_next_campaings:
                        response_campaigns = await self.campaign_repository.list_campigns(client, start, end, cursor=cursor, agentId=agent_id)
                        campaigns: dict = response_campaigns.get('campaigns')
                        
                        if campaigns:
                            for campaign in campaigns:
                                page_index = 0
                                has_next_calls = True
                                while has_next_calls:
                                    response_calls = await self.campaign_repository.get_campaign_calls(client, campaign['id'], page_index, answeredBy=AnsweredBy.HUMAN)
                                    calls = response_calls.get('calls')
                                    
                                    if calls:
                                        for call in calls:
                                            tag = get_highest_priority_tag(call['tags'])
                                            path = f"{agent_name}/{tag}"
                                            started_at = iso_to_datetime(call['started_at'])
                                            ended_at = iso_to_datetime(call['ended_at'])
                                            thread_id = call['thread_id']
                                            transcription = await self.get_transciption(thread_id, client, started_at, ended_at)
                                            await asyncio.sleep(1)
                                            if transcription:
                                                zip_file.writestr(f"{path}/{call['id']}.txt", transcription)
                                                
                                                info_call['id'].append(call['id'])
                                                info_call['thread_id'].append(thread_id)
                                                info_call['id_campaign'].append(campaign['id'])
                                                info_call['name_campaign'].append(campaign['name'])
                                                info_call['name_bot'].append(agent_name)
                                                info_call['started_at'].append(started_at.replace(tzinfo=None))
                                                info_call['duration'].append(call['duration'])
                                                info_call['phone_number'].append(call['contact']['phone_number'])
                                                info_call['result'].append(tag)
                                       
                                    calls_pagination = response_calls.get('pagination', {})
                                    has_next_calls = calls_pagination.get('has_next', False)
                                    page_index = calls_pagination.get('next_page')
                    
                    
                        campaigns_pagination: dict = response_campaigns.get('pagination', {})
                        has_next_campaings = campaigns_pagination.get('has_next', False)
                        cursor = campaigns_pagination.get('next_cursor')

            if len(info_call['id']) > 0:
                df = pd.DataFrame(info_call)
                excel_buffer = io.BytesIO()
                df.to_excel(excel_buffer, sheet_name='calls', index=False, engine='openpyxl')
                zip_file.writestr('transcription_calls.xlsx', excel_buffer.getvalue())
        
        zip_buffer.seek(0)
        return zip_buffer

    async def get_transciption(self, id, client, started_at = None, ended_at = None):
        conversation = await self.messages_repository.get_messages(id, client)
        return self.toTranscription(id, conversation, started_at, ended_at)

    def get_all_transcriptions(self, ids:list, path_download):
        for id in ids:
            self.get_transciption(id, path_download)
    
    def date_formatter(self, iso_string):
        try:
            dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return iso_string
    
    def toTranscription(self, thread_id, conversation, started_at = None, ended_at = None):

        if conversation:
            logging.info(f"Start generating thread {thread_id}")
            lines = [
                f"Transcipción de conversación: {thread_id}\n\n\n"
            ]
            
            for message in conversation:
                sent_at = iso_to_datetime(message['sent_at'])
                
                if sent_at > started_at and sent_at < ended_at:
                    sent_by = message['sent_by']
                    rol = self.ROLES[sent_by]
                    date = self.date_formatter(message['sent_at'])
                    content = message['content'].strip()

                    if rol == 'SISTEMA':
                        lines.append(f"[{date}] {rol} >>> {content}\n")
                    else:
                        lines.append(f"[{date}] {rol}: {content}\n")
            logging.info(f"End generating thread {thread_id}")
                    
            if len(lines) > 2:
                return ''.join(lines)
        logging.info(f"Not found messages in conversation: {thread_id}")
        return None