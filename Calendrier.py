import streamlit as st
from streamlit_calendar import calendar
from datetime import date, timedelta
from donnees import Options_cal, build_absences_cal, sauvegarder_ressources_github

# -------------------------------------------------------
# UTILITAIRES
# -------------------------------------------------------

def get_semaines(date_debut, date_fin):
    """Retourne la liste des lundis entre date_debut et date_fin."""
    lundis = []
    cur = date_debut - timedelta(days=date_debut.weekday())
    while cur <= date_fin:
        lundis.append(cur)
        cur += timedelta(weeks=1)
    return lundis

def get_jours(date_debut, date_fin):
    """Retourne tous les jours entre date_debut et date_fin."""
    jours = []
    cur = date_debut
    while cur <= date_fin:
        jours.append(cur)
        cur += timedelta(days=1)
    return jours

def position_jour(jour, date_debut_grille):
    """Retourne l'index de colonne (en jours) d'un jour par rapport au début de la grille."""
    return (jour - date_debut_grille).days

def get_noms_assignes(nom_projet, nom_tache, data_proj):
    """Retourne la liste des noms assignés à une sous-tâche."""
    data_st = data_proj.get(nom_projet, {}).get(nom_tache, {})
    return [a["Nom"] for a in data_st.get("Assignations", [])]


# -------------------------------------------------------
# CONSTRUCTION DU GANTT TABLEAU
# -------------------------------------------------------

def gantt_tableau(projets_data, nb_semaines, data_proj):
    """
    Génère un tableau HTML style Excel représentant le Gantt.
    - Colonnes = semaines (header) subdivisées en jours (lignes verticales légères)
    - 2 lignes par sous-tâche : ligne couleur + ligne noms
    - Les deux lignes semblent n'en former qu'une seule
    """
    today = date.today()
    date_debut = today
    date_fin = today + timedelta(weeks=nb_semaines)

    lundis = get_semaines(date_debut, date_fin)
    jours = get_jours(date_debut, date_fin)
    nb_jours = len(jours)

    # Largeur en % par jour
    pct_jour = 100 / nb_jours

    # ── CSS ──────────────────────────────────────────────────────────────────
    css = """
    <style>
    .gantt-wrap {
        overflow-x: auto;
        width: 100%;
    }
    .gantt-table {
        border-collapse: collapse;
        width: 100%;
        min-width: 700px;
        table-layout: fixed;
        font-size: 0.82em;
    }
    /* Colonne label à gauche */
    .gantt-table .col-label {
        width: 140px;
        min-width: 140px;
        max-width: 140px;
    }
    /* Cellule label sous-tâche */
    .gantt-label {
        padding: 2px 8px;
        font-weight: bold;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        border-right: 1px solid #ddd;
        vertical-align: middle;
    }
    /* Cellule label vide (ligne noms) */
    .gantt-label-sub {
        padding: 2px 8px;
        border-right: 1px solid #ddd;
        border-bottom: 2px solid #ccc;
    }
    /* Cellule de la grille (jour) */
    .gantt-cell {
        padding: 0;
        position: relative;
        border-right: 1px solid #f0f0f0; /* ligne verticale jour très légère */
    }
    /* Séparateur semaine un peu plus marqué */
    .gantt-cell-lundi {
        border-right: 1px solid #d0d0d0;
    }
    /* Séparateur de ligne entre projets */
    .gantt-row-sep td {
        border-bottom: 2px solid #ccc;
    }
    /* Header semaine */
    .gantt-header-sem {
        text-align: left;
        padding: 4px 6px;
        font-weight: bold;
        font-size: 0.85em;
        background: #f5f5f5;
        border-right: 1px solid #d0d0d0;
        border-bottom: 1px solid #ccc;
        white-space: nowrap;
        overflow: hidden;
    }
    /* Barre colorée dans la cellule */
    .gantt-bar {
        width: 100%;
        height: 100%;
        min-height: 22px;
    }
    /* Ligne noms : même couleur mais plus transparente */
    .gantt-bar-sub {
        width: 100%;
        height: 100%;
        min-height: 18px;
        display: flex;
        align-items: center;
        padding: 0 4px;
        font-size: 0.78em;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        color: #222;
    }
    </style>
    """

    # ── HEADER ───────────────────────────────────────────────────────────────
    header = '<tr><th class="col-label gantt-header-sem"></th>'
    for lundi in lundis:
        # Compter les jours de cette semaine dans la fenêtre
        jours_semaine = [j for j in jours if j >= lundi and j < lundi + timedelta(weeks=1)]
        if not jours_semaine:
            continue
        colspan = len(jours_semaine)
        label = f"Lun. {lundi.day}/{lundi.month}"
        header += f'<th colspan="{colspan}" class="gantt-header-sem">{label}</th>'
    header += '</tr>'

    # ── LIGNES ───────────────────────────────────────────────────────────────
    rows = ""
    for proj_idx, projet in enumerate(projets_data):
        nom_projet = projet["projet"]
        couleur = projet["couleur"]
        # Couleur plus claire pour la ligne noms (opacité simulée en hex)
        couleur_sub = couleur + "99"  # ~60% opacité en RGBA hex

        for st_idx, sous_tache in enumerate(projet["sous_taches"]):
            nom_st = sous_tache["tache"]
            debut_st = date.fromisoformat(sous_tache["start"])
            fin_st = date.fromisoformat(sous_tache["end"])
            noms = get_noms_assignes(nom_projet, nom_st, data_proj)
            noms_str = ", ".join(noms) if noms else ""

            # Est-ce la dernière sous-tâche du projet ?
            is_last = st_idx == len(projet["sous_taches"]) - 1

            # ── Ligne 1 : barre colorée ──
            row1 = f'<tr><td class="gantt-label col-label">{nom_st}</td>'
            for jour in jours:
                dans_tache = debut_st <= jour < fin_st
                est_lundi = jour.weekday() == 0
                cls = "gantt-cell-lundi" if est_lundi else "gantt-cell"
                if dans_tache:
                    row1 += f'<td class="{cls}"><div class="gantt-bar" style="background:{couleur};"></div></td>'
                else:
                    row1 += f'<td class="{cls}"></td>'
            row1 += '</tr>'

            # ── Ligne 2 : noms assignés ──
            sep_cls = " gantt-row-sep" if is_last else ""
            row2 = f'<tr class="{sep_cls.strip()}"><td class="gantt-label-sub col-label"></td>'
            # On cherche les colonnes de début et fin pour placer le texte
            for jour in jours:
                dans_tache = debut_st <= jour < fin_st
                est_lundi = jour.weekday() == 0
                cls = "gantt-cell-lundi" if est_lundi else "gantt-cell"
                # Afficher le texte uniquement dans la première cellule de la barre
                if dans_tache and jour == max(debut_st, date_debut):
                    row2 += f'<td class="{cls}"><div class="gantt-bar-sub" style="background:{couleur_sub};">{noms_str}</div></td>'
                elif dans_tache:
                    row2 += f'<td class="{cls}"><div class="gantt-bar-sub" style="background:{couleur_sub};"></div></td>'
                else:
                    row2 += f'<td class="{cls}"></td>'
            row2 += '</tr>'

            rows += row1 + row2

    html = f"""
    {css}
    <div class="gantt-wrap">
    <table class="gantt-table">
        <thead>{header}</thead>
        <tbody>{rows}</tbody>
    </table>
    </div>
    """
    return html


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

        # ---- Vue d'ensemble ----
        st.markdown("#### Vue d'ensemble")
        if projets:
            st.markdown(
                gantt_tableau(projets, nb_semaines, data_proj),
                unsafe_allow_html=True
            )
        else:
            st.info("Aucun projet à afficher.")

        # ---- Vue détaillée par projet ----
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
                st.markdown(
                    gantt_tableau([projet_data], nb_semaines, data_proj),
                    unsafe_allow_html=True
                )
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
