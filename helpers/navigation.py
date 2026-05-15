from time import sleep

import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
from empresa import ClsEmpresa

# Removed import of 'get_pages' as it is no longer available in Streamlit


def get_current_page_name():
    ctx = get_script_run_ctx()
    if ctx is None:
        raise RuntimeError("No se pudo obtener el contexto del script.")

    return ctx.page_script_hash.split("/")[-1]  # type: ignore


def make_sidebar():
    with st.sidebar:
        # Centrar el título
        # quitar margenes
        st.markdown(
            "<h1 style='text-align: center; margin: 0;'>DataPy</h1>",
            unsafe_allow_html=True,
        )
        # imagen desde URL
        # Quitar margenes
        image_url = "images/svg3.svg"

        st.image(image_url)
        # imagen local
        st.markdown("---")

        # chequea si el usuario está logueado
        if st.session_state.get("logged_in", False):
            _extracted_from_make_sidebar()  # llama a la función que crea el sidebar
        elif get_current_page_name() != "app":
            # si no está logueado y no está en la página de login, redirige a la página de login
            st.switch_page("app.py")


def _extracted_from_make_sidebar():
    rol_user = st.session_state.rol_user
    es_admin = rol_user.has_permission("Administrador", "read")

    st.page_link("pages/page1.py", label="Inicio", icon=None)

    pages_config = [
        # ("pages/page2.py", "Notas de entrega", "Notas", "read"),
        ("pages/page3.py", "Gestión Ruteros", "Rutero", "create"),
        ("pages/page4.py", "Procesos Masivos", "ProcesosMasivos", "read"),
        ("pages/page5.py", "Cuentas por cobrar", "CxC", "read"),
        ("pages/page6.py", "Tributario", "Tributario", "read"),
        ("pages/page7.py", "Inventario", "Inventario", "read"),
        ("pages/page8.py", "Compras", "Compras", "read"),
        ("pages/page9.py", "Edo. Cta. Rutero", "Rutero", "read"),
        ("pages/page10.py", "Ganancias Ruteros", "Rutero", "create"),
    ]

    for page, label, modulo, permiso in pages_config:
        if es_admin or rol_user.has_permission(modulo, permiso):
            st.page_link(page, label=label, icon=None)

    st.page_link("pages/page99.py", label="Configuración", icon=None)

    st.write("\n" * 2)
    l_modulos = ["PANA", "DOEL"]

    # administra el acceso del usuario a los módulos
    es_admin = st.session_state.rol_user.has_permission("Administrador", "read")
    tiene_mod_der = st.session_state.rol_user.has_permission("PANA", "read")
    tiene_mod_izq = st.session_state.rol_user.has_permission("DOEL", "read")

    if not es_admin:
        if not tiene_mod_der and "DOEL" in l_modulos:
            l_modulos.remove("DOEL")
        if not tiene_mod_izq and "PANA" in l_modulos:
            l_modulos.remove("PANA")

    if not l_modulos:
        st.warning("No tienes acceso a ningun modulo.")
        return

    user = st.session_state.get("usuario")
    mod_select = st.session_state.cls_empresa._usuarios.get(user, {}).get("modulo")
    if mod_select not in l_modulos:
        mod_select = l_modulos[0]

    modulo = st.radio(
        "Seleccione la empresa:",
        l_modulos,
        index=l_modulos.index(mod_select),
        on_change=al_cambiar_empresa,
        horizontal=True,
    )
    if modulo is None:
        modulo = l_modulos[0]

    st.session_state.cls_empresa = ClsEmpresa(st.session_state.usuario, modulo, False)

    if st.button(
        "Cerrar sesión",
        type="primary",
    ):
        logout()

    st.cache_data.clear()


def logout():
    # ClsEmpresa.limpiar_usuario(st.session_state.get("usuario", ""))
    st.session_state.logged_in = False
    st.info("Se ha cerrado la sesión con éxito!")
    sleep(0.5)
    st.switch_page("app.py")


def al_cambiar_empresa():
    # Reinicia las variables de sesión relacionadas con las paginas
    st.cache_data.clear()
