from datetime import datetime
import logging
import os

from configuration.platforms import Platforms
from repository.messages_repository import MessagesRepository


class MessagesService:
    ROLES = {
        'AI': 'AGENTE',
        'EU': 'CLIENTE',
        'SYS': 'SISTEMA'
    }

    def __init__(self, platform: Platforms):
        self.PLATFORM = platform
        self.messages_repository = MessagesRepository(self.PLATFORM)

    def get_transciption(self, id, path_download):
        conversation = self.messages_repository.get_messages(id)
        self.toTranscription(conversation, path_download)

    def get_all_transcriptions(self, ids:list, path_download):
        for id in ids:
            self.get_transciption(id, path_download)
    
    def date_formatter(self, iso_string):
        try:
            dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return iso_string
    
    def toTranscription(self, conversation, path_save):

        if conversation:
            path_root = f"{self.PLATFORM.value}/{path_save}"
            os.makedirs(path_root, exist_ok=True)
            thread_id = conversation[0]['thread_id']
            
            path = os.path.join(path_root, f"{thread_id}.txt")

            with open(path, "a", encoding="utf-8") as file:
                logging.info(f"Start writting thread {thread_id}")
                file.write(f"Transcipción de conversación: {thread_id}\n")
                file.write(f"Total de Mensajes:     {len(conversation)}\n\n\n")

                for message in conversation:
                    sent_by = message['sent_by']
                    rol = self.ROLES[sent_by]
                    date = self.date_formatter(message['sent_at'])
                    content = message['content'].strip()

                    if rol == 'SISTEMA':
                        file.write(f"[{date}] {rol} >>> {content}\n")
                    else:
                        file.write(f"[{date}] {rol}: {content}\n")
                logging.info(f"End writting thread {thread_id} in {path}")
        else:
            logging.info(f"Not found messages in conversation: {conversation}")
