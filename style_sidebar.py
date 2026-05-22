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
    section[data-testid="stSidebar"] *,
    [data-testid="stSidebarContent"] * {{
        font-family: 'GTWalsheim', sans-serif !important;
    }}

    /* Tous les liens de nav : style neutre */
    section[data-testid="stSidebar"] a,
    section[data-testid="stSidebar"] li a,
    section[data-testid="stSidebar"] nav a {{
        font-weight: normal !important;
        background-color: transparent !important;
        font-size: 1em !important;
    }}

    /* Premier lien de nav : Accueil en jaune/gras */
    section[data-testid="stSidebar"] nav ul li:first-child a,
    section[data-testid="stSidebar"] nav li:first-child a {{
        background-color: #F5D627 !important;
        font-weight: bold !important;
        font-size: 1.1em !important;
        border-radius: 6px !important;
        color: #222 !important;
        display: block !important;
        padding: 8px 12px !important;
    }}

    section[data-testid="stSidebar"] nav ul li:first-child a:hover,
    section[data-testid="stSidebar"] nav li:first-child a:hover {{
        background-color: #e6c520 !important;
    }}

    </style>
    """, unsafe_allow_html=True)
