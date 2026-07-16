import pandas as pd
import requests
import os
from datetime import datetime

# --- 1. CONFIGURACIÓN DE CONTROL ---
META_POR_MES_Y_CAT = 20 # 20 de marzo y 20 de abril por cada categoría
INICIO_INDICE = 0
CATEGORIAS_A_DESCARGAR = [] # Vacío para todas

# --- 2. CONFIGURACIÓN DE API Y RUTAS ---
TOKEN = 'sk-M2Q6e7A0hFa23zZlYnpWFKSsYcWRVgucj'
URL_BASE = 'https://api.altur.io/api/v1.0/call/ID/recording'
path_grabaciones = '../../grabaciones/'
CARPETA_RAIZ = path_grabaciones + 'llamadas_hipotecario'

path_grabaciones
# --- 3. PROCESAMIENTO DE DATOS ---
path = '../../reportes/'
name_file = 'marcaciones_filtradas'
type_file = 'csv'
file = f"{path}{name_file}.{type_file}"

df = pd.read_csv(file)
# df = pd.read_csv('marcaciones_filtradas.csv')

# Convertir la fecha a formato datetime para extraer el mes fácilmente
# Ajustar el formato si tu CSV usa algo distinto a 'día/mes/año'
df['campaign_date'] = pd.to_datetime(df['campaign_date'], format='%Y-%m-%d')

# Crear una columna con el nombre del mes para organizar carpetas
meses_nombres = {3: 'Marzo', 4: 'Abril'}
df['MES_NOMBRE'] = df['campaign_date'].dt.month.map(meses_nombres)

# Filtrar solo marzo (3) y abril (4) y las categorías si se especificaron
df = df[df['campaign_date'].dt.month.isin([3, 4])]
if CATEGORIAS_A_DESCARGAR:
    df = df[df['RESULTADO'].isin(CATEGORIAS_A_DESCARGAR)]

conteo_final = {}

print(f"Iniciando descarga organizada: {META_POR_MES_Y_CAT} llamadas por Mes/Categoría.\n")

# --- 4. BUCLE DE DESCARGA ORGANIZADO ---
# Agrupamos por RESULTADO y por MES_NOMBRE
for (categoria, mes), grupo in df.groupby(['RESULTADO', 'MES_NOMBRE']):
    
    # Aplicar el paginado dentro de este grupo específico (ej: Promesas de Marzo)
    subgrupo = grupo.iloc[INICIO_INDICE : INICIO_INDICE + META_POR_MES_Y_CAT]
    
    if len(subgrupo) == 0:
        continue

    # Crear la estructura de carpetas: llamadas_hipotecario / CATEGORIA / MES
    ruta_directorio = os.path.join(CARPETA_RAIZ, str(categoria), str(mes))
    os.makedirs(ruta_directorio, exist_ok=True)

    print(f"--- {categoria} ({mes}): Descargando {len(subgrupo)} archivos ---")
    
    for _, fila in subgrupo.iterrows():
        id_llamada = fila['id']
        # Formato de fecha para el nombre del archivo: DD-MM-AAAA
        fecha_str = fila['campaign_date'].strftime('%d-%m-%Y')
        
        try:
            url = URL_BASE.replace('ID', id_llamada)
            response = requests.get(url, 
                                    headers={'Authorization': f'api-key {TOKEN}'}, 
                                    stream=True)
            
            if response.status_code == 200:
                nombre_archivo = f"{id_llamada}_{fecha_str}.wav"
                ruta_final = os.path.join(ruta_directorio, nombre_archivo)
                
                with open(ruta_final, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Guardar registro para el reporte final
                clave = f"{categoria} - {mes}"
                conteo_final[clave] = conteo_final.get(clave, 0) + 1
            else:
                response
                print(f"  ⚠️ Error API {response.status_code} en ID {id_llamada}")
                
        except Exception as e:
            print(f"  ❌ Error en ID {id_llamada}: {e}")

# --- 5. REPORTE FINAL ---
print("\n" + "="*40)
print("RESUMEN DE DESCARGAS POR MES")
print("="*40)
for item, total in conteo_final.items():
    status = "✅ COMPLETADO" if total >= META_POR_MES_Y_CAT else f"⚠️ FALTAN {META_POR_MES_Y_CAT - total}"
    print(f"{item.ljust(25)}: {total} archivos {status}")


