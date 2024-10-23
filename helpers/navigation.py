import streamlit as st
from time import sleep
import base64
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.source_util import get_pages
from user.usuarios_roles import ClsUsuariosRoles
from scripts.empresa import ClsEmpresa

def get_current_page_name():
    ctx = get_script_run_ctx()
    if ctx is None:
        raise RuntimeError("No se pudo obtener el contexto del script.")

    pages = get_pages("")
    return pages[ctx.page_script_hash]["page_name"] # type: ignore

def make_sidebar():
    with st.sidebar:
        # Custom CSS for changing the sidebar color
        custom_css = """
                    
                    """
        # Apply custom CSS
        st.markdown(custom_css, unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: grey;'>Gestión de Datos</h1>", 
                    unsafe_allow_html=True
        )
        st.sidebar.markdown("---")
        st.write("")
        st.write("")

        if st.session_state.get("logged_in", False):
            _extracted_from_make_sidebar()
        elif get_current_page_name() != "inicio":
            # If anyone tries to access a secret page without being logged in,
            # redirect them to the login page
            st.switch_page("inicio.py") 
        
# TODO Rename this here and in `make_sidebar`
def _extracted_from_make_sidebar():
    st.page_link("pages/page1.py", label="Inicio", icon=None)
    if ClsUsuariosRoles.roles()['NotasCxc'] == 1:
        st.page_link("pages/page2.py", label="Notas de entrega", icon=None)
    if ClsUsuariosRoles.roles()['AddDev'] == 1:
        st.page_link("pages/page3.py", label="Gestión Ruteros", icon=None)
    if ClsUsuariosRoles.roles()['Proc_Masiv'] == 1:
        st.page_link("pages/page4.py", label="Procesos Masivos", icon=None)
    if ClsUsuariosRoles.roles()['Cxc'] == 1:
        st.page_link("pages/page5.py", label="Cuentas por cobrar", icon=None)
    if ClsUsuariosRoles.roles()['Trib'] == 1:
        st.page_link("pages/page6.py", label="Tributario", icon=None)
    if ClsUsuariosRoles.roles()['Inventario'] == 1:
        st.page_link("pages/page7.py", label="Inventario", icon=None)
    if ClsUsuariosRoles.roles()['Compras'] == 1:
        st.page_link("pages/page8.py", label="Compras", icon=None)
    if ClsUsuariosRoles.roles()['EdoCtaRut'] == 1:
        st.page_link("pages/page9.py", label="Edo. Cta. Rutero", icon=None)
    if ClsUsuariosRoles.roles()['GanRut'] == 1:
        st.page_link("pages/page10.py", label="Ganancias Ruteros", icon=None)
    st.page_link("pages/page99.py", label="Configuración", icon=None)

    st.write("\n" * 2)
    l_modulos = ['DOEL', 'PANA']
    # administra el acceso del usuario a los módulos
    if ClsUsuariosRoles.roles()['DOEL'] == 0:
        l_modulos.pop(0)
    elif ClsUsuariosRoles.roles()['PANA'] == 0:
        l_modulos.pop(1)        

    indice_mod = l_modulos.index(ClsEmpresa.modulo_seleccionado())
    empresa_select = st.selectbox('Seleccione la empresa:', l_modulos, 
                                  index=indice_mod, 
                                  on_change=al_cambiar_empresa)

    if st.button("Cerrar sesión"):
        logout()

def al_cambiar_empresa():
    modulo = ClsEmpresa.modulo_seleccionado()   
    if modulo == 'DOEL':
       ClsEmpresa('PANA')
    else:
       ClsEmpresa('DOEL')
    st.cache_data.clear()

def logout():
    st.session_state.logged_in = False
    st.info("Se ha cerrado la sesión con éxito!")
    sleep(0.5)
    st.switch_page("inicio.py")
