import datetime
import io
import json
import logging
from typing import Literal
import zipfile

import pandas as pd

from repository.nuxiba_repository import NuxibaRepository


class NuxibaService:
    def __init__(self, repository: NuxibaRepository):
        self.repository = repository
    
    def get_transcriptions(self, campaign: str = None, start: datetime = None, end: datetime = None, min_duration: int = 0):
        
        response = self.repository.get_transcriptions(campaign, start, end, min_duration)
        
        if response:
            zip_buffer = io.BytesIO()
            info_call = {
                'id': [],
                'campaign': [],
                'start_at': [],
                'duration': [],
                'result': [],
            }
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for row in response:
                    transcription = row.get('transcription', {})
                    
                    if transcription:
                        
                        messages = json.loads(transcription).get('transcript', [])
                        client, product = self.__extraer_cliente_producto(row['campaign'])
                        tag = row['result']
                        if not tag:
                            tag = 'SIN CLASIFICACION'
                        
                        id_call = row['id']
                        start_transcript = row['start_at']
                        
                        info_call['id'].append(id_call)
                        info_call['campaign'].append(product)          
                        info_call['start_at'].append(start_transcript)          
                        info_call['duration'].append(row['duration'])          
                        info_call['result'].append(tag)
                        
                        path = f"{client}/{product}/{tag}"
                        
                        transcript = self.__toTranscription(id_call, messages, product, tag, started_at=start_transcript, platform='NUXIBA')
                        zip_file.writestr(f"{path}/{id_call}.txt", transcript)
        
                if len(info_call['id']) > 0:
                    df = pd.DataFrame(info_call)
                    excel_buffer = io.BytesIO()
                    df.to_excel(excel_buffer, sheet_name='calls', index=False, engine='openpyxl')
                    zip_file.writestr('transcription_calls.xlsx', excel_buffer.getvalue())
            
            zip_buffer.seek(0)
            return zip_buffer

    def __toTranscription(self, thread_id, conversation, campaign, tag, started_at = None, ended_at = None, platform: Literal['NUXIBA', 'ALTUR', 'HIVECLOUD'] = 'HIVECLOUD'):
        ROLES = {
                'AI': 'AGENTE',
                'EU': 'CLIENTE',
                'SYS': 'SISTEMA',
                'agent': 'AGENTE',
                'user': 'CLIENTE'
            }

        if conversation:
            logging.info(f"Start generating thread {thread_id}")
            lines = [
                f"Transcipción de conversación: {thread_id}\n",
                f"Campaña: {campaign}\n",
                f"Clasificacion: {tag}\n",
                f"Fecha llamada: {started_at}\n\n\n",
                f"Conversacion:\n"
            ]
            
            if platform == 'ALTUR':                
                for message in conversation:
                    sent_by = message['sent_by']
                    rol = ROLES[sent_by]
                    date = self.date_formatter(message['sent_at'])
                    content = message['content'].strip()

                    if rol == 'SISTEMA':
                        lines.append(f"[{date}] {rol} >>> {content}\n")
                    else:
                        lines.append(f"[{date}] {rol}: {content}\n")
                logging.info(f"End generating thread {thread_id}")
            
            elif platform == 'NUXIBA':
                for message in conversation:
                    rol = ROLES[message.get('role')]
                    date = message.get('datetime')
                    content = message.get('content')
                    
                    lines.append(f"[{date}] {rol}: {content}\n")
                    
            if len(lines) > 1:
                return ''.join(lines)
        logging.info(f"Not found messages in conversation: {thread_id}")
        return None
    
    def __extraer_cliente_producto(self, campaign_name: str) -> dict:
        if not campaign_name:
            return ('', '')
            
        partes = campaign_name.strip().split()
        
        if len(partes) == 0:
            return ('', 'SIN CLASIFICACION')
            
        client = partes[0]
        
        if len(partes) == 1:
            return (client, 'SIN CLASIFICACION')
            
        if partes[-1].isdigit():
            producto_partes = partes[1:-1]
        else:
            producto_partes = partes[1:]
            
        product = ''.join(producto_partes)
        
        return (client, product)