import os
import time
import streamlit as st
from helpers.navigation import make_sidebar
from scripts.notas_entrega_cxc import NotasEntregaACxc
from scripts.conexion import ConexionBD
from scripts.empresa import ClsEmpresa

st.set_page_config(page_title='Notas de Entrega', 
                   layout='wide', 
                   page_icon='⚡')

st.subheader("Procesos especiales")
empresa = os.getenv('DB_NAME_PROFIT_DOEL') if  ClsEmpresa.modulo_seleccionado() =='DOEL' else os.getenv('DB_NAME_PROFIT_PANA')
conexion = ConexionBD(base_de_datos=empresa)
make_sidebar()
notas = NotasEntregaACxc(conexion)

@st.cache_data
def notas_entrega_por_agregar():
    return notas.df_notas_de_entrega_por_agregar()[['fec_emis', 'doc_num', 'co_cli', 'cli_des', 'n_control', 'descrip', 'total_bruto', 'monto_imp', 'total_neto']]
    
st.session_state.notas = notas_entrega_por_agregar()   
if st.button("🔄 Refrescar"):
    st.cache_data.clear()
    st.session_state.notas = notas_entrega_por_agregar()   
st.markdown("---")
if len(st.session_state.notas): 
    st.write('❇️ Notas de entrega')
    st.session_state.notas['fec_emis'] = st.session_state.notas['fec_emis'].dt.date
    st.session_state.notas['total_bruto'] = st.session_state.notas['total_bruto'].apply('{:,.2f}'.format)
    st.session_state.notas['monto_imp'] = st.session_state.notas['monto_imp'].apply('{:,.2f}'.format)
    st.session_state.notas['total_neto'] = st.session_state.notas['total_neto'].apply('{:,.2f}'.format)
    st.dataframe(st.session_state.notas,
               use_container_width=False,
                hide_index=True,
                column_config={"fec_emis": st.column_config.DateColumn(
                                "fecha",
                                format="DD-MM-YYYY")})
    if st.button("agregar a Cxc"):
        notas.agregar_notas_entrega_a_cxc()
        st.cache_data.clear()
        del st.session_state['notas']
        st.success('Se ha actualizado el saldo de las notas de entregar!')
        time.sleep(2)
        st.rerun()
else:
    st.warning("""No existen notas de entrega pendientes por agregar a CXC""")
st.caption("""Módulo para convertir notas de entrega en documentos por cobrar.""")