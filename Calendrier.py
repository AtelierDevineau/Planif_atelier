import streamlit as st
from streamlit_calendar import calendar
from datetime import date, timedelta
from donnees import Options_cal, build_absences_cal, sauvegarder_ressources_github

# -------------------------------------------------------
# UTILITAIRES
# -------------------------------------------------------

def get_lundis(date_debut, date_fin):
    lundis = []
    cur = date_debut - timedelta(days=date_debut.weekday())
    while cur <= date_fin:
        lundis.append(cur)
        cur += timedelta(weeks=1)
    return lundis

def get_jours(date_debut, date_fin):
    jours = []
    cur = date_debut
    while cur <= date_fin:
        jours.append(cur)
        cur += timedelta(days=1)
    return jours

def get_noms_assignes(nom_projet, nom_tache, data_proj):
    data_st = data_proj.get(nom_projet, {}).get(nom_tache, {})
    return [a["Nom"] for a in data_st.get("Assignations", [])]


# -------------------------------------------------------
# CONSTRUCTION DU GANTT TABLEAU
# -------------------------------------------------------

def gantt_tableau(projets_data, nb_semaines, data_proj):
    today = date.today()
    date_debut_grille = today
    date_fin_grille = today + timedelta(weeks=nb_semaines)

    jours = get_jours(date_debut_grille, date_fin_grille)
    lundis = get_lundis(date_debut_grille, date_fin_grille)
    nb_jours = len(jours)

    # Index de chaque jour pour retrouver sa position rapidement
    jour_index = {j: i for i, j in enumerate(jours)}

    css = """
    <style>
    .gantt-wrap { overflow-x: auto; width: 100%; }
    .gantt-table {
        border-collapse: collapse;
        width: 100%;
        min-width: 700px;
        table-layout: fixed;
        font-size: 0.82em;
    }
    /* Header semaine */
    .gh {
        text-align: left;
        padding: 4px 6px;
        font-weight: bold;
        font-size: 0.85em;
        background: #f5f5f5;
        border-right: 2px solid #999;
        border-bottom: 2px solid #ccc;
        white-space: nowrap;
        overflow: hidden;
    }
    /* Cellule vide de grille */
    .gc {
        padding: 0;
        height: 24px;
        border-right: 1px solid #f0f0f0;
        border-top: none;
        border-bottom: none;
        border-left: none;
    }
    /* Cellule vide lundi (séparateur semaine) */
    .gcl {
        padding: 0;
        height: 24px;
        border-right: 2px solid #999;
        border-top: none;
        border-bottom: none;
        border-left: none;
    }
    /* Cellule fusionnée — ligne 1 (nom tâche) */
    .gb1 {
        padding: 0 8px;
        height: 24px;
        vertical-align: middle;
        text-align: center;
        font-weight: bold;
        font-size: 0.85em;
        color: #222;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        border: none;
    }
    /* Cellule fusionnée — ligne 2 (noms ressources) */
    .gb2 {
        padding: 0 8px;
        height: 20px;
        vertical-align: middle;
        font-size: 0.78em;
        color: #333;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        border: none;
    }
    /* Séparation entre projets */
    .gsep td {
        border-bottom: 2px solid #ccc !important;
    }
    /* Cellules vides avant/après la barre sur ligne 2 */
    .gc2 {
        padding: 0;
        height: 20px;
        border-right: 1px solid #f0f0f0;
        border-top: none;
        border-bottom: none;
        border-left: none;
    }
    .gcl2 {
        padding: 0;
        height: 20px;
        border-right: 2px solid #999;
        border-top: none;
        border-bottom: none;
        border-left: none;
    }
    </style>
    """

    # ── HEADER ───────────────────────────────────────────────────────────────
    header = '<tr>'
    for lundi in lundis:
        jours_sem = [j for j in jours if lundi <= j < lundi + timedelta(weeks=1)]
        if not jours_sem:
            continue
        label = f"Lun. {lundi.day}/{lundi.month}"
        header += f'<th colspan="{len(jours_sem)}" class="gh">{label}</th>'
    header += '</tr>'

    # ── LIGNES ───────────────────────────────────────────────────────────────
    rows = ""

    for proj_idx, projet in enumerate(projets_data):
        nom_projet = projet["projet"]
        couleur = projet["couleur"]
        # Ligne 2 : même couleur que ligne 1
        couleur_sub = couleur

        for st_idx, sous_tache in enumerate(projet["sous_taches"]):
            nom_st = sous_tache["tache"]
            debut_st = date.fromisoformat(sous_tache["start"])
            fin_st = date.fromisoformat(sous_tache["end"])
            noms = get_noms_assignes(nom_projet, nom_st, data_proj)
            noms_str = ", ".join(noms)

            is_last = st_idx == len(projet["sous_taches"]) - 1

            # Intersection avec la fenêtre visible
            debut_visible = max(debut_st, date_debut_grille)
            fin_visible = min(fin_st, date_fin_grille)
            dans_fenetre = debut_visible < fin_visible

            # Index de début et fin dans la grille
            if dans_fenetre:
                idx_debut = jour_index.get(debut_visible, 0)
                idx_fin = jour_index.get(fin_visible, nb_jours)
                colspan_barre = idx_fin - idx_debut
            else:
                idx_debut = None
                colspan_barre = 0

            # ── Ligne 1 : nom de la sous-tâche dans la barre ──
            row1 = '<tr>'
            col = 0
            while col < nb_jours:
                jour = jours[col]
                est_lundi = jour.weekday() == 0
                cls_vide = "gcl" if est_lundi else "gc"

                if dans_fenetre and col == idx_debut and colspan_barre > 0:
                    # Bordure gauche si la barre commence un lundi
                    border_left = "border-left: 2px solid #999;" if est_lundi else ""
                    # Bordure droite si la barre se termine juste avant un lundi
                    jour_fin_barre = jours[min(idx_debut + colspan_barre, nb_jours - 1)]
                    border_right = "border-right: 2px solid #999;" if jour_fin_barre.weekday() == 0 else ""
                    row1 += (
                        f'<td colspan="{colspan_barre}" class="gb1" '
                        f'style="background:{couleur};{border_left}{border_right}">{nom_st}</td>'
                    )
                    col += colspan_barre
                elif dans_fenetre and idx_debut is not None and idx_debut <= col < idx_debut + colspan_barre:
                    col += 1
                    continue
                else:
                    row1 += f'<td class="{cls_vide}"></td>'
                    col += 1
            row1 += '</tr>'

            # ── Ligne 2 : noms des ressources ──
            sep_cls = ' class="gsep"' if is_last else ''
            row2 = f'<tr{sep_cls}>'
            col = 0
            while col < nb_jours:
                jour = jours[col]
                est_lundi = jour.weekday() == 0
                cls_vide = "gcl2" if est_lundi else "gc2"

                if dans_fenetre and col == idx_debut and colspan_barre > 0:
                    border_left = "border-left: 2px solid #999;" if est_lundi else ""
                    jour_fin_barre = jours[min(idx_debut + colspan_barre, nb_jours - 1)]
                    border_right = "border-right: 2px solid #999;" if jour_fin_barre.weekday() == 0 else ""
                    row2 += (
                        f'<td colspan="{colspan_barre}" class="gb2" '
                        f'style="background:{couleur_sub};{border_left}{border_right}">{noms_str}</td>'
                    )
                    col += colspan_barre
                elif dans_fenetre and idx_debut is not None and idx_debut <= col < idx_debut + colspan_barre:
                    col += 1
                    continue
                else:
                    row2 += f'<td class="{cls_vide}"></td>'
                    col += 1
            row2 += '</tr>'

            rows += row1 + row2

    return f"""
    {css}
    <div class="gantt-wrap">
    <table class="gantt-table">
        <thead>{header}</thead>
        <tbody>{rows}</tbody>
    </table>
    </div>
    """


# -------------------------------------------------------
# ONGLET CALENDRIER
# -------------------------------------------------------

def calendrier_tab():
    st.subheader('Calendrier')
    selection = st.pills(
        " ",
        ["Projets", "Absences"],
        selection_mode="single",
        default="Projets"
    )

    if selection == "Projets":
        options_semaines = {"4 semaines": 4, "8 semaines": 8, "12 semaines": 12}
        choix_semaines = st.segmented_control(
            "Fenêtre d'affichage :",
            options=list(options_semaines.keys()),
            selection_mode="single",
            default="8 semaines"
        )
        nb_semaines = options_semaines[choix_semaines]
        projets = st.session_state.Projets_gantt
        data_proj = st.session_state.Data_proj

        st.markdown("#### Vue d'ensemble")
        if projets:
            st.markdown(gantt_tableau(projets, nb_semaines, data_proj), unsafe_allow_html=True)
        else:
            st.info("Aucun projet à afficher.")

        st.markdown("#### Vue détaillée")
        if projets:
            noms_projets = [p["projet"] for p in projets]
            projet_choisi = st.selectbox(
                "Sélectionner un projet :",
                options=noms_projets,
                key="gantt_detail_projet"
            )
            projet_data = next(p for p in projets if p["projet"] == projet_choisi)
            if projet_data["sous_taches"]:
                st.markdown(gantt_tableau([projet_data], nb_semaines, data_proj), unsafe_allow_html=True)
            else:
                st.info("Ce projet n'a pas encore de sous-tâches.")

    if selection == "Absences":
        with st.form("form_absence", clear_on_submit=True):
            noms_ressources = [r["Nom"] for r in st.session_state.Ressources_base]
            col_nom, col_debut, col_fin = st.columns([2, 1, 1])
            with col_nom:
                nom_choisi = st.selectbox("Ressource", options=noms_ressources)
            with col_debut:
                date_debut = st.date_input("Début", value=date.today())
            with col_fin:
                date_fin = st.date_input("Fin", value=date.today() + timedelta(days=7))
            submitted = st.form_submit_button("➕ Ajouter l'absence")

        if submitted:
            if date_fin <= date_debut:
                st.error("La date de fin doit être après la date de début.")
            else:
                for r in st.session_state.Ressources_base:
                    if r["Nom"] == nom_choisi:
                        if "absences" not in r:
                            r["absences"] = []
                        r["absences"].append({
                            "start": date_debut.isoformat(),
                            "end": date_fin.isoformat()
                        })
                        break
                nouveau_sha = sauvegarder_ressources_github(
                    st.session_state.Ressources_base,
                    st.session_state.ressources_sha
                )
                st.session_state.ressources_sha = nouveau_sha
                st.session_state.msg_succes = f"Absence de {nom_choisi} ajoutée."
                st.rerun()

        if st.session_state.get("msg_succes"):
            st.success(st.session_state.msg_succes)
            st.session_state.msg_succes = None

        absences_cal = build_absences_cal()
        calendar(events=absences_cal, options=Options_cal)
