import os
import time
from io import BytesIO
from numpy import where
from scripts.utilidades import date_today
import matplotlib.pyplot as plt
import streamlit as st
from helpers.navigation import make_sidebar
from scripts.conexion import ConexionBD
from scripts.estado_cuenta_rutero import EstadoCuentaRutero
from scripts.consultas_generales import ConsultasGenerales
from scripts.ajustes import Ajustes
from scripts.add_doc import AddDocumento
from scripts.empresa import ClsEmpresa
from  user import usuarios


st.set_page_config(page_title='Ganancias Ruteros', 
                   layout='wide', 
                   page_icon='⚡')

make_sidebar()
empresa = os.getenv('DB_NAME_PROFIT_DOEL') if  ClsEmpresa.modulo_seleccionado() =='DOEL' else os.getenv('DB_NAME_PROFIT_PANA')
conexion = ConexionBD(base_de_datos=empresa)
estado_cuenta_rutero = EstadoCuentaRutero(conexion=conexion)

@st.cache_data
def data_ganacia_x_facturas(anio, mes):
    ganancias_aplicadas = set(Ajustes(conexion).ganancias_aplicadas()['nro_orig'])
    ganancias_hist = estado_cuenta_rutero.calculo_ganacia_por_factura_comercio_historica(anio=anio, mes=mes)
    ganancias_hist = ganancias_hist[~ganancias_hist['doc_num'].isin(ganancias_aplicadas)]
    ganancias_hist['fec_emis'] = ganancias_hist['fec_emis'].dt.normalize()
    group_ganancias_hist = ganancias_hist.groupby(['co_tran', 'co_cli', 'cli_des', 'doc_num', 'doc_num_dev', 'fec_emis']).agg({'ganancia':'sum'}).reset_index()
    return group_ganancias_hist

st.header("Ganancias por aplicar a Ruteros")
st.caption("""Módulo para aplicar ganancia a Ruteros una vez realizado el :orange[cobro total] de cada factura de comercios.""")
data_ganancia_x_factura = data_ganacia_x_facturas(anio='all', mes='all')[['co_tran', 'co_cli', 'cli_des', 'doc_num', 'fec_emis', 'doc_num_dev', 'ganancia']]
data_ganancia_x_factura.insert(0, "sel", False)
cmap = plt.colormaps['summer']
#resumen_movimientos.style.format({"saldo": "${:,.2f}"})
df_style = data_ganancia_x_factura.style.format({'ganancia': '{:,.2f}'},precision=2).background_gradient(cmap=cmap, subset=['ganancia'], axis=None)
editor_resumen_mov = st.data_editor(df_style,
                                column_config={
                                        "co_tran": st.column_config.TextColumn(
                                        "ruta",
                                         width='small',
                                        ),
                                        "co_cli": st.column_config.TextColumn(
                                        "cliente",
                                         width='small',
                                        ),
                                        "cli_des": st.column_config.TextColumn(
                                        "razón social",
                                        width='medium',
                                        ),
                                        "doc_num": st.column_config.NumberColumn(
                                        "doc. num.",
                                        width='small',
                                        ),
                                        "doc_num_dev": st.column_config.TextColumn(
                                        "num. dev.",
                                        width='small',
                                        ),
                                        "fec_emis": st.column_config.DateColumn(
                                        "fecha",
                                        width='small',
                                        format="DD-MM-YYYY")},
                                use_container_width=True,
                                disabled=["co_tran", "des_tran", "doc_num", "doc_num_dev", "ganancia"],
                                hide_index=True)

selected_facturas = list(where(editor_resumen_mov.sel)[0])
selected_rows = data_ganancia_x_factura[editor_resumen_mov.sel].copy()
if len(selected_rows) > 0 :
    mov_x_aplicar = st.dataframe(selected_rows,
                                use_container_width=True,
                                hide_index=True)
    
    if st.button("Aplicar ganancia"):
        agregar_doc = AddDocumento(conexion)
        hoy = date_today().strftime('%Y%m%d %H:%M:%S') # Convierte la fecha a YYYYMMDD
        ult_num_ajnm = int(ConsultasGenerales(conexion).get_last__nro_ajuste_negativo()) 
        i = 0
        user = usuarios.ClsUsuarios.id_usuario()
        for index, row in selected_rows.iterrows():
            i += 1
            num_ajnm = str(ult_num_ajnm + i).zfill(10)
            agregar_doc.exe_sql_insert_doc('AJNM', 
                                           num_ajnm,
                                           f'Aplicacion ganancia s/fact {row['doc_num']}',
                                           row['co_tran'],
                                           'GNR',
                                           f'{hoy}',
                                           f'{hoy}',
                                           row['ganancia'],
                                           0,
                                           row['ganancia'],
                                           '',
                                           '',
                                           user,
                                           'APS',
                                           'FACT',
                                           row['doc_num'])
        agregar_doc.confirmar_transaccion()
        st.success('Ganancia aplicada con exito!')
        st.cache_data.clear()
        time.sleep(1)
        st.rerun()
        
if st.button("🔄 Refrescar"):
    st.cache_data.clear()
    st.rerun()
    
    
    
