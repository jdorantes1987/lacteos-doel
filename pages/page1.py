import os
import time
from io import BytesIO
import altair as alt 
from multiprocessing import Process, Queue
from datetime import datetime, date

import streamlit as st
import plotly.graph_objects as go

from helpers.navigation import make_sidebar
from scripts.bcv.data import get_fecha_tasa_bcv_dia, get_monto_tasa_bcv_dia
from scripts.bcv.data import historico_tasas_bcv, path_file_tasas_bcv
from scripts.bcv.bcv_estadisticas_tasas import actulizar_file_tasas, actulizar_file_tasas_manual
from scripts.empresa import ClsEmpresa

st.set_page_config(page_title='Inicio', 
                   layout='wide', 
                   page_icon='⚡')

t1, t2 = st.columns((3,5)) 
t1.image('./images/logo.png')
titulo_empresa = 'Lácteos Doel' if ClsEmpresa.modulo_seleccionado() =='DOEL' else 'Distribuidora Panaraca'
t2.title(titulo_empresa)
st.markdown("---")
st.write('Información BCV')
def archivo_xlsx_bcv_actualizado():
    # obtiene la última fecha de modificación.
    modTimesinceEpoc = os.path.getmtime(path_file_tasas_bcv)
    hoy = date.today()
    fecha_modificacion = datetime.fromtimestamp(modTimesinceEpoc).date()
    archivo_actualizado = hoy == fecha_modificacion
    return archivo_actualizado

def update_file(tasks_to_accomplish, tasks_that_are_done):
      update_f = actulizar_file_tasas()
      if update_f:
        tasks_that_are_done.put(True)
      else:
        tasks_that_are_done.put(False)

def update_tasa_bcv():
    tasks_to_accomplish = Queue()
    tasks_that_are_done = Queue()
    p = Process(target=update_file,args=(tasks_to_accomplish, tasks_that_are_done))
    p.start()
    p.join()
    return tasks_that_are_done.get()
          

def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def tasa_manual(fecha, valor):
   actulizar_file_tasas_manual(fecha=fecha, valor_tasa=valor)

if __name__ == '__main__':
    date_t = datetime.strptime(str(get_fecha_tasa_bcv_dia().date()), '%Y-%m-%d')
    table_scorecard = """
    <div class="ui five small statistics">
      <div class="grey statistic">
        <div class="value">"""+str(get_monto_tasa_bcv_dia())+"""
        </div>
        <div class="grey label">
          Tasa BCV
        </div>
      </div>
      <div class="grey statistic">
        <div class="value">""" + date_t.strftime('%d-%m-%Y') +  """
        </div>
        <div class="grey label">
          Fecha valor tasa BCV
        </div>
      </div>
      """
    st.markdown(table_scorecard, unsafe_allow_html=True)
    local_css("files/style.css")
    make_sidebar()
    if not archivo_xlsx_bcv_actualizado():
      if update_tasa_bcv():
        st.info('Tasa BCV actualizada!')
        time.sleep(0.5)
      else:
        st.warning('No se pudo actualizar el archivo de histórico de tasas BCV')
        fecha = st.date_input("fecha de la tasa", disabled=True).strftime('%Y%m%d') # Convierte la fecha a YYYYMMDD
        valor = st.number_input('Ingrese el valor de la tasa', format="%.5f")
        if st.button("Deseas actualizar la tasa de forma manual?",  on_click=tasa_manual, args=(fecha, valor)):
          st.info('Tasa BCV actualizada!')
      st.rerun()

with st.expander("Evolución tasa BCV"):
     historico_tasa = historico_tasas_bcv()
     df = historico_tasa[historico_tasa['año'] == date.today().year]
     fig = go.Figure()
     fig = fig.add_trace(go.Scatter(x=df["fecha"].dt.normalize(),
                                y=df["venta_ask2"],
                                text="Tasa",))
     fig.update_traces(textposition="bottom right")
     fig.update_layout(
        title="Histórico de tasas BCV",
        plot_bgcolor="#E6F1F6",
     )
     fig.update_xaxes(nticks=13)
     st.plotly_chart(fig, 
                    use_container_width=True)

with st.expander("Histórico de tasas"):
     st.dataframe(historico_tasa[['cod_mon', 'fecha', 'compra_bid2', 'venta_ask2', 'var_tasas']],
                column_config={
                                "cod_mon": st.column_config.TextColumn(
                                "moneda",
                                ),
                                "compra_bid2": st.column_config.NumberColumn(
                                "compra",
                                format="%.4f",
                                ),
                                "venta_ask2": st.column_config.NumberColumn(
                                "venta",
                                format="%.4f",
                                ),
                                "var_tasas": st.column_config.NumberColumn(
                                "variación",
                                format="%.4f",
                                ),
                                "fecha":st.column_config.DateColumn(
                                "fecha",
                                format="DD-MM-YYYY"
                                )},
                use_container_width=False,
                hide_index=True)
     historico_tasa.to_excel(buf := BytesIO())
     st.download_button(
        'Descargar histórico de tasas',
        buf.getvalue(),
        f'Histórico de tasas BCV.xlsx',
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",)