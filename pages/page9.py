import os
from io import BytesIO
from numpy import where
from pandas import to_datetime
import matplotlib.pyplot as plt
import streamlit as st
from helpers.navigation import make_sidebar
from scripts.conexion import ConexionBD
from scripts.estado_cuenta_rutero import EstadoCuentaRutero
from scripts.ajustes import Ajustes
from scripts.empresa import ClsEmpresa
from scripts.cobros import Cobros



st.set_page_config(page_title='Edo. Cta. Rutero', 
                   layout='wide', 
                   page_icon='⚡')

make_sidebar()
empresa = os.getenv('DB_NAME_PROFIT_DOEL') if  ClsEmpresa.modulo_seleccionado() =='DOEL' else os.getenv('DB_NAME_PROFIT_PANA')
conexion = ConexionBD(base_de_datos=empresa)
estado_cuenta_rutero = EstadoCuentaRutero(conexion=conexion)
ajustes = Ajustes(conexion=conexion)
cobros = Cobros(conexion=conexion)

@st.cache_data
def resumen_movimientos_cuenta_ruteros(anio, mes):
    return estado_cuenta_rutero.resumen_movimiento_cuenta(anio=anio, mes=mes)

@st.cache_data
def movimiento_cuenta_rutero_x_dia(anio, mes):
    return estado_cuenta_rutero.movimiento_cuenta_rutero_x_dia(anio=anio, mes=mes)

@st.cache_data
def mov_facturas_directas(anio, mes):
    mov_fact = estado_cuenta_rutero.resumen_facturas_rutero(anio=anio, mes=mes)
    if len(mov_fact) > 0 :
        mov_fact = mov_fact.sort_values(by=['fec_emis'], ascending=[False])
        mov_fact['fec_emis'] = mov_fact['fec_emis'].dt.strftime('%d-%m-%Y')
    return mov_fact

@st.cache_data
def mov_facturas_comercios(anio, mes):
    mov_fact_comercio = estado_cuenta_rutero.calculo_ganacia_por_factura_comercio(anio=anio, mes=mes)
    if len(mov_fact_comercio) > 0 :
        mov_fact_comercio = mov_fact_comercio.sort_values(by=['fec_emis'], ascending=[False])
        mov_fact_comercio['fec_emis'] = mov_fact_comercio['fec_emis'].dt.strftime('%d-%m-%Y')
    return mov_fact_comercio

@st.cache_data
def movimientos_nota_entrega_rutero(anio, mes):
    notas_entrega = estado_cuenta_rutero.resumen_nota_entrega_rutero(anio=anio, mes=mes)
    if len(notas_entrega) > 0 :
        notas_entrega = notas_entrega.sort_values(by=['fec_emis'], ascending=[False])
        notas_entrega['fec_emis'] = notas_entrega['fec_emis'].dt.strftime('%d-%m-%Y')
        notas_entrega.rename(columns={'total_item':'total_ne'}, inplace=True)
    return notas_entrega

@st.cache_data
def movimientos_ajustes(anio, mes):
    ajustes_rutero = ajustes.documentos_ajustes(anio=anio, mes=mes)
    if len(ajustes_rutero) > 0 :
        ajustes_rutero = ajustes_rutero.sort_values(by=['fec_emis'], ascending=[False])
        ajustes_rutero['fec_emis'] = ajustes_rutero['fec_emis'].dt.strftime('%d-%m-%Y')
    return ajustes_rutero

@st.cache_data
def movimientos_ganancias_aplicadas():
    ganancias_aplicadas = ajustes.ganancias_aplicadas()
    if len(ganancias_aplicadas) > 0 :
        ganancias_aplicadas = ganancias_aplicadas.sort_values(by=['fec_emis'], ascending=[False])
        ganancias_aplicadas['fec_emis'] = ganancias_aplicadas['fec_emis'].dt.strftime('%d-%m-%Y')
    return ganancias_aplicadas

@st.cache_data
def movimientos_cobros():
    cobros_ruta = cobros.view_cobros_x_cliente()
    if len(cobros_ruta) > 0 :
        cobros_ruta = cobros_ruta[cobros_ruta['tip_cli'] == 'R']
        cobros_ruta = cobros_ruta.sort_values(by=['fecha'], ascending=[False])
        cobros_ruta['fecha'] = cobros_ruta['fecha'].dt.strftime('%d-%m-%Y')
    return cobros_ruta

if 'rutero_selected' not in st.session_state:
    st.session_state.rutero_selected = ""
    st.session_state.rutero_selected_name = ""
    st.session_state.rutero_selected_saldo = 0.0

mov_ruta = resumen_movimientos_cuenta_ruteros(anio='all', mes='all')[['co_cli', 'cli_des', 'saldo']]
st.header("Cuenta de Facturación")

col1, col2 = st.columns(2) 
with col1:
    st.metric(
                label ='Total saldos a la fecha', 
                value='{:,.2f}'.format(mov_ruta['saldo'].sum())
            )

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["Resumen", "Movimientos", "Notas de entrega", "Facturas directas", "Factura comercios", "Gcias. aplicadas", "Ajustes", "Cobros"])
with tab1:
    st.markdown('''
    :blue[Resumen del saldo general por rutero].''')
    resumen_movimientos = mov_ruta.sort_values(by='saldo', ascending=False)
    # Inserta columna llamada 'Select'
    resumen_movimientos.insert(0, "sel", False)
    cmap = plt.colormaps['summer']
    #resumen_movimientos.style.format({"saldo": "${:,.2f}"})
    df_style = resumen_movimientos.style.format({'saldo': '{:,.2f}'},precision=2).background_gradient(cmap=cmap, subset=['saldo'], axis=None)
    editor_resumen_mov = st.data_editor(df_style,
                                        column_config={ 
                                                        "co_cli": st.column_config.TextColumn(
                                                        "cod. rutero",
                                                        width='small',
                                                        ),
                                                        "cli_des": st.column_config.TextColumn(
                                                        "nombre",
                                                        width='large',
                                                        )},
                                        use_container_width=False,
                                        disabled=["co_cli", "cli_des", "saldo"],
                                        hide_index=True)
    selected_ruteros = list(where(editor_resumen_mov.sel)[0])
    selected_rows = resumen_movimientos[editor_resumen_mov.sel]
    if len(selected_rows) > 0 :
         st.session_state.rutero_selected = selected_rows['co_cli'].unique()[0]
         st.session_state.rutero_selected_name = selected_rows['cli_des'].unique()[0]
         st.session_state.rutero_selected_saldo = selected_rows['saldo'].unique()[0]
    else:
        st.session_state.rutero_selected = ""
    
    editor_resumen_mov.to_excel(buf := BytesIO())
    st.download_button(
        'Descargar',
        buf.getvalue(),
        f'Resumen estado de cuenta Rutero {ClsEmpresa.modulo_seleccionado()}.xlsx',
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",)
    
    if st.button("🔄 Refrescar"):
        st.cache_data.clear()
        st.rerun()

if len(selected_rows) > 0 :
    with tab2:
        st.markdown('''
        :blue[Detalle del movimiento de la cuenta de facturación].''')
        movimiento_x_dia = movimiento_cuenta_rutero_x_dia(anio='all', mes='all')
        col3, col4, col5 = st.columns((0.5, 3, 1))
        with col3:
            st.subheader(st.session_state.rutero_selected)
        with col4:
            st.subheader(st.session_state.rutero_selected_name)  
        with col5:   
            st.metric(
                    label ='Saldo rutero', 
                    value='{:,.2f}'.format(float(st.session_state.rutero_selected_saldo))
            )
            
        if len(movimiento_x_dia) > 0:
            mov_filtrados_x_rutero = movimiento_x_dia[movimiento_x_dia['co_cli'].isin(selected_rows['co_cli'])].copy() 
            mov_filtrados_x_rutero['saldo'] = mov_filtrados_x_rutero['total_ne'] + mov_filtrados_x_rutero['total_fd'] - mov_filtrados_x_rutero['total_fcp2'] + mov_filtrados_x_rutero['total_ajust'] - mov_filtrados_x_rutero['total_cobro'] - mov_filtrados_x_rutero['total_ganancia'] - mov_filtrados_x_rutero['total_fondo']
            mov_filtrados_x_rutero['fec_emis'] = mov_filtrados_x_rutero['fec_emis'].dt.strftime('%d-%m-%Y')
            mov_filtrados_x_rutero['saldo final'] = mov_filtrados_x_rutero['saldo'].cumsum()
            mov_filtrados_x_rutero.drop(columns=['saldo'], inplace=True)
            resumen_movimientos_style = mov_filtrados_x_rutero.style.format({
                                                                            'total_ne': '{:,.2f}', 
                                                                            'saldo final': '{:,.2f}',
                                                                            'total_fd': '{:,.2f}',
                                                                            'total_fcp2': '{:,.2f}',
                                                                            'total_ajust': '{:,.2f}',
                                                                            'total_cobro':'{:,.2f}',
                                                                            'total_ganancia':'{:,.2f}',
                                                                            'total_fondo':'{:,.2f}',
                                                                            'saldo final': '{:,.2f}'},
                                                                            precision=2)
            mov_rut = st.dataframe(resumen_movimientos_style,
                                                column_config={
                                                    "fec_emis":st.column_config.TextColumn(
                                                    "fecha",
                                                    width='small',
                                                    ),
                                                    "fec_mid": st.column_config.TextColumn(
                                                    "día",
                                                    width='small',
                                                    ),
                                                    "co_cli": st.column_config.TextColumn(
                                                    "ruta",
                                                    ),
                                                    "cli_des": st.column_config.TextColumn(
                                                    "razón social",
                                                    width='medium',
                                                    ),
                                                    "total_ne": st.column_config.NumberColumn(
                                                    "n. entrega",
                                                    width='small',
                                                    ),
                                                    "total_fd": st.column_config.NumberColumn(
                                                    "f. directa",
                                                    width='small',
                                                    ),
                                                    "total_fcp2": st.column_config.NumberColumn(
                                                    "f. comerc.",
                                                    width='small',
                                                    ),
                                                    "total_ajust": st.column_config.NumberColumn(
                                                    "ajustes",
                                                    width='small',
                                                    ),
                                                    "total_cobro": st.column_config.NumberColumn(
                                                    "cobros",
                                                    width='small',
                                                    ),
                                                    "total_ganancia": st.column_config.NumberColumn(
                                                    "gncia/apl",
                                                    width='small',
                                                    ),
                                                    "total_fondo": st.column_config.NumberColumn(
                                                    "fdo. garant.",
                                                    width='small',
                                                    ),
                                                    "saldo final": st.column_config.NumberColumn(
                                                    "saldo final",
                                                    width='small',
                                                    )},
                                                use_container_width=True,
                                                hide_index=True)
            mov_filtrados_x_rutero.to_excel(buf := BytesIO())
            st.download_button(
            'Descargar',
            buf.getvalue(),
            f'Movimientos estado de cuenta Rutero {ClsEmpresa.modulo_seleccionado()}.xlsx',
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",)
            
    with tab3:
        st.markdown('''
        :blue[Movimientos notas de entrega por rutero].''')
        movimientos_ne = movimientos_nota_entrega_rutero(anio='all', mes='all')
        movimientos_ne = movimientos_ne[movimientos_ne['co_cli'] == st.session_state.rutero_selected]
        movimientos_ne = movimientos_ne.style.format({'total_ne': '{:,.2f}'}, precision=2)
        st.dataframe(movimientos_ne,
                    column_config={
                                    "co_cli": st.column_config.TextColumn(
                                    "rutero",
                                        width='small',
                                    ),
                                    "cli_des": st.column_config.TextColumn(
                                    "razón social",
                                    width='large',
                                    ),
                                    "doc_num": st.column_config.TextColumn(
                                    "número doc.",
                                    width='small',
                                    ),
                                    "fec_emis": st.column_config.TextColumn(
                                    "fecha",
                                    width='small')},
                    use_container_width=False,
                    hide_index=True)
        
    with tab4:
        st.markdown('''
        :blue[Facturas emitidas a ruteros].''')
        mov_facturas = mov_facturas_directas(anio='all', mes='all')[['co_cli', 'cli_des', 'doc_num', 'fec_emis', 'total_item']]
        mov_facturas = mov_facturas[mov_facturas['co_cli'] == st.session_state.rutero_selected]
        mov_facturas = mov_facturas.style.format({'total_item': '{:,.2f}'}, precision=2)
        st.dataframe(mov_facturas,
                    column_config={
                                    "co_cli": st.column_config.TextColumn(
                                    "rutero",
                                        width='small',
                                    ),
                                    "cli_des": st.column_config.TextColumn(
                                    "razón social",
                                    width='large',
                                    ),
                                    "doc_num": st.column_config.TextColumn(
                                    "número fact.",
                                    width='small',
                                    ),
                                    "fec_emis": st.column_config.TextColumn(
                                    "fecha",
                                    width='small')},
                    use_container_width=False,
                    hide_index=True)

    with tab5:
        st.markdown('''
        :blue[Facturas comercios aplicadas a rutero].''')
        facturas_comercios_ruteros = mov_facturas_comercios(anio='all', mes='all')
        facturas_comercios_ruteros = facturas_comercios_ruteros.groupby(['co_cli_t1', 'co_tran', 'fec_emis', 'cli_des', 'doc_num_t1'], sort=False).agg({'total_item_precio_2':'sum'}).reset_index()
        facturas_comercios_ruteros.rename(columns={'co_tran':'ruta', 'co_cli_t1':'co_cli', 'total_item_precio_2':'total_fact.'}, inplace=True)
        facturas_comercios_ruteros = facturas_comercios_ruteros[facturas_comercios_ruteros['ruta'] == st.session_state.rutero_selected]
        facturas_comercios_ruteros = facturas_comercios_ruteros.style.format({'total_fact.': '{:,.2f}'}, precision=2)
        st.dataframe(facturas_comercios_ruteros,
                    column_config={
                                    "co_cli": st.column_config.TextColumn(
                                    "cod. cliente",
                                        width='small',
                                    ),
                                    "cli_des": st.column_config.TextColumn(
                                    "razón social",
                                    width='large',
                                    ),
                                    "doc_num_t1": st.column_config.TextColumn(
                                    "número fact.",
                                    width='small',
                                    ),
                                    "fec_emis": st.column_config.TextColumn(
                                    "fecha",
                                    width='small')},
                    use_container_width=False,
                    hide_index=True)
        
    with tab6:
        st.markdown('''
        :blue[Ganancias aplicadas sobre facturas de comercios precio dos].''')
        ganancias_aplicadas = movimientos_ganancias_aplicadas()[['co_cli', 'co_tipo_doc', 'fec_emis', 'nro_doc', 'nro_orig', 'total_neto']]
        ganancias_aplicadas = ganancias_aplicadas[ganancias_aplicadas['co_cli'] == st.session_state.rutero_selected]
        st.metric(
                label ='Total ganancias aplicadas', 
                value='{:,.2f}'.format(ganancias_aplicadas['total_neto'].sum())
            )
        ganancias_aplicadas = ganancias_aplicadas.style.format({'total_neto.': '{:,.2f}'}, precision=2)
        st.dataframe(ganancias_aplicadas,
                    column_config={
                                    "co_cli": st.column_config.TextColumn(
                                    "cod. cliente",
                                        width='small',
                                    ),
                                    "nro_doc": st.column_config.TextColumn(
                                    "doc. ajuste",
                                    width='small',
                                    ),
                                    "nro_orig": st.column_config.TextColumn(
                                    "número fact.",
                                    width='small',
                                    ),
                                    "co_tipo_doc": st.column_config.TextColumn(
                                    "tipo doc.",
                                    width='small',
                                    ),
                                    "fec_emis": st.column_config.TextColumn(
                                    "fecha",
                                    width='small')},
                    use_container_width=False,
                    hide_index=True)  
        
    with tab7:
        st.markdown('''
        :blue[Ajustes aplicados al rutero].''')
        ajustes_rutero = movimientos_ajustes(anio='all', mes='all')
        ajustes_rutero = ajustes_rutero[(ajustes_rutero['tip_cli'] == 'R') & (~ajustes_rutero['co_tipo_doc'].isin(['IVAN', 'AJPA', 'AJNA'])) & (ajustes_rutero['co_cta_ingr_egr'] != 'APS')].copy()
        ajustes_rutero = ajustes_rutero.groupby(['co_tipo_doc', 'co_cli', 'cli_des', 'doc_num', 'fec_emis']).agg({'total_neto':'sum'}).reset_index()
        ajustes_rutero.rename(columns={'total_neto':'total_ajust'}, inplace=True)
        ajustes_rutero = ajustes_rutero[ajustes_rutero['co_cli'] == st.session_state.rutero_selected]
        ajustes_rutero = ajustes_rutero.style.format({'total_ajust': '{:,.2f}'}, precision=2)
        st.dataframe(ajustes_rutero,
                    column_config={
                                    "co_cli": st.column_config.TextColumn(
                                    "ruta",
                                        width='small',
                                    ),
                                    "cli_des": st.column_config.TextColumn(
                                    "razón social",
                                    width='large',
                                    ),
                                    "doc_num": st.column_config.TextColumn(
                                    "número ajuste",
                                    width='small',
                                    ),
                                    "co_tipo_doc": st.column_config.TextColumn(
                                    "tipo ajuste.",
                                    width='small',
                                    ),
                                    "fec_emis": st.column_config.TextColumn(
                                    "fecha",
                                    width='small')},
                    use_container_width=False,
                    hide_index=True)
        
    with tab8:
        st.markdown('''
        :blue[Cobros realizados a rutero].''')
        cobros_rutero = movimientos_cobros()
        cobros_rutero = cobros_rutero[cobros_rutero['tip_cli'] == 'R']
        cobros_rutero = cobros_rutero.groupby(['co_cli', 'cli_des', 'co_tipo_doc', 'cob_num', 'fecha', 'nro_doc'], sort=False).agg({'cargo':'sum'}).reset_index()
        cobros_rutero.rename(columns={'fecha':'fec_emis', 'cargo':'total_cobro'}, inplace=True)
        cobros_rutero = cobros_rutero[cobros_rutero['co_cli'] == st.session_state.rutero_selected]
        st.metric(
                    label ='Total cobros', 
                    value='{:,.2f}'.format(cobros_rutero['total_cobro'].sum())
                )
        cobros_rutero = cobros_rutero.style.format({'total_cobro': '{:,.2f}'}, precision=2)
        st.dataframe(cobros_rutero,
                    column_config={
                                    "co_cli": st.column_config.TextColumn(
                                    "ruta",
                                        width='small',
                                    ),
                                    "cli_des": st.column_config.TextColumn(
                                    "razón social",
                                    width='large',
                                    ),
                                    "co_tipo_doc": st.column_config.TextColumn(
                                    "tipo doc.",
                                    width='small',
                                    ),
                                    "cob_num": st.column_config.TextColumn(
                                    "núm. cobro",
                                    width='small',
                                    ),
                                    "nro_doc": st.column_config.TextColumn(
                                    "núm. doc",
                                    width='small',
                                    ),
                                    "fec_emis": st.column_config.TextColumn(
                                    "fecha",
                                    width='small')},
                    use_container_width=False,
                    hide_index=True)    