import streamlit as st
import plotly.graph_objects as go
from streamlit_calendar import calendar
from datetime import date, timedelta, datetime
from donnees import Options_cal, build_absences_cal, sauvegarder_ressources_github


#-------------UTILITAIRES--------------------

def to_timestamp_ms(date_str):
    """Convertit une date ISO 'YYYY-MM-DD' en timestamp milliseconds pour Plotly."""
    return int(datetime.fromisoformat(date_str).timestamp() * 1000)

def semaines_entre(date_debut_str, date_fin_str):
    """Génère les dates des lundis entre deux dates pour les ticks de l'axe."""
    debut = date.fromisoformat(date_debut_str)
    fin = date.fromisoformat(date_fin_str)
    lundi = debut - timedelta(days=debut.weekday())
    ticks_dates = []
    ticks_labels = []
    while lundi <= fin:
        semaine = lundi.isocalendar()[1]
        annee = lundi.isocalendar()[0]
        ticks_dates.append(lundi.isoformat())
        ticks_labels.append(f"S{semaine:02d} {annee}")
        lundi += timedelta(weeks=1)
    return ticks_dates, ticks_labels

def jours_entre(date_debut_str, date_fin_str):
    """Génère les dates de chaque jour entre deux dates pour la grille verticale."""
    debut = date.fromisoformat(date_debut_str)
    fin = date.fromisoformat(date_fin_str)
    jours = []
    cur = debut
    while cur <= fin:
        jours.append(cur.isoformat())
        cur += timedelta(days=1)
    return jours


#-------------CREATION GANTT--------------------

def gantt(projets_data, nb_semaines, titre=""):
    """
    Construction d'un diagramme de Gantt Plotly.
    - Pas de labels Y (trop peu de place)
    - Clés Y uniques = "projet||sous-tâche" pour éviter les collisions
    - Texte en noir sur les barres si assez larges, sinon au survol
    - Grille verticale légère derrière les barres
    """
    fig = go.Figure()

    today = date.today()
    x_min = today.isoformat()
    x_max = (today + timedelta(weeks=nb_semaines)).isoformat()

    duree_fenetre_ms = to_timestamp_ms(x_max) - to_timestamp_ms(x_min)
    seuil_texte_ms = duree_fenetre_ms * 0.05

    for projet in reversed(projets_data):
        nom_projet = projet["projet"]
        couleur = projet["couleur"]

        for sous_tache in projet["sous_taches"]:
            # Clé Y unique pour éviter que deux sous-tâches homonymes de projets différents
            # se retrouvent sur la même ligne
            label_y = f"{nom_projet}||{sous_tache['tache']}"

            duree_ms = (
                date.fromisoformat(sous_tache["end"]) -
                date.fromisoformat(sous_tache["start"])
            ).days * 24 * 3600 * 1000
            base_ms = to_timestamp_ms(sous_tache["start"])

            texte_barre = sous_tache["tache"] if duree_ms >= seuil_texte_ms else ""

            fig.add_trace(go.Bar(
                name=nom_projet,
                orientation="h",
                y=[label_y],
                x=[duree_ms],
                base=[base_ms],
                marker=dict(color=couleur, line=dict(color="white", width=1)),
                text=texte_barre,
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(color="black", size=11),
                hovertemplate=(
                    f"<b>{nom_projet}</b><br>"
                    f"Tâche : {sous_tache['tache']}<br>"
                    f"Début : {sous_tache['start']}<br>"
                    f"Fin : {sous_tache['end']}<extra></extra>"
                ),
                showlegend=False,
            ))

    # Ticks semaines
    ticks_dates, ticks_labels = semaines_entre(x_min, x_max)

    # Légende manuelle par projet
    for projet in projets_data:
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="markers",
            marker=dict(size=10, color=projet["couleur"], symbol="square"),
            name=projet["projet"],
        ))

    nb_sous_taches = sum(len(p["sous_taches"]) for p in projets_data)

    fig.update_layout(
        barmode="overlay",
        title=titre if titre else "",
        xaxis=dict(
            type="date",
            range=[x_min, x_max],
            tickvals=ticks_dates,
            ticktext=ticks_labels,
            tickangle=-90,
            showgrid=True,
            gridcolor="#eeeeee",
            gridwidth=1,
            side="top",
        ),
        yaxis=dict(
            autorange="reversed",
            showticklabels=False,  # on masque les labels Y (clés techniques)
            showgrid=False,
        ),
        height=160 + nb_sous_taches * 40,
        margin=dict(l=10, r=20, t=80, b=120),
        plot_bgcolor="white",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
        ),
    )

    return fig


#-------------ONGLET CALENDRIER----------------------

def calendrier_tab():
    """Affiche onglet calendrier"""
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

        # ---- Vue d'ensemble ----
        st.markdown("#### Vue d'ensemble")
        if projets:
            fig_global = gantt(projets, nb_semaines)
            st.plotly_chart(fig_global, use_container_width=True)
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
                fig_detail = gantt([projet_data], nb_semaines, titre=projet_choisi)
                st.plotly_chart(fig_detail, use_container_width=True)
            else:
                st.info("Ce projet n'a pas encore de sous-tâches.")

    if selection == "Absences":
        # --- Formulaire d'ajout d'absence ---
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
