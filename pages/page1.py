import os
import time
from io import BytesIO
import altair as alt 
from multiprocessing import Process, Queue
import streamlit as st
from datetime import datetime, date
from helpers.navigation import make_sidebar
from scripts.bcv.data import get_fecha_tasa_bcv_dia, get_monto_tasa_bcv_dia
from scripts.bcv.data import historico_tasas_bcv, path_file_tasas_bcv
from scripts.bcv.bcv_estadisticas_tasas import actulizar_file_tasas
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
      task = tasks_to_accomplish.get_nowait()
      actulizar_file_tasas()
      tasks_that_are_done.put(task)
      time.sleep(.5)

def actualizar_tasa_bcv():
    tasks_to_accomplish = Queue()
    tasks_that_are_done = Queue()
    tasks_to_accomplish.put("Tasa de cambio actualizada!")
    p = Process(target=update_file,args=(tasks_to_accomplish, tasks_that_are_done))
    p.start()
    p.join()
    st.info(tasks_that_are_done.get())
    time.sleep(1)
    st.rerun()
          

def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


if __name__ == '__main__':
    date = get_fecha_tasa_bcv_dia().date()

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
        <div class="value">""" +str(date)+  """
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
       actualizar_tasa_bcv()

with st.expander("Evolución tasa BCV"):
     historico_tasa = historico_tasas_bcv()
     df = historico_tasa[historico_tasa['año'] == 2024]
     chart = alt.Chart(df, title='Histórico').mark_line().encode(
      x='fecha', y=alt.Y('venta_ask2', scale=alt.Scale(domain=[df['venta_ask2'].min() - 1, df['venta_ask2'].max() + 1])), strokeDash='cod_mon'
        ).properties(width=650, height=350)     
     st.altair_chart(chart, use_container_width=True)

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