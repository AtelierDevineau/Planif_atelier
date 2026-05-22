import streamlit as st
import pandas as pd
from donnees import POSTES, sauvegarder_ressources_github, sauvegarder_assignations_github, get_couleur_poste
from Logique import recalculer_dispos

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

# -------------------------------------------------------
# ONGLET PRINCIPAL
# -------------------------------------------------------

def crea_ress_tab():
    st.markdown(STYLE, unsafe_allow_html=True)
    st.subheader("Gestion des ressources")

    if st.session_state.get("ress_modifiees"):
        st.warning("❌ Modifications non sauvegardées")
    if st.session_state.get("msg_succes_ress"):
        st.success(st.session_state.msg_succes_ress)
        st.session_state.msg_succes_ress = None

    ressources = st.session_state.Ressources_base

    if "ressources_edit" not in st.session_state:
        st.session_state.ressources_edit = [r.copy() for r in ressources]

    ressources_edit = st.session_state.ressources_edit

    col_gauche, col_droite = st.columns(2)
    colonnes = [col_gauche, col_droite]

    for idx_poste, poste in enumerate(POSTES):
        couleur = get_couleur_poste(poste)
        with colonnes[idx_poste % 2]:
            st.markdown(
                f"""<div style="border: 2px solid {couleur}; border-radius: 8px;
                padding: 12px; margin-bottom: 12px;">
                <span style="font-weight: bold; color: {couleur};
                font-size: 1.05em;">{poste}</span>
                </div>""",
                unsafe_allow_html=True
            )
            with st.container(border=True):
                ress_poste = [r for r in ressources_edit if r["Poste"] == poste]

                if ress_poste:
                    colonnes_df = ["Nom", "Contrat", "Dispo_base"]
                    if poste == "Autres":
                        # S'assurer que la colonne Precision existe pour toutes les lignes
                        for r in ress_poste:
                            r.setdefault("Precision", "")
                        colonnes_df = ["Nom", "Precision", "Contrat", "Dispo_base"]

                    df = pd.DataFrame(ress_poste)[colonnes_df]
                    column_config = {
                        "Nom": st.column_config.TextColumn("Nom", width="small"),
                        "Contrat": st.column_config.SelectboxColumn(
                            "Contrat",
                            options=["Permanent", "Intermittent"],
                            width="small"
                        ),
                        "Dispo_base": st.column_config.NumberColumn(
                            "Dispo (%)", min_value=0, max_value=100, step=5, width="small"
                        ),
                    }
                    if poste == "Autres":
                        column_config["Precision"] = st.column_config.TextColumn(
                            "Précision", width="small"
                        )
                    df_edit = st.data_editor(
                        df,
                        key=f"editor_{poste}",
                        column_config=column_config,
                        hide_index=True,
                        num_rows="fixed",
                        use_container_width=True,
                    )

                    for idx, row in df_edit.iterrows():
                        nom_original = ress_poste[idx]["Nom"]
                        nom_nouveau = row["Nom"]
                        dispo_nouvelle = int(row["Dispo_base"])
                        contrat_nouveau = row["Contrat"]

                        if nom_nouveau != nom_original:
                            noms_assignes = [
                                a["Nom"]
                                for data in st.session_state.Data_proj.values()
                                for sous_tache in data.values()
                                for a in (sous_tache.get("Assignations", []) if isinstance(sous_tache, dict) else [])
                            ]
                            if nom_original in noms_assignes:
                                st.warning(
                                    f"⚠️ **{nom_original}** est assigné(e) à un ou plusieurs projets. "
                                    f"Renommer en **{nom_nouveau}** ne mettra pas à jour les assignations existantes."
                                )

                        for r in ressources_edit:
                            if r["Nom"] == nom_original and r["Poste"] == poste:
                                r["Nom"] = nom_nouveau
                                r["Dispo_base"] = dispo_nouvelle
                                r["Contrat"] = contrat_nouveau
                                if poste == "Autres":
                                    r["Precision"] = row.get("Precision", "")
                                break

                    if ress_poste != [r for r in ressources_edit if r["Poste"] == poste]:
                        st.session_state.ress_modifiees = True

                    # --- Suppression : selectbox + emoji poubelle uniquement ---
                    noms_poste = [r["Nom"] for r in ress_poste]
                    col_sel, col_del = st.columns([5, 1])
                    with col_sel:
                        a_supprimer = st.selectbox(
                            "Supprimer :",
                            options=["—"] + noms_poste,
                            key=f"suppr_select_{poste}",
                            label_visibility="collapsed"
                        )
                    with col_del:
                        if st.button("🗑️", key=f"suppr_btn_{poste}", type="secondary", help="Supprimer cette ressource"):
                            if a_supprimer != "—":
                                noms_assignes = [
                                    a["Nom"]
                                    for data in st.session_state.Data_proj.values()
                                    for sous_tache in data.values()
                                    for a in (sous_tache.get("Assignations", []) if isinstance(sous_tache, dict) else [])
                                ]
                                assignations_modifiees = False

                                if a_supprimer in noms_assignes:
                                    projets_concernes = [
                                        proj for proj, data in st.session_state.Data_proj.items()
                                        if any(
                                            a["Nom"] == a_supprimer
                                            for sous_tache in data.values()
                                            for a in (sous_tache.get("Assignations", []) if isinstance(sous_tache, dict) else [])
                                        )
                                    ]
                                    st.warning(
                                        f"⚠️ **{a_supprimer}** est assigné(e) au(x) projet(s) : "
                                        f"**{', '.join(projets_concernes)}**. "
                                        f"Cette ressource sera retirée de ces assignations."
                                    )
                                    for proj, data in st.session_state.Data_proj.items():
                                        for nom_st, sous_tache in data.items():
                                            if isinstance(sous_tache, dict):
                                                assignations = sous_tache.get("Assignations", [])
                                                nouvelles = [a for a in assignations if a["Nom"] != a_supprimer]
                                                if len(nouvelles) != len(assignations):
                                                    st.session_state.Data_proj[proj][nom_st]["Assignations"] = nouvelles
                                                    st.session_state.Data_proj[proj][nom_st]["Nb_ressources"] = len(nouvelles)
                                                    assignations_modifiees = True

                                ressources_edit[:] = [r for r in ressources_edit if r["Nom"] != a_supprimer]
                                st.session_state.ress_modifiees = True

                                if assignations_modifiees:
                                    nouveau_sha = sauvegarder_assignations_github(
                                        st.session_state.Data_proj,
                                        st.session_state.assignations_sha
                                    )
                                    st.session_state.assignations_sha = nouveau_sha

                                st.rerun()

                # --- Ajout d'une nouvelle ressource ---
                key_exp_ajout = f"expander_ajout_{poste}"
                if key_exp_ajout not in st.session_state:
                    st.session_state[key_exp_ajout] = False

                def garder_expander_ress_ouvert(key=key_exp_ajout):
                    st.session_state[key] = True

                with st.expander("➕ Ajouter une ressource", expanded=st.session_state[key_exp_ajout]):
                    st.session_state[key_exp_ajout] = False  # reset après rendu

                    nouveau_nom = st.text_input(
                        "Nom",
                        key=f"new_nom_{poste}",
                        placeholder="Nom et prénom"
                    )
                    nouveau_contrat = st.radio(
                        "Type de contrat",
                        options=["Permanent", "Intermittent"],
                        key=f"new_contrat_{poste}",
                        horizontal=True,
                        on_change=garder_expander_ress_ouvert,
                    )
                    mi_temps = st.checkbox(
                        "Mi-temps (dispo 50%)",
                        key=f"new_mitemps_{poste}",
                        on_change=garder_expander_ress_ouvert,
                    )
                    nouvelle_dispo = 50 if mi_temps else 100
                    precision_poste = ""
                    if poste == "Autres":
                        precision_poste = st.text_input(
                            "Précision sur le poste",
                            key=f"new_precision_{poste}",
                            placeholder="Ex : Électricien, Peintre..."
                        )
                    if st.button("Ajouter", key=f"add_btn_{poste}", type="primary"):
                        if not nouveau_nom.strip():
                            st.error("Merci de saisir un nom.")
                        elif any(r["Nom"] == nouveau_nom.strip() for r in ressources_edit):
                            st.error(f"**{nouveau_nom.strip()}** existe déjà.")
                        else:
                            ressources_edit.append({
                                "Nom": nouveau_nom.strip(),
                                "Poste": poste,
                                "Contrat": nouveau_contrat,
                                "Dispo_base": nouvelle_dispo,
                                "Precision": precision_poste.strip(),
                                "absences": []
                            })
                            st.session_state.ress_modifiees = True
                            st.rerun()

    # --- Bouton de sauvegarde global ---
    st.divider()
    if st.button("✅ Enregistrer toutes les modifications", type="primary"):
        nouveau_sha = sauvegarder_ressources_github(
            ressources_edit, st.session_state.ressources_sha
        )
        st.session_state.ressources_sha = nouveau_sha

        st.session_state.Ressources_base = [r.copy() for r in ressources_edit]
        st.session_state.Ressources = [
            {"Nom": r["Nom"], "Dispo_restante": r["Dispo_base"]}
            for r in ressources_edit
        ]
        recalculer_dispos(
            st.session_state.Data_proj,
            st.session_state.Ressources,
            st.session_state.Ressources_base
        )

        st.session_state.ress_modifiees = False
        st.session_state.ressources_edit = [r.copy() for r in ressources_edit]
        st.session_state.msg_succes_ress = "Ressources mises à jour et sauvegardées."
        st.rerun()
