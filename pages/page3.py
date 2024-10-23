import os
import time
import streamlit as st
from helpers.navigation import make_sidebar
from scripts.conexion import ConexionBD
from scripts.devoluciones import Devoluciones
from scripts.consultas_generales import ConsultasGenerales
from scripts.empresa import ClsEmpresa

st.set_page_config(page_title='Gestión Ruteros', 
                   layout='wide', 
                   page_icon='⚡')

st.subheader("🎫 Notas de crédito")
make_sidebar()
empresa = os.getenv('DB_NAME_PROFIT_DOEL') if  ClsEmpresa.modulo_seleccionado() =='DOEL' else os.getenv('DB_NAME_PROFIT_PANA')
conexion = ConexionBD(base_de_datos=empresa)
devoluciones = Devoluciones(conexion=conexion)
consultas_generales = ConsultasGenerales(conexion)

@st.cache_data
def devoluciones_por_agregar():
    dev = devoluciones.resumen_pedidos(anio='all', mes='all')
    dev.rename(columns={'co_tran': 'cod_rutero', 'des_tran': 'descrip_rutero', 'doc_num': 'num_pedido'}, inplace=True)
    dev['total'] = dev['monto_base_item'] + dev['iva']
    return dev.groupby(['cod_rutero', 'descrip_rutero', 'co_cli', 'cli_des', 'num_pedido']).agg({'monto_base_item': 'sum', 
                                                                                                'iva': 'sum', 'iva': 'sum', 
                                                                                                'total': 'sum'}).reset_index()
if st.button("🔄 Refrescar"):
    st.cache_data.clear()
    st.session_state.devoluciones_por_agregar = devoluciones_por_agregar()

st.session_state.devoluciones_por_agregar = devoluciones_por_agregar()

if len(st.session_state.devoluciones_por_agregar) > 0:
    st.write("❇️ Abonos por aplicar")
    st.dataframe(st.session_state.devoluciones_por_agregar,
                use_container_width=False,
                hide_index=True,
                column_config={
                                "cod_rutero": st.column_config.TextColumn(
                                "rutero",
                            ),
                                "descrip_rutero": st.column_config.TextColumn(
                                "nombre rutero",
                            ),
                                "co_cli": st.column_config.TextColumn(
                                "cliente",
                            ),
                                "cli_des": st.column_config.TextColumn(
                                "razón social",
                            ),
                                "monto_base_item": st.column_config.NumberColumn(
                                "base imponible",
                                default=0,
                                format="$ %.2f",
                            ),
                                "iva": st.column_config.NumberColumn(
                                "IVA",
                                default=0,
                                format="$ %.2f",
                            ),
                                "total": st.column_config.NumberColumn(
                                "total pedido",
                                default=0,
                                format="$ %.2f",
                            )})

    if st.button("Aplicar"):
        devoluciones.procesar_devolucion(anio='all', mes='all')
        st.cache_data.clear()
        del st.session_state['devoluciones_por_agregar']
        st.success('Se ha procesado la devolución!')
        time.sleep(1)
        st.rerun()
else:
    st.warning("""No existen (N/C) notas de crédito pendientes por aplicar""")
st.caption("""Módulo para gestionar abonos a ruteros. Este proceso crea una devolución por cada Rutero según precio (02) de los pedidos asociados.""")