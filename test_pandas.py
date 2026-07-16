import pandas as pd

# cuenta	fecha	inicio_llamada	fin_llamada	tmo	resultado
# 007410027492391224	2026-07-06	9:59:05	9:59:29	24	TRANSFERENCIA
file = pd.read_excel('tests.xlsx')

file['inicio'] = pd.to_datetime(file['fecha'].astype(str) + ' ' + '00:00:00')
file['fin'] = pd.to_datetime(file['fecha'].astype(str) + ' ' + '23:59:59')

file['fecha_inicio_completa'] = pd.to_datetime(file['fecha'].astype(str) + ' ' + file['inicio_llamada'].astype(str))
file['fecha_fin_completa'] = pd.to_datetime(file['fecha'].astype(str) + ' ' + file['fin_llamada'].astype(str))
file['cuenta'] = file['cuenta'].astype(str)

file_resumen = file.groupby('fecha').agg(
    fecha_primer_llamada=('fecha_inicio_completa', 'min'),
    fecha_ultima_llamada=('fecha_fin_completa', 'max'),
    inicio=('inicio', 'first'),
    fin=('fin', 'first'),
    cuentas=('cuenta', lambda x: list(x.unique()))
).reset_index()

file_resumen['fecha_primer_llamada'] = file_resumen['fecha_primer_llamada'].dt.strftime('%Y-%m-%dT%H:%M:%S')
file_resumen['fecha_ultima_llamada'] = file_resumen['fecha_ultima_llamada'].dt.strftime('%Y-%m-%dT%H:%M:%S')
file_resumen['inicio'] = file_resumen['inicio'].dt.strftime('%Y-%m-%dT%H:%M:%S')
file_resumen['fin'] = file_resumen['fin'].dt.strftime('%Y-%m-%dT%H:%M:%S')

# 5. Convertir el DataFrame final a la lista de diccionarios que buscas
accounts = file_resumen[['inicio', 'fin', 'fecha_primer_llamada', 'fecha_ultima_llamada', 'cuentas']].to_dict('records')
# ---- Ver el resultado ----
import json
print(json.dumps(accounts, indent=4))