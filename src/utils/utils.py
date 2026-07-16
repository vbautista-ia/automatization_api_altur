
from datetime import datetime

from configuration.bots import Bots
from configuration.platforms import Platforms

def get_bots_by_paltform(platform:Platforms):
    return Bots[platform.name].value

def get_bots_start_with(bots: Bots, start_wiht:str):
    return {key: bot for key, bot in bots.items() if bot.startswith(start_wiht)} if start_wiht else bots

def to_date_iso(valor_fecha):
    if isinstance(valor_fecha, datetime):
        return valor_fecha.isoformat() + "Z"

    if isinstance(valor_fecha, str):
        texto_limpio = valor_fecha.strip().replace("/", "-")
        
        try:
            fecha_obj = datetime.strptime(texto_limpio, "%Y-%m-%d %H:%M:%S")
            return fecha_obj.isoformat() + "Z"
            
        except ValueError:
            try:
                fecha_obj = datetime.strptime(texto_limpio, "%Y-%m-%d")
                return fecha_obj.isoformat() + "Z"
                
            except ValueError:
                raise ValueError(f"Formato invalido. Formato valido: YYYY-MM-DD o YYYY-MM-DD HH:MM:SS")
    raise ValueError(f"Tipo de dato incorrecto: {type(valor_fecha).__name__}. Debe de ser Texto o Fecha: YYYY-MM-DD o YYYY-MM-DD HH:MM:SS ")