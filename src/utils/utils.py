
from datetime import date, datetime
import io
import logging
import zipfile

import pandas as pd

from config.bots import Bots
from config.platforms import Platforms

def get_bots_by_paltform(platform:Platforms):
    return Bots[platform.name].value

def get_bots_start_with(bots: dict, start_wiht:str):
    return {key: bot for key, bot in bots.items() if bot.startswith(start_wiht)} if start_wiht else bots

def get_bots_contains(bots: dict, content:str):
    lower_bots = {key: bot.casefold() for key, bot in bots.items()}
    if content:
        content = content.casefold()
        return {key: bot for key, bot in lower_bots.items() if content in bot}
    return bots

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

def iso_to_datetime(value_date: str | None):
    if value_date:
        return datetime.fromisoformat(value_date)
    return None

def get_month(date: date):
    MESES_ES = (
        "", "enero", "febrero", "marzo", "abril", "mayo", "junio", 
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    )
    return MESES_ES[date.month]

def to_row_excel(campaign, contact):
    return {
        'campaign_name': campaign['name'],
        'campaign_date':  datetime.fromisoformat(campaign['created_at']).date(),
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
    
def to_excel(prefix_name, result):
    logging.info("<<<<<<<<<< Save in excel flile >>>>>>>>>>")
    df = pd.DataFrame(result)
    
    if 'last_update' in df.columns:
        df['last_update'] = pd.to_datetime(df['last_update']).dt.tz_localize(None)
    
    if 'tags' in df.columns:
        tags_df = df['tags'].apply(lambda x: x if isinstance(x, list) else [])
        tags_df = df['tags'].str.join('|').str.get_dummies()
        tags_df = tags_df.astype(bool).astype(str)
        df = df.join(tags_df).drop(columns=['tags'])
    
    if 'follow_up' in df.columns:
        df['follow_up'] = df['follow_up'].astype(str)   
    
    if 'extracted_data' in df.columns:
        diccionarios = df['extracted_data'].apply(lambda x: x if isinstance(x, dict) else {})
        extracted_df = pd.DataFrame(diccionarios.tolist(), index=df.index)
        extracted_df = extracted_df.fillna("").astype(str)
        df = df.join(extracted_df).drop(columns=['extracted_data'])

    file_name_base = f"{prefix_name}_contacts_mult_camp"
    zip_buffer = io.BytesIO()
    MAX_ROWS = 1048570 
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:

        if len(df) <= MAX_ROWS:
            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, index=False, engine='openpyxl')
            file_name = f"{file_name_base}.xlsx"
            zip_file.writestr(file_name, excel_buffer.getvalue())
        
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
                    chunk_path = f"{file_name_base}_part_{file_index}.xlsx"
                    
                    chunk_excel_buffer = io.BytesIO()
                    chunk_to_save.to_excel(chunk_excel_buffer, sheet_name='contacts', index=False, engine='openpyxl')
                    zip_file.writestr(chunk_path, chunk_excel_buffer.getvalue())
                    logging.info(f"Guardado {chunk_path} con {current_row_count} registros.")
                    
                    current_chunk_dfs = []
                    current_row_count = 0
                    file_index += 1
                
                current_chunk_dfs.append(group_df)
                current_row_count += group_len
                
            if current_chunk_dfs:
                chunk_to_save = pd.concat(current_chunk_dfs)
                chunk_path = f"{file_name_base}_part_{file_index}.xlsx"
                
                chunk_excel_buffer = io.BytesIO()
                chunk_to_save.to_excel(chunk_excel_buffer, sheet_name='contacts', index=False, engine="openpyxl")
                zip_file.writestr(chunk_path, chunk_excel_buffer.getvalue())
                logging.info(f"Guardado {chunk_path} con {current_row_count} registros (Último archivo).")
    zip_buffer.seek(0)
    return zip_buffer