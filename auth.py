import streamlit as st
from streamlit_cookies_controller import CookieController

def verifier_auth():
    """
    Vérifie l'authentification via session_state ou cookie.
    Arrête la page si non authentifié.
    """
    controller = CookieController()

    if not st.session_state.get("authentifie"):
        cookie_auth = controller.get("atelier_auth")
        if cookie_auth == "true":
            st.session_state.authentifie = True
        elif cookie_auth is None:
            # Cookie pas encore lu — attendre le prochain rendu
            st.stop()
        else:
            st.warning("Veuillez vous connecter depuis la page d'accueil.")
            st.stop()

    return True
