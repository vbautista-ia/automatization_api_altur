import pandas as pd

file = pd.read_csv('../../Grabaciones_MIA_CC.csv', encoding='utf-8')

file = file.groupby('FECHA').apply(list).reset_index()
print(file.head())

