import ssl
from pandas import DataFrame
from pandas import concat
from pandas import to_datetime
import locale
import time
from urllib.request import build_opener, urlretrieve, urlcleanup
from xlrd import open_workbook
from scripts.bcv.data import path_file_tasas_bcv, historico_tasas_bcv

ssl._create_default_https_context = ssl._create_unverified_context

url_base = 'https://www.bcv.org.ve/sites/default/files/EstadisticasGeneral'
dic_year_files = {'2024': ['2_1_2d24_smc.xls', '2_1_2c24_smc.xls','2_1_2b24_smc.xls', '2_1_2a24_smc.xls'],
                  '2023': ['2_1_2d23_smc.xls', '2_1_2c23_smc.xls', '2_1_2c23_smc_60.xls', '2_1_2a23_smc.xls'],
                  '2022': ['2_1_2d22_smc.xls', '2_1_2c22_smc.xls', '2_1_2b22_smc.xls', '2_1_2a22_smc.xls'],
                  '2021': ['2_1_2d21_smc.xls', '2_1_2c21_smc.xls', '2_1_2b21_smc.xls', '2_1_2a21_smc_58.xls'],
                  '2020': ['2_1_2d20_smc.xls', '2_1_2c20_smc.xls', '2_1_2b20_smc.xls', '2_1_2a20_smc.xls']
                  }

# ACTUALIZA EL HISTÓRICO DE TASAS CON LA ÚLTIMA PUBLICACIÓN
def get_data_usd_bcv_web_last_qt():
    name_file_tasa_download = list(dic_year_files.values())[0][0]  # Convierte el diccionario en una lista y obtiene el primer elemento
    url = url_base + f'/{name_file_tasa_download}'
    #  cambiar el encabezado del agente de usuario
    opener = build_opener()
    #  agregar el encabezado de solicitud de agente de usuario
    opener.addheaders = [('User-Agent',
                          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36')]
    file_name = urlretrieve(url)
    print('Se descargó archivo de la ruta:', url)
    # Como el resultado de la descarga es una tuple con la información del archivo y el recurso de la web se coloca el indice [0] que es la del archivo
    wb = open_workbook(file_name[0], 
                       on_demand=True)  # Abre el libro de trabajo con el indicador "on_demand=True", para que las hojas no se carguen automáticamente.
    sheets = wb.sheet_names()
    cols = ['cod_mon', 'mon_pais', 'compra_bid', 'venta_ask', 'compra_bid2', 'venta_ask2']
    df_arr_sh = []
    for i in range(len(sheets)):
        sh = wb.sheet_by_index(i)
        # Creamos las listas
        filas = []
        for fila in range(11, 33):
            columnas = [sh.cell_value(fila, columna + 1) for columna in range(0, 6)]
            filas.append(columnas)
        df_base = DataFrame(filas, columns=cols)
        # extrae la fecha valor de la celda D5, hay que remover los espacios
        df_base['fecha'] = str(sh.cell_value(4, 3))[13:].replace('/', '').strip()
        # df_base['fecha'] = sh.name  # Anteriormente extraía la fecha del nombre de la hoja lo cual es incorrecto, ya que se debe tomar la fecha valor.
        df_base['fecha'] = to_datetime(df_base['fecha'], format='%d%m%Y')
        df_base['archivo'] = name_file_tasa_download
        df_arr_sh.append(df_base)
    data = concat(df_arr_sh, axis=0, ignore_index=True)
    data = data[data['cod_mon'] == 'USD']
    urlcleanup()
    # wb.release_resources()
    # del wb
    return data


# Actualiza el archivo tasas_BCV.xlsx
def actulizar_file_tasas():
    locale.setlocale(locale.LC_ALL, 'es_ES')
    df_file_tasa = historico_tasas_bcv()
    df_file_tasa_new = get_data_usd_bcv_web_last_qt()
    name_file_tasa_download = list(dic_year_files.values())[0][0]  # Obtiene el primer nombre de la lista de diccionario
    df_file_tasa_filtred = df_file_tasa[df_file_tasa['archivo'] != name_file_tasa_download]
    new_file_tasa = [df_file_tasa_new, df_file_tasa_filtred]
    df = concat(new_file_tasa).reset_index(drop=True)
    df['año'] = df['fecha'].dt.year
    df['mes'] = df['fecha'].dt.month
    df['dia'] = df['fecha'].dt.day
    df['mes_'] = df['fecha'].dt.month_name(locale='es_ES').str[:3]
    locale.setlocale(locale.LC_ALL, '')
    df['var_tasas'] = df['venta_ask2'].diff(
        periods=-1)  # Permite calcular la diferencia que existe entre el valor de la celda actual con respecto a la anterior
    df.to_excel(path_file_tasas_bcv)

