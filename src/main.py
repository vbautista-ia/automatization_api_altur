from datetime import datetime
import logging
import os
from fastapi import FastAPI
import pandas as pd

# from configuration.platforms import Platforms
# from service.call_assets_service import CallAssetsService
# from service.call_service import CallService
# from service.report_service import ReportService

from controller.report_controller import router as router_report 
from controller.campaign_controller import router as router_campaign 
from controller.call_controller import call_router

logging.basicConfig(
    level=logging.INFO, # Captura todos los mensajes (desde DEBUG hasta CRITICAL)
    # format='%(asctime)s - %(levelname)s - %(message)s' # Muestra fecha, nivel y texto
)

app = FastAPI()
app.include_router(router=router_report)
app.include_router(router=router_campaign)
app.include_router(router=call_router)


# callService = CallAssetsService(Platforms.BBVA_RETARGETING)

# calls = ['cll_oiQEmQocFKRPCxEXTXR8',
# 'cll_B6JIj6vhjkMDd1tyLN9h',
# 'cll_v6JHmEVA8JQLDe2X8jVg',
# 'cll_sBZjipnFM2AUXx5gd0zT',
# 'cll_QMZBM5PPeUux5p46LafR',
# 'cll_u8cu2GNghWGfQv8ds5Cc',
# 'cll_c50uUkknAfvnZGX1tswA',
# 'cll_t61gO7iHzWXOD6qcDuW8',
# ]

# callService.download_resourses_by_id_call(calls)

# call_service = CallService(Platforms.BBVA_COBRANZA)

##BUSCAR LLAMADAS
# df = pd.read_csv("../../llamadas_buscar_spc.csv", sep=",", dtype={'CUENTA': str})
# resultado = {}
# df['FECHA'] = pd.to_datetime(df['FECHA']).dt.strftime('%Y-%m-%d')
# for fecha, grupo in df.groupby('FECHA'):
    
#     # 3. Construimos la lista de diccionarios directamente iterando sobre el grupo
#     lista_cuentas = [{fila['CUENTA']: fila['HORA INICIO LLAMADA']} for _, fila in grupo.iterrows()]
    
#     # 4. Asignamos la lista a la llave de la fecha
#     resultado[fecha] = lista_cuentas
# # Mostramos el resultado final

# {'fecha': [{'el numero de cuenta': la fecha de inicio}, ]}

## DESCARGAR LLAMADAS
# resultado = {
#     '2026-05-24': [
#         {'007410027432684248': '18:14:33'},
#         {'007410409886831467': '19:23:10'}
#     ]
# }

# call_service.download_all_recording_by_account(resultado)



### CREACIÓN DE EXCEL con PANDAS ###
# report = ReportService(Platforms.BBVA_COBRANZA)
# result = report.get_total_accounts('COBRANZA_', '2026-07-08T00:00:00Z', '2026-07-08T23:59:59Z')

# if not result['total_cuentas']:
#     logging.info('Not found calls to accounts')
# else:
#     # Ejemplo de objeto en result
#     # {
#     #     'fecha': '2026-07-09',
#     #     'total_cuentas': {
#     #         'Agente 1': 42342, 
#     #         'Agente 2': 323
#     #         }
#     # }
#     tabla = {
#         'fecha': [],
#         'producto': [],
#         'total': []
#     }


#     for agente, total in result['total_cuentas'].items():
#         tabla['fecha'].append(result['fecha'])
#         tabla['producto'].append(agente)
#         tabla['total'].append(total)

#     df = pd.DataFrame(tabla)

#     file_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
#     path = os.path.join(Platforms.BBVA_COBRANZA.value)
#     os.makedirs(path, exist_ok=True)   
#     path = os.path.join(path, file_name)

#     df.to_excel(path, sheet_name='total_counts', index=False, engine="openpyxl")

#     logging.info('End search calls by accounts')




# report_service = ReportService(Platforms.BBVA_COBRANZA)

# accounts = ["007410027487145035", "007409609861147030", "007409609620796666", "007410027492391224"]
# # start = '04-07-2026 17:00:00'
# # end = '04-07-2026 18:59:59'
# # start = '04-07-2026 09:45:00'
# # end = '05-07-2026 20:30:00'
# start = '04-07-2026 08:00:00'
# end = '04-07-2026 20:00:00'
# agent_start = 'COBRANZA_'
# report_service.search_transaction_by_account(accounts, start, end, agent_start)
