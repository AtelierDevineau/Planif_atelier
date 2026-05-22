import streamlit as st
import json
import requests
import base64

#---------GITHUB---------------------------------------------------------------------------------

GITHUB_REPO = st.secrets["GITHUB_REPO"]
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_API_BASE = f"https://api.github.com/repos/{GITHUB_REPO}/contents"

def _headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

def _charger_fichier(nom_fichier):
    """Lit un fichier JSON depuis le repo GitHub. Retourne (données, sha)."""
    response = requests.get(f"{GITHUB_API_BASE}/{nom_fichier}", headers=_headers())
    if response.status_code == 200:
        data = response.json()
        contenu = base64.b64decode(data["content"]).decode("utf-8")
        return json.loads(contenu), data["sha"]
    else:
        st.error(f"Erreur de lecture GitHub ({response.status_code}) pour {nom_fichier}")
        return None, None

def _sauvegarder_fichier(nom_fichier, donnees, sha):
    """Écrit un fichier JSON sur GitHub. Retourne le nouveau sha."""
    contenu_encode = base64.b64encode(
        json.dumps(donnees, ensure_ascii=False, indent=4).encode("utf-8")
    ).decode("utf-8")
    payload = {
        "message": f"Mise à jour {nom_fichier} via l'app",
        "content": contenu_encode,
        "sha": sha
    }
    response = requests.put(
        f"{GITHUB_API_BASE}/{nom_fichier}", headers=_headers(), json=payload
    )
    if response.status_code in (200, 201):
        return response.json()["content"]["sha"]
    else:
        st.error(f"Erreur de sauvegarde GitHub ({response.status_code}) pour {nom_fichier}")
        return sha

# Fonctions publiques projets
def charger_projets_github():
    return _charger_fichier("projets.json")

def sauvegarder_projets_github(projets, sha):
    return _sauvegarder_fichier("projets.json", projets, sha)

# Fonctions publiques ressources
def charger_ressources_github():
    return _charger_fichier("ressources.json")

def sauvegarder_ressources_github(ressources, sha):
    return _sauvegarder_fichier("ressources.json", ressources, sha)

# Fonctions publiques assignations
def charger_assignations_github():
    return _charger_fichier("assignations.json")

def sauvegarder_assignations_github(assignations, sha):
    return _sauvegarder_fichier("assignations.json", assignations, sha)


#---------POSTES---------------------------------------------------------------------------------
# Dictionnaire poste -> couleur (utilisé dans Crea_ress et Calendrier)
POSTES = {
    "BE":             "#4E9AF1",  # bleu
    "Serrurerie":     "#F1874E",  # orange
    "Construction":   "#A0C45A",  # vert olive
    "Usinage":        "#A64EF1",  # violet
    "Déco":           "#F1C84E",  # jaune
    "Administration": "#4EF1C8",  # turquoise
    "Tapisserie" :    "#0218C7",  #Bleu marine
    "Régisseur":      "#F14E7A",  # rose
    "Autres":         "#A0A0A0",  # gris
}


#---------CALENDRIER---------------------------------------------------------------------------------

Options_cal = {
    "initialView": "dayGridMonth",
    "locale": "fr",
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay"
    }
}

#-------INITIALISATION SESSION STATE-----------------------------------------------------------------------------------

def init_session_state():
    """Initialise les variables de session si elles n'existent pas encore"""

    # Ressources : chargées depuis GitHub
    if "Ressources_base" not in st.session_state:
        ressources, sha = charger_ressources_github()
        st.session_state.Ressources_base = ressources or []
        st.session_state.ressources_sha = sha

    # Ressources avec dispo restante : calculées depuis Ressources_base
    if "Ressources" not in st.session_state:
        st.session_state.Ressources = [
            {"Nom": r["Nom"], "Dispo_restante": r["Dispo_base"]}
            for r in st.session_state.Ressources_base
        ]

    # Assignations : chargées depuis GitHub
    if "Data_proj" not in st.session_state:
        assignations, sha = charger_assignations_github()
        st.session_state.Data_proj = assignations or {}
        st.session_state.assignations_sha = sha

    # Projets Gantt : chargés depuis GitHub
    if "Projets_gantt" not in st.session_state:
        projets, sha = charger_projets_github()
        st.session_state.Projets_gantt = projets or []
        st.session_state.projets_sha = sha

    # Message de succès persisté entre reruns
    if "msg_succes" not in st.session_state:
        st.session_state.msg_succes = None


#------RECUPERER COULEUR PROJET--------------------------------------------------
def get_couleur_projet(nom_projet):
    """Retourne la couleur hex d'un projet depuis le session_state, gris par défaut"""
    for p in st.session_state.Projets_gantt:
        if p["projet"] == nom_projet:
            return p["couleur"]
    return "#CCCCCC"


#------RECUPERER COULEUR POSTE--------------------------------------------------
def get_couleur_poste(poste):
    """Retourne la couleur hex d'un poste, gris par défaut"""
    return POSTES.get(poste, "#A0A0A0")


#------CONSTRUIRE ABSENCES_CAL DEPUIS RESSOURCES_BASE---------------------------
def build_absences_cal():
    """Construit la liste d'événements calendrier depuis les absences dans Ressources_base"""
    events = []
    for r in st.session_state.Ressources_base:
        couleur = get_couleur_poste(r.get("Poste", "Autres"))
        for absence in r.get("absences", []):
            events.append({
                "title": r["Nom"],
                "start": absence["start"],
                "end": absence["end"],
                "backgroundColor": couleur,
                "borderColor": couleur,
            })
    return events
