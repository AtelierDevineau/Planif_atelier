import streamlit as st
import base64
import os

def inject_style():
    """Injecte le CSS global : police GT Walsheim et style sidebar."""

    # Charger la police depuis le repo
    font_path = os.path.join(os.path.dirname(__file__), "fonts", "GT-Walsheim-Regular.ttf")
    try:
        with open(font_path, "rb") as f:
            font_b64 = base64.b64encode(f.read()).decode("utf-8")
        font_face = f"""
        @font-face {{
            font-family: 'GTWalsheim';
            src: url(data:font/truetype;base64,{font_b64}) format('truetype');
            font-weight: normal;
            font-style: normal;
        }}
        """
    except FileNotFoundError:
        font_face = ""  # fallback si la police n'est pas trouvée

    st.markdown(f"""
    <style>
    {font_face}

    /* Police GT Walsheim sur toute la sidebar */
    [data-testid="stSidebar"] * {{
        font-family: 'GTWalsheim', sans-serif !important;
    }}

    /* Style spécial pour le lien Accueil (premier lien) uniquement */
    [data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:first-child {{
        background-color: #F5D627 !important;
        font-size: 1.1em !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        margin-bottom: 8px !important;
        padding: 10px 14px !important;
        color: #222 !important;
    }}

    [data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:first-child:hover {{
        background-color: #e6c520 !important;
    }}

    /* Autres liens : style neutre, pas de gras */
    [data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:not(:first-child) {{
        font-weight: normal !important;
        background-color: transparent !important;
        font-size: 1em !important;
    }}

    </style>
    """, unsafe_allow_html=True)
