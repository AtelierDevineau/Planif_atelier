import streamlit as st
from datetime import date, timedelta
from donnees import sauvegarder_projets_github, sauvegarder_assignations_github

#-------------AFFICHAGE----------------------
COULEURS_PALETTE = {
    "🔴":    "#FF6C6C",
    "🟠":   "#FFBD45",
    "🔵":     "#63CDEB",
    "🟢":     "#6BCB77",
    "🟣":   "#A78BFA",
    "⚫":     "#312E36",
    "🟤":     "#573129",
}

STYLE = """
<style>
/* Boutons supprimer → rouge */
div[data-testid="stButton"] button[kind="secondary"] {
    background-color: #FF4B4B;
    color: white;
    border: none;
}
div[data-testid="stButton"] button[kind="secondary"]:hover {
    background-color: #cc0000;
    color: white;
}
/* Boutons primary → vert */
div[data-testid="stButton"] button[kind="primary"] {
    background-color: #28a745;
    color: white;
    border: none;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    background-color: #1e7e34;
    color: white;
}
</style>
"""
#-------------CALLBACKS----------------------

def garder_expander_ouvert(key_expander):
    """Callback pour maintenir l'expander ouvert lors d'une interaction."""
    st.session_state[key_expander] = True

#-------------ONGLET-----------------------------

def crea_proj_tab():
    st.subheader("Gestion des projets")
    projets = st.session_state.Projets_gantt

    if st.session_state.get("msg_succes"):
        st.success(st.session_state.msg_succes)
        st.session_state.msg_succes = None

    # ---------- LISTE PROJETS EXISTANTS ------------
    if projets:
        st.subheader("Projets existants")

        couleurs_prises = {p["couleur"] for p in projets}

        for i, projet in enumerate(projets):
            couleur = projet["couleur"]
            key_expander = f"expander_open_{i}"
            if key_expander not in st.session_state:
                st.session_state[key_expander] = False

            with st.expander(
                f"**{projet['projet']}** - {len(projet['sous_taches'])} sous-tache(s)",
                expanded=st.session_state[key_expander]
            ):
                # On ne remet PAS à False ici — l'expander reste ouvert
                # tant que l'utilisateur interagit dedans

                # --------------- EDITION DU PROJET ---------------
                new_proj = st.text_input(
                    "Nom du projet",
                    value=projet["projet"],
                    key=f"nom_{i}"
                )

                col_client, col_couleur = st.columns([2, 1])
                with col_client:
                    new_client = st.text_input(
                        "Client",
                        value=projet.get("client", ""),
                        key=f"client_{i}",
                        placeholder="Nom du client"
                    )
                with col_couleur:
                    couleurs_disponibles = {
                        nom: hex_
                        for nom, hex_ in COULEURS_PALETTE.items()
                        if hex_ == couleur or hex_ not in couleurs_prises
                    }
                    noms_disponibles = list(couleurs_disponibles.keys())
                    hex_disponibles = list(couleurs_disponibles.values())
                    index_couleur = hex_disponibles.index(couleur) if couleur in hex_disponibles else 0
                    choix_couleur = st.selectbox(
                        "Couleur",
                        options=noms_disponibles,
                        index=index_couleur,
                        key=f"couleur_{i}",
                        format_func=lambda nom: f"{nom} ({COULEURS_PALETTE[nom]})"
                    )
                new_color = COULEURS_PALETTE[choix_couleur]

                new_description = st.text_area(
                    "Description",
                    value=projet.get("description", ""),
                    key=f"description_{i}",
                    placeholder="Décrivez le projet en quelques mots...",
                    height=80
                )

                # --------------- SOUS TACHES ----------------------
                st.markdown("**Sous-tâches**")
                sous_taches = projet["sous_taches"]
                a_supp = None

                for j, st_data in enumerate(sous_taches):
                    cols = st.columns([3, 2, 2, 0.6])
                    with cols[0]:
                        sous_taches[j]["tache"] = st.text_input(
                            "Nom", value=st_data["tache"],
                            key=f"tache_{i}_{j}", label_visibility="collapsed"
                        )
                    with cols[1]:
                        sous_taches[j]["start"] = st.date_input(
                            "Début",
                            value=date.fromisoformat(st_data["start"]),
                            key=f"start_{i}_{j}",
                            label_visibility="collapsed",
                            on_change=garder_expander_ouvert,
                            args=(key_expander,)
                        ).isoformat()
                    with cols[2]:
                        sous_taches[j]["end"] = st.date_input(
                            "Fin",
                            value=date.fromisoformat(st_data["end"]),
                            key=f"end_{i}_{j}",
                            label_visibility="collapsed",
                            on_change=garder_expander_ouvert,
                            args=(key_expander,)
                        ).isoformat()
                    with cols[3]:
                        if st.button("🗑️", key=f"del_st_{i}_{j}", help="Supprimer cette tâche"):
                            a_supp = j

                if a_supp is not None:
                    sous_taches.pop(a_supp)
                    st.session_state[key_expander] = True
                    st.rerun()

                # ---------------- AJOUT SOUS-TÂCHE -----------------------
                if st.button("➕ Ajouter une sous-tâche", key=f"add_st_{i}",type="tertiary"):
                    if sous_taches:
                        last_end = date.fromisoformat(sous_taches[-1]["end"])
                    else:
                        last_end = date.today()
                    sous_taches.append({
                        "tache": "Nouvelle tâche",
                        "start": last_end.isoformat(),
                        "end": (last_end + timedelta(weeks=2)).isoformat(),
                    })
                    st.session_state[key_expander] = True
                    st.rerun()

                # -------------- BOUTONS --------------------------
                col_save, col_del = st.columns([1, 1])
                with col_save:
                    if st.button("✅ Enregistrer les modifications", key=f"save_{i}",type="tertiary"):
                        projets[i]["projet"] = new_proj
                        projets[i]["couleur"] = new_color
                        projets[i]["sous_taches"] = sous_taches
                        projets[i]["client"] = new_client
                        projets[i]["description"] = new_description
                        nouveau_sha = sauvegarder_projets_github(
                            projets, st.session_state.projets_sha
                        )
                        st.session_state.projets_sha = nouveau_sha
                        st.session_state[key_expander] = True
                        st.session_state.msg_succes = f"Projet « {new_proj} » mis à jour et sauvegardé."
                        st.rerun()
                with col_del:
                    if st.button("🗑 Supprimer ce projet", key=f"suppr_{i}", type="secondary"):
                        nom_projet = projet["projet"]
                        if nom_projet in st.session_state.Data_proj and st.session_state.Data_proj[nom_projet].get("Assignations"):
                            nb = st.session_state.Data_proj[nom_projet].get("Nb_ressources", 0)
                            st.warning(
                                f"⚠️ Le projet **{nom_projet}** a {nb} ressource(s) assignée(s). "
                                f"Ces assignations seront supprimées."
                            )
                        projets.pop(i)
                        nouveau_sha = sauvegarder_projets_github(
                            projets, st.session_state.projets_sha
                        )
                        st.session_state.projets_sha = nouveau_sha
                        if nom_projet in st.session_state.Data_proj:
                            del st.session_state.Data_proj[nom_projet]
                            nouveau_sha_assig = sauvegarder_assignations_github(
                                st.session_state.Data_proj,
                                st.session_state.assignations_sha
                            )
                            st.session_state.assignations_sha = nouveau_sha_assig
                        st.session_state.msg_succes = f"Projet « {nom_projet} » supprimé."
                        st.rerun()

    # ----------------- CREATION NOUVEAU PROJET ----------------------
    st.divider()
    st.subheader("Nouveau projet")

    couleurs_prises = {p["couleur"] for p in projets}
    couleur_defaut = next(
        (hex_ for hex_ in COULEURS_PALETTE.values() if hex_ not in couleurs_prises),
        list(COULEURS_PALETTE.values())[0]
    )

    with st.form("form_nouveau_projet", clear_on_submit=True):
        nom_new = st.text_input("Nom du projet")
        client_new = st.text_input("Client", placeholder="Nom du client")
        description_new = st.text_area(
            "Description",
            placeholder="Décrivez le projet en quelques mots...",
            height=80
        )
        submitted = st.form_submit_button("Créer le projet")

    if submitted:
        if not nom_new.strip():
            st.error("Merci de saisir le nom du projet")
        elif any(p["projet"] == nom_new.strip() for p in projets):
            st.error("Un projet avec ce nom existe déjà")
        else:
            projets.append({
                "projet": nom_new.strip(),
                "couleur": couleur_defaut,
                "client": client_new.strip(),
                "description": description_new.strip(),
                "sous_taches": []
            })
            nouveau_sha = sauvegarder_projets_github(
                projets, st.session_state.projets_sha
            )
            st.session_state.projets_sha = nouveau_sha
            st.session_state.msg_succes = f"Projet « {nom_new.strip()} » créé et sauvegardé ! Dépliez-le ci-dessus pour ajouter des sous-tâches et choisir sa couleur."
            st.rerun()

