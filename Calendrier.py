import streamlit as st
import streamlit.components.v1 as components
from streamlit_calendar import calendar
from datetime import date, timedelta
from donnees import Options_cal, build_absences_cal, sauvegarder_ressources_github
from donnees import COULEURS_TACHES, ORDRE_TACHES, get_couleur_tache

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

def gantt_tableau(projets_data, data_proj, date_debut_grille, date_fin_grille, gantt_id="gantt", font_face=""):
    today = date.today()

    jours = get_jours(date_debut_grille, date_fin_grille)
    lundis = get_lundis(date_debut_grille, date_fin_grille)
    nb_jours = len(jours)
    jour_index = {j: i for i, j in enumerate(jours)}

    # Colonnes avec séparateurs de semaine
    colonnes = []
    for jour in jours:
        if jour.weekday() == 0 and jour != jours[0]:
            colonnes.append({"type": "sep"})
        colonnes.append({"type": "jour", "jour": jour})

    col_index = {}
    for i, col in enumerate(colonnes):
        if col["type"] == "jour":
            col_index[col["jour"]] = i

    nb_cols = len(colonnes)
    nb_seps = sum(1 for c in colonnes if c["type"] == "sep")
    largeur_totale = nb_jours * 14 + nb_seps * 3

    # Regrouper toutes les sous-tâches par type
    # Structure : {type_tache: [(nom_projet, sous_tache_data), ...]}
    taches_par_type = {t: [] for t in ORDRE_TACHES}
    for projet in projets_data:
        nom_projet = projet["projet"]
        for sous_tache in projet["sous_taches"]:
            nom_tache = sous_tache["tache"]
            type_tache = nom_tache if nom_tache in ORDRE_TACHES else "Autre"
            taches_par_type[type_tache].append((nom_projet, sous_tache))

    # Scroll vers aujourd'hui
    if today >= date_debut_grille:
        jours_avant = (today - date_debut_grille).days
        seps_avant = sum(1 for j in jours if j <= today and j.weekday() == 0 and j != date_debut_grille)
        scroll_px = max(0, jours_avant * 14 + seps_avant * 3)
    else:
        scroll_px = 0

    css = f"""
    <style>
    {font_face}
    body, table, td, th {{
        font-family: 'GTWalsheim', sans-serif;
    }}
    .gantt-wrap {{ overflow-x: auto; width: 100%; }}
    .gantt-table {{
        border-collapse: separate;
        border-spacing: 0;
        width: {largeur_totale}px;
        table-layout: fixed;
        font-size: 0.82em;
    }}
    .gh {{
        text-align: left;
        padding: 4px 6px;
        font-weight: bold;
        font-size: 0.85em;
        background: #f5f5f5;
        border-bottom: 2px solid #ccc;
        border-top: none;
        border-right: none;
        border-left: none;
        white-space: nowrap;
        overflow: hidden;
    }}
    .gh-sep {{
        background: #999;
        width: 3px;
        padding: 0;
        border: none;
    }}
    .gc {{
        padding: 0;
        height: 24px;
        border-right: 1px solid #f0f0f0;
        border-top: none;
        border-bottom: none;
        border-left: none;
    }}
    .gc-sep {{
        background: #bbb;
        width: 3px;
        padding: 0;
        border: none;
        height: 24px;
    }}
    .gc-sep2 {{
        background: #bbb;
        width: 3px;
        padding: 0;
        border: none;
        height: 20px;
    }}
    .gb1 {{
        padding: 0 8px;
        height: 24px;
        vertical-align: middle;
        text-align: center;
        font-weight: bold;
        font-size: 0.85em;
        color: #fff;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        border: none;
    }}
    .gb1-dark {{
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
    }}
    .gb2 {{
        padding: 0 8px;
        height: 20px;
        vertical-align: middle;
        font-size: 0.78em;
        color: #333;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        border: none;
    }}
    .gsep td {{
        border-bottom: 2px solid #ccc !important;
    }}
    .gc2 {{
        padding: 0;
        height: 20px;
        border-right: 1px solid #f0f0f0;
        border-top: none;
        border-bottom: none;
        border-left: none;
    }}
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

    # ── COLGROUP ─────────────────────────────────────────────────────────────
    colgroup = '<colgroup>'
    for col in colonnes:
        if col["type"] == "sep":
            colgroup += '<col style="width:3px;min-width:3px;max-width:3px;">'
        else:
            colgroup += '<col style="width:14px;min-width:14px;">'
    colgroup += '</colgroup>'

    # ── LIGNES ───────────────────────────────────────────────────────────────
    rows = ""

    for type_idx, type_tache in enumerate(ORDRE_TACHES):
        taches = taches_par_type.get(type_tache, [])
        if not taches:
            continue

        couleur = COULEURS_TACHES.get(type_tache, "#A0A0A0")
        # Texte blanc sur couleurs sombres, noir sur claires
        couleurs_claires = {"#F1C84E", "#7EB8F7", "#A0C45A"}
        cls_texte = "gb1-dark" if couleur in couleurs_claires else "gb1"
        couleur_sub = couleur + "99"

        for st_idx, (nom_projet, sous_tache) in enumerate(taches):
            nom_tache = sous_tache["tache"]
            debut_st = date.fromisoformat(sous_tache["start"])
            fin_st = date.fromisoformat(sous_tache["end"])
            noms = get_noms_assignes(nom_projet, nom_tache, data_proj)
            noms_str = ", ".join(noms)

            is_last = st_idx == len(taches) - 1

            debut_visible = max(debut_st, date_debut_grille)
            fin_visible = min(fin_st, date_fin_grille)
            dans_fenetre = debut_visible < fin_visible

            if dans_fenetre:
                ci_debut = col_index.get(debut_visible, 0)
                ci_fin = col_index.get(fin_visible, nb_cols)
                colspan_barre = ci_fin - ci_debut
            else:
                ci_debut = None
                colspan_barre = 0

            # Ligne 1 : nom du projet dans la barre — cliquable
            row1 = '<tr>'
            ci = 0
            while ci < nb_cols:
                col = colonnes[ci]
                if col["type"] == "sep":
                    row1 += '<td class="gc-sep"></td>'
                    ci += 1
                elif dans_fenetre and ci == ci_debut and colspan_barre > 0:
                    # Encoder projet et tâche pour l'onclick
                    import json as _json
                    payload = _json.dumps({"projet": nom_projet, "tache": nom_tache})
                    payload_safe = payload.replace("'", "\\'")
                    row1 += (
                        f'<td colspan="{colspan_barre}" class="{cls_texte}" '
                        f'style="background:{couleur};cursor:pointer;" '
                        f'onclick="window.parent.postMessage({{type:\'gantt_click\',data:{payload}}},\'*\')">'
                        f'{nom_projet}</td>'
                    )
                    ci += colspan_barre
                else:
                    row1 += '<td class="gc"></td>'
                    ci += 1
            row1 += '</tr>'

            # Ligne 2 : noms des ressources
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

    # ── LEGENDE ──────────────────────────────────────────────────────────────
    types_presents = [t for t in ORDRE_TACHES if taches_par_type.get(t)]
    legende_html = '<div style="margin-top:12px;display:flex;flex-wrap:wrap;gap:12px;">'
    for t in types_presents:
        c = COULEURS_TACHES.get(t, "#A0A0A0")
        legende_html += (
            f'<span style="display:flex;align-items:center;gap:6px;font-size:0.85em;">'
            f'<span style="display:inline-block;width:16px;height:16px;'
            f'background:{c};border-radius:3px;"></span>{t}</span>'
        )
    legende_html += '</div>'

    html = f"""
    {css}
    <div class="gantt-wrap" id="{gantt_id}">
    <table class="gantt-table">
        {colgroup}
        <thead>{header}</thead>
        <tbody>{rows}</tbody>
    </table>
    </div>
    {legende_html}
    <script>
    setTimeout(function() {{
        var el = document.getElementById("{gantt_id}");
        if (el) {{ el.scrollLeft = {scroll_px}; }}
    }}, 300);
    </script>
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
        projets = st.session_state.Projets_gantt
        data_proj = st.session_state.Data_proj

        # Charger la police GT Walsheim
        import base64 as _b64, os as _os
        font_face = ""
        font_path = _os.path.join(_os.path.dirname(__file__), "fonts", "GT-Walsheim-Regular.ttf")
        try:
            with open(font_path, "rb") as f:
                font_b64 = _b64.b64encode(f.read()).decode("utf-8")
            font_face = f"""
            @font-face {{
                font-family: 'GTWalsheim';
                src: url(data:font/truetype;base64,{font_b64}) format('truetype');
            }}
            """
        except FileNotFoundError:
            pass

        # Plage de dates
        toutes_dates = [
            date.fromisoformat(st_data[cle])
            for p in projets
            for st_data in p.get("sous_taches", [])
            for cle in ("start", "end")
        ]
        today = date.today()
        if toutes_dates:
            date_debut_grille = min(min(toutes_dates), today) - timedelta(days=7)
            date_fin_grille = max(toutes_dates) + timedelta(days=7)
        else:
            date_debut_grille = today - timedelta(days=7)
            date_fin_grille = today + timedelta(weeks=12)

        st.markdown("#### Vue d'ensemble")
        if projets:
            html_global = gantt_tableau(projets, data_proj, date_debut_grille, date_fin_grille, "gantt_global", font_face)
            nb_lignes = sum(len(p.get("sous_taches", [])) for p in projets)
            components.html(html_global, height=max(300, 80 + nb_lignes * 50), scrolling=False)
        else:
            st.info("Aucun projet à afficher.")

        # Composant récepteur des clics sur le Gantt
        recepteur_html = """
        <script>
        window.addEventListener('message', function(e) {
            if (e.data && e.data.type === 'gantt_click') {
                var data = e.data.data;
                // Stocker dans un input caché pour que Streamlit puisse le lire
                var input = document.createElement('input');
                input.type = 'hidden';
                input.id = 'gantt_click_data';
                input.value = JSON.stringify(data);
                document.body.appendChild(input);
                // Déclencher un event pour notifier Streamlit
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: JSON.stringify(data)
                }, '*');
            }
        });
        </script>
        """

        # Utiliser un vrai composant Streamlit pour recevoir le clic
        clic_data = components.html(
            """
            <script>
            window.addEventListener('message', function(e) {
                if (e.data && e.data.type === 'gantt_click') {
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: JSON.stringify(e.data.data)
                    }, '*');
                }
            });
            </script>
            """,
            height=0
        )

        if clic_data:
            import json as _json
            try:
                data = _json.loads(clic_data)
                nom_projet_clic = data.get("projet")
                nom_tache_clic = data.get("tache")
                if nom_projet_clic and nom_tache_clic:
                    st.session_state["choix_projet"] = nom_projet_clic
                    st.session_state["choix_sous_tache"] = nom_tache_clic
                    st.switch_page("pages/04_Assignation.py")
            except Exception:
                pass
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
                dates_proj = [
                    date.fromisoformat(st_data[cle])
                    for st_data in projet_data["sous_taches"]
                    for cle in ("start", "end")
                ]
                d_debut = min(min(dates_proj), today) - timedelta(days=7)
                d_fin = max(dates_proj) + timedelta(days=7)
                html_detail = gantt_tableau([projet_data], data_proj, d_debut, d_fin, "gantt_detail", font_face)
                nb_st = len(projet_data["sous_taches"])
                components.html(html_detail, height=max(200, 80 + nb_st * 50), scrolling=False)
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
