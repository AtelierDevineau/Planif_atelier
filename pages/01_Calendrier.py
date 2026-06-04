import streamlit as st
from donnees import init_session_state
from Calendrier import calendrier_tab
from style_sidebar import inject_style
from auth import verifier_auth

st.set_page_config(page_title="Calendrier — Atelier Devineau", page_icon="📅")
inject_style()
verifier_auth()


init_session_state()
calendrier_tab()
