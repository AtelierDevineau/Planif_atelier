#----------------CALCUL DES DISPOS------------------------
def recalculer_dispos(data_proj, ressources, ressources_base):
    """
    Repart des dispos de base et recalcule selon tous les projets/sous-tâches sauvegardés.
    Structure data_proj : {projet: {sous_tache: {Assignations: [{Nom, Pct}]}}}
    """
    # Repartir des dispos de base
    for r in ressources:
        r["Dispo_restante"] = next(
            rb["Dispo_base"] for rb in ressources_base if rb["Nom"] == r["Nom"]
        )
    # Parcourir toutes les sous-tâches de tous les projets
    for projet, sous_taches in data_proj.items():
        for nom_st, data in sous_taches.items():
            for assignation in data.get("Assignations", []):
                for r in ressources:
                    if r["Nom"] == assignation["Nom"]:
                        r["Dispo_restante"] -= assignation["Pct"]


#-------------FONCTION POUR RETURN DISPO RESTANTE--------------
def get_dispo_restante(nom, ressources):
    """Retourne la dispo restante d'une ressource"""
    return next(r["Dispo_restante"] for r in ressources if r["Nom"] == nom)


#-------------FONCTION POUR RETURN DISPO BASE--------------
def get_dispo_base(nom, ressources_base):
    """Retourne la dispo de base d'une ressource"""
    return next(r["Dispo_base"] for r in ressources_base if r["Nom"] == nom)


#-------------FONCTION POUR RETURN CHARGE SUR SOUS-TACHE COURANTE--------------
def get_charge_sur_projet(nom, assignations_sauvegardees):
    """Retourne la charge déjà assignée à une ressource sur la sous-tâche courante"""
    return next((a["Pct"] for a in assignations_sauvegardees if a["Nom"] == nom), 0)


#-------------FONCTION POUR RETURN NOMS PERS DISPO + DEJA ASSIGNEES SOUS-TACHE COURANTE--------------
def get_noms_ressources_disponibles(ressources, assignations_sauvegardees):
    """Retourne les ressources avec dispo > 0, plus celles déjà assignées à la sous-tâche courante"""
    noms_deja_assignes = [a["Nom"] for a in assignations_sauvegardees]
    return [
        r["Nom"] for r in ressources
        if r["Dispo_restante"] > 0 or r["Nom"] in noms_deja_assignes
    ]


#-------------FONCTION POUR STOCKAGE DES DONNEES DE LA BARRE DE DISPO VISUELLE--------------
def get_segments_charge(nom, data_proj, projet_courant):
    """
    Retourne la liste des segments colorés pour la barre de charge d'une ressource.
    Agrège toutes les sous-tâches par projet pour l'affichage.
    Chaque segment = {"projet": nom, "pct": valeur, "couleur": hex}
    Le dernier segment = dispo restante en gris clair.
    """
    import streamlit as st
    from donnees import get_couleur_projet

    # Agréger la charge par projet (somme sur toutes les sous-tâches)
    charge_par_projet = {}
    for nom_proj, sous_taches in data_proj.items():
        if projet_courant and nom_proj == projet_courant:
            continue
        for data in sous_taches.values():
            for a in data.get("Assignations", []):
                if a["Nom"] == nom:
                    charge_par_projet[nom_proj] = charge_par_projet.get(nom_proj, 0) + a["Pct"]

    segments = []
    total_assigne = 0
    for nom_proj, pct in charge_par_projet.items():
        segments.append({
            "projet": nom_proj,
            "pct": pct,
            "couleur": get_couleur_projet(nom_proj)
        })
        total_assigne += pct

    # Dispo de base depuis le session_state
    dispo_base = next(
        r["Dispo_base"]
        for r in st.session_state.Ressources_base
        if r["Nom"] == nom
    )
    dispo_restante = dispo_base - total_assigne
    if dispo_restante > 0:
        segments.append({
            "projet": "Disponible",
            "pct": dispo_restante,
            "couleur": "#E0E0E0"
        })
    return segments
