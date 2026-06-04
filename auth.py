import streamlit as st
from streamlit_cookies_controller import CookieController

def verifier_auth():
    if "authentifie" not in st.session_state:
        st.session_state.authentifie = False

    controller = CookieController()

    if not st.session_state.authentifie:
        cookie_auth = controller.get("atelier_auth")
        if cookie_auth == "true":
            st.session_state.authentifie = True
        elif cookie_auth is None:
            pass
        else:
            st.warning("Veuillez vous connecter depuis la page d'accueil.")
            st.stop()

    return True
