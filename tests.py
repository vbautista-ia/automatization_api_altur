from datetime import datetime
import os
import time

import requests
from collections import defaultdict


def date_formatter(iso_string):
    """
    Convierte la fecha de formato ISO a un formato más legible.
    Ejemplo: '2023-11-07T05:31:56Z' -> '2023-11-07 05:31:56'
    """
    try:
        # Reemplazamos la 'Z' por '+00:00' para que Python lo procese correctamente
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        # Si la fecha viene vacía o mal formada, regresamos el string original
        return iso_string
    
def toTranscription(conversation, carpeta_salida, producto, resultado):
    """
    Genera un archivo TXT individual por cada conversación en la lista.
    """
    path_salida = carpeta_salida + '/' + producto + '/' + resultado
    os.makedirs(path_salida, exist_ok=True)

    # Mapeo para traducir las siglas de tu API a roles comprensibles
    mapeo_roles = {
        "AI": "Agente",
        "EU": "Cliente",
        "SYS": "Sistema"
    }
    if conversation:
        thread_id = conversation[0]['thread_id']
        file_name = f"{thread_id}.txt"
        final_path = os.path.join(path_salida, file_name)

        # Abrimos un archivo nuevo con codificación utf-8 (importante para acentos o eñes)
        with open(final_path, "a", encoding="utf-8") as file:
            # Creamos un encabezado para el documento
            file.write(f"Transcipción de thread id: {thread_id}\n")
            file.write(f"Total de Mensajes:     {len(conversation)}\n\n\n")

            # Escribimos cada mensaje en la conversación
            for message in conversation:

                sent_by = message['sent_by']
                rol_legible = mapeo_roles[sent_by]
                fecha = date_formatter(message['sent_at'])
                contenido = message['content'].strip()
                file.write(f"[{fecha}] {rol_legible}: {contenido}\n")

            print(f"Generado con éxito {thread_id}: {final_path}")



TOKEN = 'api-key sk-y1WYihu7Tuezza2j7VUcQ73No1oM9b0HO'
AUTHORIZATION = {'Authorization': TOKEN}
URL_LIST_CAMP = 'https://api.altur.io/api/v1.0/campaigns?pageSize=100&agentId=AGENT_ID&status=finished&integration=phone_call&startDate=START_DATE&endDate=END_DATE'
URL_CAMP_CALLS = 'https://api.altur.io/api/v1.0/campaigns/ID_CAMP/calls?pageSize=100&pageIndex=PAGE_INDEX'
URL_CALL = 'https://api.altur.io/api/v1.0/call/ID'
URL_THREAD = 'https://api.altur.io/api/v1.0/message/THREAD_ID'

agents = {
    'HIPOTECARIO': '00859262-febf-41d8-b231-8b938220a613',
    'AUTO': '44395ce7-8b92-44f0-9b00-d96ee0d52c5d'
}

# AGENT_ID = 
START_DATE = '2026-04-27'
END_DATE = '2026-05-22'

PATH = '../../reportes/SPC_TRANSCRIPCIONES/'

TAGS = ['PROMESA', 'NO DEFINE', 'REAGENDA', 'OCUPADO']
campaigns = defaultdict(list)
calls = defaultdict(lambda: defaultdict(list))
threads = defaultdict(lambda: defaultdict(list))
# {producto: {promesa: [], negativa: []}}
has_cursor = False
url = URL_LIST_CAMP

for key, agent in agents.items():
    has_next = True
    cursor = ''
    url = url.replace('AGENT_ID', agent).replace('START_DATE', START_DATE).replace('END_DATE', END_DATE)
    
    while has_next:
        url_request = url + cursor
        response = requests.get(url_request,
                                headers=AUTHORIZATION)
        print("--- CAMPAÑAS ---")
        print(url_request)

        response = response.json()
        for campaign in response['campaigns']:
            campaigns[key].append(campaign['id'])
        
        has_next = response['pagination']['has_next']
        
        if has_next:
            cursor = '&cursor='
            cursor = cursor + response['pagination']['next_cursor']
        time.sleep(0.1)


for key, list_campaign in campaigns.items():
    count_promesa = 0
    count_negativa = 0
    for campaign in list_campaign:
        has_next = True
        page_index = 0

        while has_next and (count_promesa < 21 and count_negativa < 21):
            url_request = URL_CAMP_CALLS.replace('ID_CAMP', f"{campaign}").replace('PAGE_INDEX', f"{page_index}")
            response = requests.get(url_request, headers=AUTHORIZATION)
            response = response.json()
            print(f"{key} {url_request}")
            print(f"Promesas: {count_promesa} - negativa {count_negativa}")

            for call in response['calls']:

                if  TAGS[0] in call['tags']:
                    calls[key][TAGS[0]].append(call['id'])
                    count_promesa += 1

                if  TAGS[1] in call['tags']:
                    calls[key][TAGS[1]].append(call['id'])
                    count_negativa += 1

                if  TAGS[2] in call['tags']:
                    calls[key][TAGS[1]].append(call['id'])
                    count_negativa += 1
                
                if  TAGS[3] in call['tags']:
                    calls[key][TAGS[1]].append(call['id'])
                    count_negativa += 1
            has_next = response['pagination']['has_next']
            page_index += 1
            time.sleep(0.1)

        if count_promesa == 20 and count_negativa == 20:
            break


for name_campaign, campaign in calls.items():
    for name_tag, result in campaign.items():
        for call in result:
            time.sleep(0.2)
            url = URL_CALL.replace('ID', call)
            print('--- calls ---')
            print(url)
            response = requests.get(url, headers=AUTHORIZATION)
            response = response.json()

            url_thread = URL_THREAD.replace('THREAD_ID', response['thread']['id'])

            conversation = requests.get(url_thread, headers=AUTHORIZATION)

            if conversation.status_code == 200:
                messages = conversation.json()

                toTranscription(messages,  PATH, name_campaign, name_tag)


