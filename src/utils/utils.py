
from datetime import date, datetime
import logging
import os

import pandas as pd

from configuration.bots import Bots
from configuration.platforms import Platforms

def get_bots_by_paltform(platform:Platforms):
    return Bots[platform.name].value

def get_bots_start_with(bots: dict, start_wiht:str):
    return {key: bot for key, bot in bots.items() if bot.startswith(start_wiht)} if start_wiht else bots

def get_bots_contains(bots: dict, content:str):
    return {key: bot for key, bot in bots.items() if content in bot} if content else bots

def to_date_iso(valor_fecha):
    if isinstance(valor_fecha, datetime):
        return valor_fecha.isoformat()

    if isinstance(valor_fecha, str):
        texto_limpio = valor_fecha.strip().replace("/", "-")
        
        try:
            fecha_obj = datetime.strptime(texto_limpio, "%Y-%m-%d %H:%M:%S")
            return fecha_obj.isoformat()
            
        except ValueError:
            try:
                fecha_obj = datetime.strptime(texto_limpio, "%Y-%m-%d")
                return fecha_obj.isoformat()
                
            except ValueError:
                raise ValueError(f"Formato invalido. Formato valido: YYYY-MM-DD o YYYY-MM-DD HH:MM:SS")
    raise ValueError(f"Tipo de dato incorrecto: {type(valor_fecha).__name__}. Debe de ser Texto o Fecha: YYYY-MM-DD o YYYY-MM-DD HH:MM:SS ")

def get_month(date: date):
    MESES_ES = (
        "", "enero", "febrero", "marzo", "abril", "mayo", "junio", 
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    )
    return MESES_ES[date.month]

def to_row_excel(campaign, contact):
    return {
        'campaign_name': campaign['name'],
        'campaign_create_at':  datetime.fromisoformat(campaign['created_at']).date(),
        'id': contact['f_id'],
        'contact': contact['contact'],
        'name': contact['name'],
        'context': contact['context'],
        'status': contact['status'],
        'retries': contact['retries'],
        'calls': contact['call_count'],
        'billed_duration': contact['billed_duration'],
        'last_update': contact['last_call_at'],
        'follow_up': contact['has_follow_up'],
        'tags': contact['tags'],
        'extracted_data': contact['extracted_data'],
    }
    
def to_excel(prefix_name, result, root_path):
    logging.info("<<<<<<<<<< Save in excel flile >>>>>>>>>>")
    df = pd.DataFrame(result)
            
    tags_df = df['tags'].str.join('|').str.get_dummies()
    tags_df = tags_df.astype(bool)
    df = df.join(tags_df)
    df = df.drop(columns=['tags'])
    
    diccionarios = df['extracted_data'].apply(lambda x: x if isinstance(x, dict) else {})
    extracted_df = pd.DataFrame(diccionarios.tolist(), index=df.index)
    extracted_df = extracted_df.fillna("").astype(str)
    
    df = df.join(extracted_df)
    df = df.drop(columns=['extracted_data'])

    file_name_base = f"{prefix_name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    path = os.path.join(root_path)
    os.makedirs(path, exist_ok=True)   

    MAX_ROWS = 1048570 

    if len(df) <= MAX_ROWS:
        full_path = os.path.join(path, f"{file_name_base}.xlsx")
        df.to_excel(full_path, sheet_name='calls', index=False, engine="openpyxl")
    
    else:
        logging.info(">>> El archivo supera el límite de Excel. Segmentando por campañas...")
        
        campaign_groups = df.groupby('campaign_name')
        current_chunk_dfs = []
        current_row_count = 0
        file_index = 1
        
        for campaign_name, group_df in campaign_groups:
            group_len = len(group_df)
   
            if current_row_count + group_len > MAX_ROWS and current_chunk_dfs:
                chunk_to_save = pd.concat(current_chunk_dfs)
                chunk_path = os.path.join(path, f"{file_name_base}_part_{file_index}.xlsx")
                chunk_to_save.to_excel(chunk_path, sheet_name='calls', index=False, engine="openpyxl")
                print(f"Guardado {chunk_path} con {current_row_count} registros.")
                
                current_chunk_dfs = []
                current_row_count = 0
                file_index += 1
            
            current_chunk_dfs.append(group_df)
            current_row_count += group_len
            
        if current_chunk_dfs:
            chunk_to_save = pd.concat(current_chunk_dfs)
            chunk_path = os.path.join(path, f"{file_name_base}_part_{file_index}.xlsx")
            chunk_to_save.to_excel(chunk_path, sheet_name='calls', index=False, engine="openpyxl")
            print(f"Guardado {chunk_path} con {current_row_count} registros (Último archivo).")
    