import os
import streamlit as st
from time import sleep
from datetime import datetime
from scripts.conexion import ConexionBD
from user.control_usuarios import ControlAcceso
from user.usuarios_roles import ClsUsuariosRoles
from dotenv import load_dotenv
from scripts.empresa import ClsEmpresa

load_dotenv()

st.set_page_config(page_title='LÁCTEOS DOEL, C.A.', 
                   layout="centered", 
                   initial_sidebar_state="collapsed", 
                   page_icon=':vs:')

MENU_INICIO = 'pages/page1.py'

def roles():
    return ClsUsuariosRoles.roles()

st.title("Datos del usuario")
st.write("Ingrese sus datos.")
username = st.text_input("usuario")
password = st.text_input("clave", type="password")

if st.button("Iniciar sesión", type="primary"):
    conexion = ConexionBD(base_de_datos=os.getenv('DB_NAME_PROFIT_PANA'))
    if is_valid := ControlAcceso(conexion).aut_user(username, password):
        date = datetime.now()
        print(f"{date} Usuario {username} ha iniciado sesión.")
        st.session_state.logged_in = True
        rol = roles()
        # Se establece por primera vez el modulo a usar
        if rol['DOEL'] == 1:
            ClsEmpresa('DOEL')
        else:
            ClsEmpresa('PANA')

        st.success("Sesión iniciada!")
        sleep(0.5)
        st.switch_page(MENU_INICIO)
    else:
     st.error("usuario o clave incorrecta")
        