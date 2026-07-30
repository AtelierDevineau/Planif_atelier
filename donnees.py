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
    response = requests.get(f"{GITHUB_API_BASE}/{nom_fichier}", headers=_headers())
    if response.status_code == 200:
        data = response.json()
        contenu = base64.b64decode(data["content"]).decode("utf-8")
        return json.loads(contenu), data["sha"]
    else:
        st.error(f"Erreur de lecture GitHub ({response.status_code}) pour {nom_fichier}")
        return None, None

def _sauvegarder_fichier(nom_fichier, donnees, sha):
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

def charger_projets_github():
    return _charger_fichier("projets.json")

def sauvegarder_projets_github(projets, sha):
    return _sauvegarder_fichier("projets.json", projets, sha)

def charger_ressources_github():
    return _charger_fichier("ressources.json")

def sauvegarder_ressources_github(ressources, sha):
    return _sauvegarder_fichier("ressources.json", ressources, sha)

def charger_assignations_github():
    return _charger_fichier("assignations.json")

def sauvegarder_assignations_github(assignations, sha):
    return _sauvegarder_fichier("assignations.json", assignations, sha)


#---------POSTES---------------------------------------------------------------------------------
POSTES = {
    "BE":             "#4E9AF1",  # bleu
    "Serrurerie":     "#F1874E",  # orange
    "Construction":   "#A0C45A",  # vert olive
    "Usinage":        "#A64EF1",  # violet
    "Peinture":       "#F1C84E",  # jaune
    "Sculpture":      "#2E8B57",  # vert foncé
    "Administration": "#4EF1C8",  # turquoise
    "Régisseur":      "#F14E7A",  # rose
    "Tapisserie":     "#E07B54",  # terre cuite
    "Autres":         "#A0A0A0",  # gris
}

# Correspondance type de sous-tâche → couleur dans le Gantt
COULEURS_TACHES = {
    "Pré étude":    "#7EB8F7",  # bleu clair (BE clair)
    "Etude":        "#4E9AF1",  # bleu (BE)
    "Construction": "#A0C45A",  # vert olive (Construction)
    "Serrurerie":   "#F1874E",  # orange (Serrurerie)
    "CU":           "#A64EF1",  # violet (Usinage)
    "Peinture":     "#F1C84E",  # jaune (Peinture)
    "Sculpture":    "#2E8B57",  # vert foncé (Sculpture)
    "Tapisserie":   "#E07B54",  # terre cuite (Tapisserie)
    "Montage":      "#222222",  # noir
    "Autre":        "#A0A0A0",  # gris
}

# Ordre d'affichage des types de tâches dans le Gantt
ORDRE_TACHES = [
    "Pré étude", "Etude", "Construction", "Serrurerie",
    "Sculpture", "Tapisserie", "Peinture", "CU", "Montage", "Autre"
]


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

#-------PROJETS-----------------------------------------------------------------------------------
Projets = [
    {"Nom": "L'enlèvement au sérail", "Client": "TCE"},
    {"Nom": "Manon Lescaut", "Client": "TCE"},
    {"Nom": "Brundibar", "Client": "L'opéra Comique"}
]

#-------INITIALISATION SESSION STATE-----------------------------------------------------------------------------------

def init_session_state():
    if "Ressources_base" not in st.session_state:
        ressources, sha = charger_ressources_github()
        st.session_state.Ressources_base = ressources or []
        st.session_state.ressources_sha = sha

    if "Ressources" not in st.session_state:
        st.session_state.Ressources = [
            {"Nom": r["Nom"], "Dispo_restante": r["Dispo_base"]}
            for r in st.session_state.Ressources_base
        ]

    if "Data_proj" not in st.session_state:
        assignations, sha = charger_assignations_github()
        st.session_state.Data_proj = assignations or {}
        st.session_state.assignations_sha = sha

    if "Projets_gantt" not in st.session_state:
        projets, sha = charger_projets_github()
        st.session_state.Projets_gantt = projets or []
        st.session_state.projets_sha = sha

    if "msg_succes" not in st.session_state:
        st.session_state.msg_succes = None


#------FORMATER DATE EN JJ/MM/AAAA--------------------------------------------------
def fmt_date(date_iso):
    """Convertit une date ISO 'AAAA-MM-JJ' en 'JJ/MM/AAAA'."""
    try:
        from datetime import date as _date
        d = _date.fromisoformat(date_iso)
        return f"{d.day:02d}/{d.month:02d}/{d.year}"
    except Exception:
        return date_iso


#------RECUPERER COULEUR PROJET--------------------------------------------------
def get_couleur_projet(nom_projet):
    for p in st.session_state.Projets_gantt:
        if p["projet"] == nom_projet:
            return p["couleur"]
    return "#CCCCCC"


#------RECUPERER COULEUR POSTE--------------------------------------------------
def get_couleur_poste(poste):
    return POSTES.get(poste, "#A0A0A0")


#------RECUPERER COULEUR TACHE--------------------------------------------------
def get_couleur_tache(nom_tache):
    """Retourne la couleur d'une sous-tâche selon son type."""
    return COULEURS_TACHES.get(nom_tache, COULEURS_TACHES["Autre"])


#------CONSTRUIRE ABSENCES_CAL--------------------------------------------------
def build_absences_cal():
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
