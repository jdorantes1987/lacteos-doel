from pandas import read_excel

path_file_tasas_bcv = './scripts/bcv/tasas_BCV.xlsx'

def historico_tasas_bcv():
    return read_excel(path_file_tasas_bcv)

def get_fecha_tasa_bcv_dia():
    df_data_bcv = historico_tasas_bcv()  # archivo BCV
    return df_data_bcv['fecha'].max()

def get_monto_tasa_bcv_dia():
    df_data_bcv = historico_tasas_bcv()  # archivo BCV
    fila_tasa_dia = df_data_bcv[df_data_bcv['fecha'] == df_data_bcv['fecha'].max()]
    return float(fila_tasa_dia['venta_ask2'].iloc[0])
