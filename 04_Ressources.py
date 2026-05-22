import streamlit as st
from donnees import init_session_state
from Crea_ress import crea_ress_tab
from style_sidebar import inject_style

st.set_page_config(page_title="Ressources — Atelier Devineau", page_icon="🧑‍🔧")
inject_style()

if not st.session_state.get("authentifie"):
    st.warning("Veuillez vous connecter depuis la page d'accueil.")
    st.stop()

init_session_state()
crea_ress_tab()
