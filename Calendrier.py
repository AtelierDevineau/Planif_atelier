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
    """
    Gantt en tableau HTML.
    - Une colonne séparateur grise de 3px entre chaque semaine (pas de bordure CSS)
    - 2 lignes par sous-tâche : couleur pleine (nom) + couleur ~60% (ressources)
    - Cellules fusionnées sur la durée de la tâche
    """
    today = date.today()
    date_debut_grille = today
    date_fin_grille = today + timedelta(weeks=nb_semaines)

    jours = get_jours(date_debut_grille, date_fin_grille)
    lundis = get_lundis(date_debut_grille, date_fin_grille)
    nb_jours = len(jours)
    jour_index = {j: i for i, j in enumerate(jours)}

    # On construit une liste de "colonnes" : soit un jour, soit un séparateur
    # Chaque élément : {"type": "jour", "jour": date} ou {"type": "sep"}
    colonnes = []
    for jour in jours:
        if jour.weekday() == 0 and jour != jours[0]:  # lundi sauf le premier
            colonnes.append({"type": "sep"})
        colonnes.append({"type": "jour", "jour": jour})

    # Reconstruire l'index colonne → index dans colonnes (pour les jours uniquement)
    col_index = {}  # jour → index dans colonnes
    for i, col in enumerate(colonnes):
        if col["type"] == "jour":
            col_index[col["jour"]] = i

    nb_cols = len(colonnes)

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
    .gh {
        text-align: left;
        padding: 4px 6px;
        font-weight: bold;
        font-size: 0.85em;
        background: #f5f5f5;
        border-bottom: 2px solid #ccc;
        white-space: nowrap;
        overflow: hidden;
        border-right: none;
        border-left: none;
        border-top: none;
    }
    /* Colonne séparateur header */
    .gh-sep {
        background: #999;
        width: 3px;
        padding: 0;
        border: none;
    }
    .gc {
        padding: 0;
        height: 24px;
        border-right: 1px solid #f0f0f0;
        border-top: none;
        border-bottom: none;
        border-left: none;
    }
    /* Colonne séparateur dans les lignes */
    .gc-sep {
        background: #bbb;
        width: 3px;
        padding: 0;
        border: none;
        height: 24px;
    }
    .gc-sep2 {
        background: #bbb;
        width: 3px;
        padding: 0;
        border: none;
        height: 20px;
    }
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
    .gsep td {
        border-bottom: 2px solid #ccc !important;
    }
    .gc2 {
        padding: 0;
        height: 20px;
        border-right: 1px solid #f0f0f0;
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
        if lundi != lundis[0]:
            header += '<th class="gh-sep"></th>'
        label = f"Lun. {lundi.day}/{lundi.month}"
        header += f'<th colspan="{len(jours_sem)}" class="gh">{label}</th>'
    header += '</tr>'

    # ── LIGNES ───────────────────────────────────────────────────────────────
    rows = ""

    for projet in projets_data:
        nom_projet = projet["projet"]
        couleur = projet["couleur"]
        couleur_sub = couleur + "99"

        for st_idx, sous_tache in enumerate(projet["sous_taches"]):
            nom_st = sous_tache["tache"]
            debut_st = date.fromisoformat(sous_tache["start"])
            fin_st = date.fromisoformat(sous_tache["end"])
            noms = get_noms_assignes(nom_projet, nom_st, data_proj)
            noms_str = ", ".join(noms)
            is_last = st_idx == len(projet["sous_taches"]) - 1

            debut_visible = max(debut_st, date_debut_grille)
            fin_visible = min(fin_st, date_fin_grille)
            dans_fenetre = debut_visible < fin_visible

            if dans_fenetre:
                ci_debut = col_index.get(debut_visible, 0)
                ci_fin = col_index.get(fin_visible, nb_cols)
                # colspan = nombre de colonnes entre ci_debut et ci_fin
                # (inclut les séparateurs éventuels à l'intérieur)
                colspan_barre = ci_fin - ci_debut
            else:
                ci_debut = None
                colspan_barre = 0

            # ── Ligne 1 ──
            row1 = '<tr>'
            ci = 0
            while ci < nb_cols:
                col = colonnes[ci]
                if col["type"] == "sep":
                    row1 += '<td class="gc-sep"></td>'
                    ci += 1
                elif dans_fenetre and ci == ci_debut and colspan_barre > 0:
                    row1 += (
                        f'<td colspan="{colspan_barre}" class="gb1" '
                        f'style="background:{couleur};">{nom_st}</td>'
                    )
                    ci += colspan_barre
                else:
                    row1 += '<td class="gc"></td>'
                    ci += 1
            row1 += '</tr>'

            # ── Ligne 2 ──
            sep_cls = ' class="gsep"' if is_last else ''
            row2 = f'<tr{sep_cls}>'
            ci = 0
            while ci < nb_cols:
                col = colonnes[ci]
                if col["type"] == "sep":
                    row2 += '<td class="gc-sep2"></td>'
                    ci += 1
                elif dans_fenetre and ci == ci_debut and colspan_barre > 0:
                    row2 += (
                        f'<td colspan="{colspan_barre}" class="gb2" '
                        f'style="background:{couleur_sub};">{noms_str}</td>'
                    )
                    ci += colspan_barre
                else:
                    row2 += '<td class="gc2"></td>'
                    ci += 1
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
