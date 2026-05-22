import streamlit as st
from donnees import init_session_state
from Calendrier import calendrier_tab
from Assignation import assignation_tab
from Crea_proj import crea_proj_tab
from Crea_ress import crea_ress_tab
from Recap import recap_tab

# ── Login ─────────────────────────────────────────────────────────────────────
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False

if not st.session_state.authentifie:
    st.title("Accès à l'application")
    mdp = st.text_input("Mot de passe", type="password")
    if st.button("Connexion"):
        if mdp == st.secrets["MOT_DE_PASSE"]:
            st.session_state.authentifie = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect")
    st.stop()
# ── Init ──────────────────────────────────────────────────────────────────────
init_session_state()

# ── Logo ──────────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("Atelier Devineau logo.png", use_container_width=True)

# ── Titre centré et en gras ─────────────────────────────────────────────────────────────────────
st.markdown("<h1 style='text-align:center; font-weight:bold;'>Planification projets</h1>", unsafe_allow_html=True)
# ── Onglets ───────────────────────────────────────────────────────────────────
Calendrier,Crea_proj, Crea_ress, Assignation, Recap = st.tabs(["Calendrier", "Création projet","Ajout de Ressources","Assignation équipe","Récapitulatif"])

with Calendrier:
    calendrier_tab()

with Crea_proj:
    crea_proj_tab()

with Crea_ress:
    crea_ress_tab()

with Assignation:
    assignation_tab()

with Recap:
    recap_tab()


