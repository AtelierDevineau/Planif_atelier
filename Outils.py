import streamlit as st
from donnees import init_session_state
from Calendrier import calendrier_tab
from Assignation import assignation_tab
from Crea_proj import crea_proj_tab
from Crea_ress import crea_ress_tab
from Recap import recap_tab

# ── Configuration page ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Atelier Devineau — Outils",
    page_icon="🔧",
)

# ── Authentification ──────────────────────────────────────────────────────────
if not st.session_state.get("authentifie"):
    st.warning("Veuillez vous connecter depuis la page d'accueil.")
    st.stop()

# ── Init données ──────────────────────────────────────────────────────────────
init_session_state()

# ── Logo ──────────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("Atelier Devineau logo.png", use_container_width=True)

# ── Titre ─────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align:center; font-weight:bold;'>Planification projets</h1>",
    unsafe_allow_html=True
)

# ── Onglets ───────────────────────────────────────────────────────────────────
Calendrier, Crea_proj, Assignation, Crea_ress, Recap = st.tabs([
    "Calendrier", "Création projet", "Assignation équipe", "Ressources", "Récapitulatif"
])

with Calendrier:
    calendrier_tab()
with Crea_proj:
    crea_proj_tab()
with Assignation:
    assignation_tab()
with Crea_ress:
    crea_ress_tab()
with Recap:
    recap_tab()
