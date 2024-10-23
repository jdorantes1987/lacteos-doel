import os
import time
from io import BytesIO
import streamlit as st
import matplotlib.pyplot as plt
from helpers.navigation import make_sidebar
from scripts.conexion import ConexionBD
from scripts.cxc import CXC
from scripts.empresa import ClsEmpresa
from scripts.cxc import CXC

st.set_page_config(page_title='CXC', 
                   layout='wide', 
                   page_icon='⚡')

make_sidebar()
base_de_datos = os.getenv('DB_NAME_PROFIT_DOEL') if ClsEmpresa.modulo_seleccionado() =='DOEL' else os.getenv('DB_NAME_PROFIT_PANA')
conexion = ConexionBD(base_de_datos=base_de_datos)

# No se debe colocar @st.cache_data ya que existen Tipos de datos mixtos en las columnas de la tabla dinamica y produce error al cargar otros dataframes
def cuentas_por_cobrar_pivot(tipo_cliente):
    return CXC(conexion).cxc_clientes_resum_pivot(tipo_cliente=tipo_cliente)

@st.cache_data
def view_cxc():
    return CXC(conexion).view_cxc()

st.subheader("Reporte de cuentas por cobrar")
st.caption("""Desplagar y luego hacer click en ':blue[Archivo de CXC]' para descargar achivo Excel de cuentas por cobrar a la fecha.""")
with st.expander("mostrar"):
    tipo_cliente_select = st.selectbox('Elije un :blue[tipo de cliente]:',
                                      ['Comercios', 'Ruteros', 'Todos'], 
                                      0)

    tipo_cliente = tipo_cliente_select[0]
    datos = cuentas_por_cobrar_pivot(tipo_cliente=tipo_cliente)
    saldo_cxc = datos.sort_values(by=['All'], 
                                  ascending=False)
    cmap = plt.colormaps['summer']
    st.dataframe(
                saldo_cxc.style
                .format('{:,.2f}')
                .background_gradient(
                                    subset=['All'], 
                                    cmap=cmap),
            #  Permite ajustar el ancho al tamaño del contenedor    
                use_container_width=True
    )
    df_cxc = view_cxc()
    if tipo_cliente_select == 'T':
        df_cxc = df_cxc[df_cxc['tip_cli'] != '']
    else:
        df_cxc = df_cxc[df_cxc['tip_cli'] == tipo_cliente]
    df_cxc.to_excel(buf := BytesIO())
    st.download_button(
        'Archivo de CXC',
        buf.getvalue(),
        f'Cobranza {ClsEmpresa.modulo_seleccionado()}.xlsx',
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )