import streamlit as st
from donnees import init_session_state
from Crea_proj import crea_proj_tab
from style_sidebar import inject_style
from auth import verifier_auth

st.set_page_config(page_title="Projets — Atelier Devineau", page_icon="📋")
inject_style()
verifier_auth()


init_session_state()
crea_proj_tab()
