import streamlit as st
from datetime import date, timedelta
from donnees import sauvegarder_projets_github, sauvegarder_assignations_github

#-------------AFFICHAGE----------------------
COULEURS_PALETTE = {
    "Rouge":    "#FF6C6C",
    "Orange":   "#FFBD45",
    "Bleu":     "#63CDEB",
    "Vert":     "#6BCB77",
    "Violet":   "#A78BFA",
    "Rose":     "#F472B6",
    "Gris":     "#94A3B8",
}

TACHES_TYPES = [
    "Pré étude", "Etude", "Construction", "Serrurerie",
    "Sculpture", "Tapisserie", "Peinture", "CU", "Montage", "Autre"
]

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
            key_expander = f"__xpnd_p{i}__"
            if key_expander not in st.session_state:
                st.session_state[key_expander] = False

            with st.expander(
                f"**{projet['projet']}** - {len(projet['sous_taches'])} sous-tache(s)",
                expanded=st.session_state[key_expander]
            ):
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
                    nom_actuel = st_data["tache"]

                    # Si le nom est hors liste, on l'ajoute comme option unique pour ce selectbox
                    options_j = TACHES_TYPES[:]
                    if nom_actuel not in TACHES_TYPES:
                        options_j = [nom_actuel] + TACHES_TYPES
                    index_type = options_j.index(nom_actuel) if nom_actuel in options_j else options_j.index("Autre")

                    cols = st.columns([3, 2, 2, 0.6])
                    with cols[0]:
                        choix_type = st.selectbox(
                            "Type",
                            options=options_j,
                            index=index_type,
                            key=f"tache_type_{i}_{j}",
                            label_visibility="collapsed",
                            on_change=lambda k=key_expander: st.session_state.__setitem__(k, True)
                        )
                        if choix_type == "Autre":
                            nom_custom = st.text_input(
                                "Nom personnalisé",
                                key=f"tache_custom_{i}_{j}",
                                placeholder="Nom de la tâche...",
                                label_visibility="collapsed"
                            )
                            if st.button("Valider", key=f"tache_valider_{i}_{j}"):
                                if nom_custom.strip():
                                    sous_taches[j]["tache"] = nom_custom.strip()
                                    # Vider le champ texte et forcer le selectbox à se reconstruire
                                    if f"tache_custom_{i}_{j}" in st.session_state:
                                        del st.session_state[f"tache_custom_{i}_{j}"]
                                    if f"tache_type_{i}_{j}" in st.session_state:
                                        del st.session_state[f"tache_type_{i}_{j}"]
                                    st.session_state[key_expander] = True
                                    st.rerun()
                        else:
                            sous_taches[j]["tache"] = choix_type
                    with cols[1]:
                        sous_taches[j]["start"] = st.date_input(
                            "Début",
                            value=date.fromisoformat(st_data["start"]),
                            key=f"start_{i}_{j}",
                            label_visibility="collapsed",
                            on_change=lambda k=key_expander: st.session_state.__setitem__(k, True)
                        ).isoformat()
                    with cols[2]:
                        sous_taches[j]["end"] = st.date_input(
                            "Fin",
                            value=date.fromisoformat(st_data["end"]),
                            key=f"end_{i}_{j}",
                            label_visibility="collapsed",
                            on_change=lambda k=key_expander: st.session_state.__setitem__(k, True)
                        ).isoformat()
                    with cols[3]:
                        if st.button("🗑️", key=f"del_st_{i}_{j}", help="Supprimer cette tâche"):
                            a_supp = j

                if a_supp is not None:
                    sous_taches.pop(a_supp)
                    st.session_state[key_expander] = True
                    st.rerun()

                # ---------------- AJOUT SOUS-TÂCHE -----------------------
                if st.button("➕ Ajouter une sous-tâche", key=f"add_st_{i}"):
                    if sous_taches:
                        last_end = date.fromisoformat(sous_taches[-1]["end"])
                    else:
                        last_end = date.today()
                    sous_taches.append({
                        "tache": "Pré étude",
                        "start": last_end.isoformat(),
                        "end": (last_end + timedelta(weeks=2)).isoformat(),
                    })
                    st.session_state[key_expander] = True
                    st.rerun()

                # -------------- BOUTONS --------------------------
                col_save, col_del = st.columns([1, 1])
                with col_save:
                    if st.button("✅ Enregistrer les modifications", key=f"save_{i}"):
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
