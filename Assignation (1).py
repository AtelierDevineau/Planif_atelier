import streamlit as st
from datetime import date
from donnees import sauvegarder_assignations_github
from Logique import (
    recalculer_dispos,
    get_dispo_restante,
    get_charge_sur_projet,
    get_noms_ressources_disponibles
)
from Logique import get_segments_charge

# -------------------------------------------------------
# FONCTIONS UTILITAIRES
# -------------------------------------------------------

def init_statut_sauvegarde():
    if "statut_sauvegarde" not in st.session_state:
        st.session_state.statut_sauvegarde = "vide"

def marquer_modifie():
    st.session_state.statut_sauvegarde = "modifie"

def afficher_statut():
    if st.session_state.statut_sauvegarde == "sauvegarde":
        st.success("✅ Sauvegardé")
    elif st.session_state.statut_sauvegarde == "modifie":
        st.warning("❌ Modifications non sauvegardées")


def ressource_en_conge(nom, start_st, end_st):
    """
    Vérifie si une ressource a une absence qui chevauche la période de la sous-tâche.
    Retourne la liste des périodes d'absence en conflit.
    """
    conflits = []
    for r in st.session_state.Ressources_base:
        if r["Nom"] == nom:
            for absence in r.get("absences", []):
                debut_abs = date.fromisoformat(absence["start"])
                fin_abs = date.fromisoformat(absence["end"])
                debut_st = date.fromisoformat(start_st)
                fin_st = date.fromisoformat(end_st)
                # Chevauchement si les périodes se croisent
                if debut_abs < fin_st and fin_abs > debut_st:
                    conflits.append(f"{absence['start']} → {absence['end']}")
    return conflits


def get_data_sous_tache(projet, nom_tache):
    """Retourne les données d'assignation d'une sous-tâche, dict vide si inexistant."""
    return (
        st.session_state.Data_proj
        .get(projet, {})
        .get(nom_tache, {})
    )


def afficher_bloc_ressource(k, noms_filtres, default_index, assignations_sauvegardees, projet, sous_tache_data):
    """Affiche le bloc visuel d'une ressource et retourne l'assignation choisie."""
    pct_sauvegarde = next(
        (a["Pct"] for i, a in enumerate(assignations_sauvegardees) if i == k), 0
    )
    start_st = sous_tache_data.get("start", "")
    end_st = sous_tache_data.get("end", "")

    with st.container(border=True):
        st.markdown(f"**Personne {k+1}**")

        nom_choisi = st.selectbox(
            "Nom :", noms_filtres,
            index=default_index,
            key=f"select_ress_{projet}_{sous_tache_data.get('tache','')}_{k}",
            on_change=marquer_modifie
        )

        dispo_restante = get_dispo_restante(nom_choisi, st.session_state.Ressources)
        charge_ce_projet = get_charge_sur_projet(nom_choisi, assignations_sauvegardees)
        max_slider = dispo_restante + charge_ce_projet

        st.caption(f"Disponibilité restante : {dispo_restante}%")

        # Alerte congés si chevauchement avec la sous-tâche
        if start_st and end_st:
            conflits = ressource_en_conge(nom_choisi, start_st, end_st)
            if conflits:
                st.warning(
                    f"⚠️ **{nom_choisi}** a des congés pendant cette sous-tâche : "
                    + ", ".join(conflits)
                )

        pct_choisi = st.slider(
            "Charge :", min_value=0, max_value=max_slider,
            value=pct_sauvegarde,
            key=f"slider_ress_{projet}_{sous_tache_data.get('tache','')}_{k}",
            on_change=marquer_modifie
        )

    return {"Nom": nom_choisi, "Pct": pct_choisi}


def afficher_tableau_recap():
    """Affiche le récap sous forme de barres de charge par ressource."""
    st.divider()
    st.subheader("Récapitulatif")

    # Tableau projet / nb ressources total
    recap = {}
    for projet, sous_taches in st.session_state.Data_proj.items():
        noms = set()
        for data in sous_taches.values():
            for a in data.get("Assignations", []):
                noms.add(a["Nom"])
        recap[projet] = len(noms)

    st.dataframe({
        "Projet": list(recap.keys()),
        "Ressources distinctes": list(recap.values())
    })

    st.subheader("Charge par ressource")

    for r in st.session_state.Ressources:
        nom = r["Nom"]

        est_assigne = any(
            a["Nom"] == nom
            for sous_taches in st.session_state.Data_proj.values()
            for data in sous_taches.values()
            for a in data.get("Assignations", [])
        )
        if not est_assigne:
            continue

        st.caption(f"**{nom}**")
        segments = get_segments_charge(nom, st.session_state.Data_proj, projet_courant=None)

        barres = ""
        legende = ""
        for s in segments:
            if s["pct"] <= 0:
                continue
            nom_projet_safe = s["projet"].replace("'", "&#39;")
            tooltip = f"{nom_projet_safe} : {s['pct']}%"
            barres += (
                f'<div title="{tooltip}" style="'
                f'width:{s["pct"]}%;background-color:{s["couleur"]};'
                f'height:20px;display:inline-block;vertical-align:middle;"></div>'
            )
            legende += (
                f'<span style="margin-right:12px;font-size:0.75em;">'
                f'<span style="display:inline-block;width:10px;height:10px;'
                f'background-color:{s["couleur"]};border-radius:2px;'
                f'margin-right:4px;vertical-align:middle;"></span>'
                f'{nom_projet_safe} ({s["pct"]}%)</span>'
            )

        html = (
            f'<div style="width:100%;background:#F0F0F0;border-radius:4px;'
            f'overflow:hidden;margin-bottom:4px;">{barres}</div>'
            f'<div style="margin-bottom:8px;">{legende}</div>'
        )
        st.markdown(html, unsafe_allow_html=True)


# -------------------------------------------------------
# ONGLET PRINCIPAL
# -------------------------------------------------------

def assignation_tab():
    st.subheader('Assignation des équipes')
    init_statut_sauvegarde()

    # Recalcul des dispos à chaque rendu
    recalculer_dispos(
        st.session_state.Data_proj,
        st.session_state.Ressources,
        st.session_state.Ressources_base
    )

    projets = st.session_state.Projets_gantt
    if not projets:
        st.info("Aucun projet disponible. Créez d'abord un projet dans l'onglet 'Création projet'.")
        return

    # --- Sélection du projet ---
    noms_projets = [p["projet"] for p in projets]
    projet = st.selectbox(
        "Choisir un projet :",
        options=noms_projets,
        key="choix_projet",
        on_change=marquer_modifie
    )

    # Récupérer les sous-tâches du projet sélectionné
    sous_taches_projet = next(
        (p["sous_taches"] for p in projets if p["projet"] == projet), []
    )

    if not sous_taches_projet:
        st.info("Ce projet n'a pas encore de sous-tâches. Ajoutez-en dans l'onglet 'Création projet'.")
        return

    # --- Sélection de la sous-tâche ---
    noms_sous_taches = [st_data["tache"] for st_data in sous_taches_projet]
    nom_sous_tache = st.selectbox(
        "Choisir une sous-tâche :",
        options=noms_sous_taches,
        key="choix_sous_tache",
        on_change=marquer_modifie
    )

    # Données de la sous-tâche sélectionnée (dates)
    sous_tache_data = next(
        (st_data for st_data in sous_taches_projet if st_data["tache"] == nom_sous_tache),
        {}
    )

    # Afficher les dates de la sous-tâche
    st.caption(f"📅 {sous_tache_data.get('start', '')} → {sous_tache_data.get('end', '')}")

    st.markdown(f"<h2 style='text-align:center; font-weight:bold;'>{projet} — {nom_sous_tache}</h2>", unsafe_allow_html=True)

    # Initialiser Data_proj pour ce projet/sous-tâche si nécessaire
    if projet not in st.session_state.Data_proj:
        st.session_state.Data_proj[projet] = {}
    if nom_sous_tache not in st.session_state.Data_proj[projet]:
        st.session_state.Data_proj[projet][nom_sous_tache] = {}

    data_st = st.session_state.Data_proj[projet][nom_sous_tache]
    assignations_sauvegardees = data_st.get("Assignations", [])

    # --- Préparation des listes ---
    noms_disponibles = get_noms_ressources_disponibles(
        st.session_state.Ressources, assignations_sauvegardees
    )

    nb_ress = st.number_input(
        "Personnes à affecter à cette sous-tâche :",
        value=data_st.get("Nb_ressources", 0),
        min_value=0,
        max_value=len(noms_disponibles),
        key=f"nb_ress_{projet}_{nom_sous_tache}",
        on_change=marquer_modifie
    )

    # --- Grille 2 colonnes ---
    lignes_cols = [st.columns(2) for _ in range(0, nb_ress, 2)]

    # --- Boucle ressources ---
    assignation_en_cours = []
    deja_choisis = []

    for k in range(nb_ress):
        nom_sauvegarde = (
            assignations_sauvegardees[k]["Nom"]
            if k < len(assignations_sauvegardees) else None
        )

        noms_filtres = [n for n in noms_disponibles if n not in deja_choisis]
        default_index = noms_filtres.index(nom_sauvegarde) if nom_sauvegarde in noms_filtres else 0

        with lignes_cols[k // 2][k % 2]:
            # On passe sous_tache_data pour avoir accès aux dates dans le bloc
            assignation = afficher_bloc_ressource(
                k, noms_filtres, default_index, assignations_sauvegardees,
                projet,
                {**sous_tache_data, "tache": nom_sous_tache}
            )

        deja_choisis.append(assignation["Nom"])
        assignation_en_cours.append(assignation)

    # --- Sauvegarde ---
    afficher_statut()

    if st.button("Sauvegarder"):
        st.session_state.Data_proj[projet][nom_sous_tache] = {
            "Nb_ressources": nb_ress,
            "Assignations": assignation_en_cours
        }
        recalculer_dispos(
            st.session_state.Data_proj,
            st.session_state.Ressources,
            st.session_state.Ressources_base
        )
        nouveau_sha = sauvegarder_assignations_github(
            st.session_state.Data_proj,
            st.session_state.assignations_sha
        )
        st.session_state.assignations_sha = nouveau_sha
        st.session_state.statut_sauvegarde = "sauvegarde"
        st.rerun()

    # --- Tableau récap ---
    if st.session_state.Data_proj:
        afficher_tableau_recap()
