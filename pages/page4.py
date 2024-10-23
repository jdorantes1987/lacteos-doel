import os
import time
import streamlit as st
from helpers.navigation import make_sidebar
from scripts.conexion import ConexionBD
from scripts.stock import Stock
from scripts.update_all import UpdateAll
from scripts.cliientes import Clientes
from scripts.empresa import ClsEmpresa

st.set_page_config(page_title='Procesos Masivos', 
                   layout='wide', 
                   page_icon='⚡')

base_de_datos = os.getenv('DB_NAME_PROFIT_DOEL') if ClsEmpresa.modulo_seleccionado() =='DOEL' else os.getenv('DB_NAME_PROFIT_PANA')
conexion = ConexionBD(base_de_datos=base_de_datos)

st.subheader("🗂️ Stock inventario")
with st.expander("mostrar"):
    make_sidebar()
    if st.button("Actualizar Stock x almacen"):
        Stock(conexion).update_stock()
        st.success('Stock actualizado!')
        time.sleep(1)
        st.rerun()
st.caption("""Presione 'Actualizar' para recalcular el stock de artículos de inventario.""")

st.header("🗄️ Factura ventas")
with st.expander("mostrar"):
    col1, col2 = st.columns(2, 
                            gap="small")
    with col1:
        fecha_ini = st.date_input("fecha inicial").strftime('%Y%m%d %H:%M:%S') # Convierte la fecha a YYYYMMDD
    with col2:
        fecha_fin = st.date_input("fecha final").strftime('%Y%m%d 23:59:59') # Convierte la fecha a YYYYMMDD
    if st.button("Actualizar tasas facturas"):
        UpdateAll(conexion).agregar_info_tasa_facturas(fecha_ini=fecha_ini, fecha_fin=fecha_fin)
        st.success('Procesado!')
        time.sleep(1)
        st.rerun()
st.caption("""Presione 'Actualizar' para asignar la tasa de cambio de forma masiva a las facturas comprendidas entre el rango de fecha seleccionado.""")

descrip_modulo = ' de Distribuidora Panaraca' if ClsEmpresa.modulo_seleccionado() =='DOEL' else ' de Lácteos Doel'
st.subheader(f"👨‍🔧 Sincronizar con clientes {descrip_modulo}")
with st.expander("mostrar"):
    if st.button("Procesar"):
        o_clientes = Clientes(conexion)
        if ClsEmpresa.modulo_seleccionado() == 'DOEL':
            o_clientes.exe_sql_insert_cliente(o_clientes.clientes_por_sinc_doel())
        else:
            o_clientes.exe_sql_insert_cliente(o_clientes.clientes_por_sinc_pana())
        st.success('Clientes sincronizados!')
        time.sleep(1)
        st.rerun()