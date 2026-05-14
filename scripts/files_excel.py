from pandas import read_excel, to_datetime

p_data_estadisticas_bcv = (
    "./scripts/bcv/tasas_BCV.xlsx"  # ruta relativa, regresa a la carpeta anterior
)
p_data_estadisticas_bcv_datapy = "//10.100.104.1/AdministracionFinanzas/DESARROLLO_DataProfit/"  # ruta relativa, regresa a la carpeta anterior
p_data_estadisticas_par = "../bantel/accesos/excel/tasas_Par.xlsx"  # ruta relativa, regresa a la carpeta anterior
p_data_comprobantes_manuales = "C:/Users/jdorantes/Documents/Analisis/Desarrollos/DATA_COMPROBANTES_X_CONTABILIZAR.xlsx"
p_data_revision_contabilidad = (
    "C:/Users/jdorantes/Documents/Analisis/Revision Contabilidad.xlsm"
)
p_data_edo_cta_banesco = "C:/Users/jdorantes/Documents/Analisis/Estados de Cuenta/Banesco/2025/01. ENE/Banesco Enero 2025.xlsx"
p_data_insert_fact_y_recibos = (
    "X:/DESARROLLO_DataProfit/Planes Facturacion Clientes Izquierda.xlsx",
    "//10.100.104.1/AdministracionFinanzas/DESARROLLO_DataProfit/Planes Facturacion Clientes Derecha.xlsx",
)
p_data_iva_forma99030 = "C:/Users/jdorantes/Documents/Analisis/FORMAS 99030.xlsx"


def datos_estadisticas_tasas():
    hist_tc = read_excel(p_data_estadisticas_bcv)
    hist_tc["fecha"] = to_datetime(hist_tc["fecha"])
    hist_tc = hist_tc.drop(hist_tc.columns[0], axis=1).reset_index(
        drop=True
    )  # Elimina la primera columna del dataframe
    return hist_tc
