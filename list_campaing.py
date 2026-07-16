import pandas as pd
import requests
import os
from datetime import datetime
import json
import time

# --- 1. CONFIGURACIÓN DE CONTROL ---
META_POR_MES_Y_CAT = 20 # 20 de marzo y 20 de abril por cada categoría
INICIO_INDICE = 0
CATEGORIAS_A_DESCARGAR = [] # Vacío para todas

# --- 2. CONFIGURACIÓN DE API Y RUTAS ---
TOKEN = 'sk-y1WYihu7Tuezza2j7VUcQ73No1oM9b0HO'
path_grabaciones = '../../grabaciones/llamadas_SPC_70'

date = '2026-05-14'
cuentas = [

'007423579681168413'

]
CARPETA_RAIZ = path_grabaciones + 'HIPOTECARIO'
producto = 'SPC_HIPOTECARIO'
horarios = [

'14:39:40'

]

URL_BASE = f'https://api.altur.io/api/v1.0/campaigns?pageSize=50&status=finished&startDate={date}T00:00:00Z&endDate={date}T23:59:00Z'

URL_BASE_RECORDING = 'https://api.altur.io/api/v1.0/call/ID/recording'



horarios_dt = [datetime.fromisoformat(f"{date}T{h}-06:00") for h in horarios]

# ID_CAMPAIGN = 54465
response = requests.get(URL_BASE,
                        headers={'Authorization': f'api-key {TOKEN}'})

print(response.status_code)

r = []

for resu in response.json()['campaigns']:
    if resu['name'].startswith(producto):
        r.append({'id': resu['id'], 'name': resu['name'], 'created_at': resu['created_at'], 'last_iteration': resu['cycle_last_iteration_at']})

#FILTRAR CAMPAÑAS POR HORARIO DE LLAMADA
campanas_filtradas = []
for campana in r:
    # Convertimos los strings de la campaña a datetime
    inicio = datetime.fromisoformat(campana["created_at"])
    fin = datetime.fromisoformat(campana["last_iteration"])
    
    # Comprobamos si ALGÚN horario de nuestra lista cae dentro de este rango
    for horario in horarios_dt:
        if inicio <= horario <= fin:
            campanas_filtradas.append(campana)
            break # Si ya encontramos un horario que encaja, guardamos la campaña y dejamos de buscar en esta



##LLAMADAS DE CAMPAÑAS
page_index = 0
page_size = 100
URL_BASE_CALL_CAMPAING = 'https://api.altur.io/api/v1.0/campaigns/ID/calls?pageSize=100&pageIndex=INDEX'


def getCampaingsCalls(campaing_id, page_index, url):
    url = url.replace('ID', f'{campaing_id}').replace('INDEX', f'{page_index}')
    print(url)
    return requests.get(url,
                        headers={'Authorization': f'api-key {TOKEN}'})

def findCuenta(calls):
    for call in calls:
        return ({
            'id': call['id'],
            'numero_cuenta': call['contact']['f_id'],
            'created_at': call['created_at'],
            'status': call['contact']['f_id'],
            'duration': call['duration']
        })


calls = []
for campaing in campanas_filtradas:
    next = True
    page_index = 0
    while next:
        response = getCampaingsCalls(campaing['id'], page_index, URL_BASE_CALL_CAMPAING)
        time.sleep(0.1)
        response_json = response.json()
        # print(response_json)
        for call in response_json['calls']:
            if call['contact']['f_id'] in cuentas:
                calls.append({
                    'id': call['id'],
                    'numero_cuenta': call['contact']['f_id'],
                    'answered_by': call['answered_by'],
                    'created_at': call['created_at'],
                    'phone_number': call['contact']['phone_number'],
                    'duration': call['duration']
                })

        next = response_json['pagination']['has_next']
        page_index += 1


# for campaing in campanas_filtradas:

#     URL_BASE_CALL_CAMPAING = URL_BASE_CALL_CAMPAING.replace('ID', f'{campaing[0]['id']}')

#     response = requests.get(URL_BASE_CALL_CAMPAING,
#                         headers={'Authorization': f'api-key {TOKEN}'})


# result = response.json()

with open('test.txt', 'w', encoding='utf-8') as file:
    # file.write(json.dumps(result, indent=4))
    # json.dump(r, file, indent=4, ensure_ascii=False)
    # json.dump(campanas_filtradas, file, indent=4, ensure_ascii=False)
    json.dump(calls, file, indent=4, ensure_ascii=False)


#EXPORT RECORDS
for call in calls:
    fecha_dt = datetime.fromisoformat(call['created_at'])

    fecha_formateada = fecha_dt.strftime('%d-%m-%Y')

    ruta_directorio = os.path.join(path_grabaciones, CARPETA_RAIZ, str(fecha_formateada))
    os.makedirs(ruta_directorio, exist_ok=True)
    print(f"--- : Descargando {call['numero_cuenta']} archivos ---")
    
    id_llamada = call['id']
    # Formato de fecha para el nombre del archivo: DD-MM-AAAA
    numero_cuenta = call['numero_cuenta']

    try:
        url = URL_BASE_RECORDING.replace('ID', id_llamada)
        response = requests.get(url, 
                                headers={'Authorization': f'api-key {TOKEN}'}, 
                                stream=True)
        
        if response.status_code == 200:
            nombre_archivo = f"{id_llamada}_{numero_cuenta}.wav"
            ruta_final = os.path.join(ruta_directorio, nombre_archivo)
            
            with open(ruta_final, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        else:
            response
            print(f"  ⚠️ Error API {response.status_code} en ID {id_llamada}")
            
    except Exception as e:
        print(f"  ❌ Error en ID {id_llamada}: {e}")


print('end')