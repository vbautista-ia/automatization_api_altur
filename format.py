# import pandas as pd

# path = '../../reportes/'
# name_file = 'calls_multiple_campaigns'
# type_file = 'csv'
# file = f"{path}{name_file}.{type_file}"

# # 1. Cargar tu archivo consolidado
# df = pd.read_csv(file)

# # 2. Las etiquetas que vamos a buscar
# columnas_etiquetas = [
#     'PROMESA', 
#     'NO DEFINE', 
#     'FAMILIAR', 
#     'TERCERO', 
#     'EQUIVOCADO', 
#     'Screening iOS',  # Ojo aquí con las mayúsculas/minúsculas para que coincida con tu CSV
#     'CUELGA'
# ]

# # 3. La información principal que necesitas
# columnas_info = ['campaign_date', 'id']

# # 4. Filtrar las filas que tengan al menos un 'True' en las etiquetas
# filtro = df[columnas_etiquetas].any(axis=1)



# # Usamos .copy() para no modificar el DataFrame original y evitar advertencias
# df_filtrado = df.loc[filtro].copy()

# # 5. ¡LA MAGIA OCURRE AQUÍ!
# # idxmax(axis=1) busca el "True" de cada fila y extrae el nombre de esa columna
# df_filtrado['RESULTADO'] = df_filtrado[columnas_etiquetas].idxmax(axis=1)

# # 6. Seleccionamos solo las columnas de info y nuestra nueva columna RESULTADO
# # (Dejamos atrás las columnas de True/False porque ya no las necesitamos)
# columnas_finales = columnas_info + ['RESULTADO']
# df_final = df_filtrado[columnas_finales]

# # 7. ¡AQUÍ ORDENAMOS LOS REGISTROS!
# # Convertimos la columna a una "Categoría" y le pasamos tu lista como el orden oficial
# df_final['RESULTADO'] = pd.Categorical(
#     df_final['RESULTADO'], 
#     categories=columnas_etiquetas, 
#     ordered=True
# )

# # Ahora ordenamos: Primero por tu RESULTADO (en el orden de tu lista) y luego por fecha
# df_final = df_final.sort_values(by=['RESULTADO', 'campaign_date'])

# # 8. Exportar el resultado
# # df_final.to_csv('marcaciones_formato_limpio.csv', index=False)
# df_final.to_csv(path + 'marcaciones_filtradas.csv', index=False)



# # Agrupar por RESULTADO y tomar un máximo de los primeros 20 de cada grupo
# # df_muestra = df_final.groupby('RESULTADO').head(20)
# # Exportas esta muestra en lugar del completo
# # df_muestra.to_csv(path + 'muestra_20_marcaciones.csv', index=False)


# resumen_conteos = df_final['RESULTADO'].value_counts()
# print("\n--- RESUMEN DE MARCACIONES ---")
# print(resumen_conteos)

# print(f"¡Listo! Se procesaron {len(df_final)} registros.")
# print("\nMuestra de los primeros registros:")
# print(df_final.head())

import pandas as pd
import os

path = '../../reportes/'
name_file = 'calls_multiple_campaigns'
type_file = 'csv'
file = f"{path}{name_file}.{type_file}"
headers = ['campaign_name', 'campaign_date', 'id', 'contact', 'name', 
           'context', 'status', 'retries', 'calls', 'billed_duration', 'last_update']

# 1. Cargar tu archivo consolidado
df = pd.read_csv(file)

# 2. Las etiquetas que vamos a buscar
columnas_etiquetas = [
    'PROMESA'
]

# 3. La información principal que necesitas
columnas_info = ['id', 'campaign_date', 'FECHA PROMESA']

# 4. Filtrar las filas que tengan al menos un 'True' en las etiquetas
filtro = df[columnas_etiquetas].any(axis=1)

# Usamos .copy() para no modificar el DataFrame original y evitar advertencias
df_filtrado = df.loc[filtro].copy()

# 5. ¡LA MAGIA OCURRE AQUÍ!
# idxmax(axis=1) busca el "True" de cada fila y extrae el nombre de esa columna
# df_filtrado['RESULTADO'] = df_filtrado[columnas_etiquetas].idxmax(axis=1)

# 6. Seleccionamos solo las columnas de info y nuestra nueva columna RESULTADO
# columnas_finales = columnas_info + ['RESULTADO']
# AÑADIDO: .copy() para poder manipular las fechas de forma segura
# df_final = df_filtrado[columnas_finales].copy()
df_final = df_filtrado[columnas_info].copy()

# --- NUEVO: CONVERSIÓN Y EXTRACCIÓN DE MES ---
# Convertimos a formato datetime (usando el formato YYYY-MM-DD que me comentaste)
df_final['campaign_date'] = pd.to_datetime(df_final['campaign_date'], format='%Y-%m-%d')

# Extraemos el mes y le asignamos su nombre
meses_nombres = {3: 'Marzo', 4: 'Abril'}
# df_final['MES'] = df_final['campaign_date'].dt.month.map(meses_nombres)


# 7. ¡AQUÍ ORDENAMOS LOS REGISTROS!
# Convertimos la columna a una "Categoría" y le pasamos tu lista como el orden oficial
# df_final['RESULTADO'] = pd.Categorical(
#     df_final['RESULTADO'], 
#     categories=columnas_etiquetas, 
#     ordered=True
# )

# Ahora ordenamos: Primero por tu RESULTADO (en el orden de tu lista) y luego por fecha
# df_final = df_final.sort_values(by=['RESULTADO', 'campaign_date'])

# 8. Exportar el resultado
# df_final.to_csv('marcaciones_formato_limpio.csv', index=False)
# df_final.to_csv(path + 'marcaciones_filtradas.csv', index=False)

# Agrupar por RESULTADO y tomar un máximo de los primeros 20 de cada grupo
# df_muestra = df_final.groupby('RESULTADO').head(20)
# Exportas esta muestra en lugar del completo
# df_muestra.to_csv(path + 'muestra_20_marcaciones.csv', index=False)

# 8. Exportar el resultado (Modificado para no sobreescribir)
archivo_salida = path + 'marcaciones_filtradas_dos.csv'

if os.path.exists(archivo_salida):
    # Si ya existe: modo 'a' (append) y NO escribimos los encabezados de nuevo
    df_final.to_csv(archivo_salida, mode='a', header=False, index=False)
    print(f"\nSe AGREGARON {len(df_final)} registros al archivo existente.")
else:
    # Si no existe: modo 'w' (write, por defecto) y SÍ escribimos los encabezados
    df_final.to_csv(archivo_salida, mode='w', header=True, index=False)
    print(f"\nSe CREÓ el archivo con {len(df_final)} registros.")

# --- NUEVO: IMPRIMIR RESUMEN POR MES ---

print(f"Total de registros: {len(df)}")
print(f"\n¡Listo! Se procesaron {len(df_final)} registros.")
print("\nMuestra de los primeros registros:")
print(df_final.head())


# print(file.dtypes)

# print(file.head(0))
# file = file.drop(['campaign_name', 'campaign_date'], axis=1)


# print(content_separate)

# for index, data in enumerate(headers.split(',')):
#     if(content_separate[index] == 'True'):
#         print(data, content_separate[index], end='    ')