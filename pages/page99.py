import os
import time
import streamlit as st
from helpers.navigation import make_sidebar
from  user import usuarios
from user.control_usuarios import ControlAcceso
from scripts.conexion import ConexionBD

st.set_page_config(page_title='DataPy: Reiniciar clave', 
                   layout='centered', 
                   page_icon=':vs:')
make_sidebar()
st.header("🛠️ Cambiar clave de usuario")
with st.expander("mostrar"):
   current_password = st.text_input("clave actual", type="password")
   new_password = st.text_input("nueva clave", type="password")
   rep_new_password = st.text_input("repetir clave", type="password")
   conexion = ConexionBD(base_de_datos = os.getenv("DB_NAME_PROFIT_PANA"))
   if st.button("cambiar", type="primary"):
      user = usuarios.ClsUsuarios.id_usuario()
      aut = ControlAcceso(conexion).aut_user(user, current_password)
      if aut:
         if new_password==rep_new_password:
            ControlAcceso(conexion).change_password(user, new_password) 
            st.success("La clave fue cambiada con éxito!")
            time.sleep(1)
            st.switch_page("pages/page1.py")
         else:
            st.error("La nueva clave ingresada no coincide con la confirmación.")
      else:
         st.error("La clave ingresada no coincide con la anterior.")

