import streamlit as st
from datetime import date
from donnees import get_couleur_poste, POSTES

# -------------------------------------------------------
# UTILITAIRES
# -------------------------------------------------------

def est_absent_aujourdhui(ressource):
    """Retourne True si la ressource est en congé aujourd'hui."""
    today = date.today()
    for absence in ressource.get("absences", []):
        debut = date.fromisoformat(absence["start"])
        fin = date.fromisoformat(absence["end"])
        if debut <= today < fin:
            return True
    return False


def html_tableau_projets(projets):
    """Génère un tableau HTML avec une cellule colorée par projet."""
    lignes = ""
    for p in projets:
        couleur = p["couleur"]
        nom = p["projet"]
        client = p.get("client", "—")
        lignes += (
            f"<tr style='border-bottom:1px solid #eee;'>"
            f"<td style='background-color:{couleur};width:30px;'></td>"
            f"<td style='padding:6px 12px;'><b>{nom}</b></td>"
            f"<td style='padding:6px 12px;color:#666;'>{client}</td>"
            f"</tr>"
        )
    return f"""
    <table style="width:100%;border-collapse:collapse;margin-bottom:16px;">
        <thead>
            <tr style="background:#f5f5f5;text-align:left;">
                <th style="padding:6px 12px;width:30px;"></th>
                <th style="padding:6px 12px;">Projet</th>
                <th style="padding:6px 12px;">Client</th>
            </tr>
        </thead>
        <tbody>{lignes}</tbody>
    </table>
    """


def html_tableau_ressources(ressources):
    """Génère un tableau HTML des ressources triées par poste avec présence colorée."""
    ordre_postes = list(POSTES.keys())
    ressources_triees = sorted(
        ressources,
        key=lambda r: ordre_postes.index(r.get("Poste", "Autres"))
        if r.get("Poste", "Autres") in ordre_postes else len(ordre_postes)
    )

    lignes = ""
    for r in ressources_triees:
        poste = r.get("Poste", "Autres")
        couleur_poste = get_couleur_poste(poste)
        absent = est_absent_aujourdhui(r)
        statut_lettre = "A" if absent else "P"
        statut_couleur = "#e74c3c" if absent else "#27ae60"

        lignes += (
            f"<tr style='border-bottom:1px solid #eee;'>"
            f"<td style='background-color:{couleur_poste}22;color:{couleur_poste};"
            f"font-weight:bold;padding:6px 12px;border-left:4px solid {couleur_poste};'>"
            f"{poste}</td>"
            f"<td style='padding:6px 12px;'>{r['Nom']}</td>"
            f"<td style='padding:6px 12px;color:#666;'>{r.get('Contrat', '—')}</td>"
            f"<td style='padding:6px 12px;text-align:center;'>"
            f"<span style='background-color:{statut_couleur};color:white;"
            f"border-radius:4px;padding:2px 10px;font-weight:bold;'>{statut_lettre}</span>"
            f"</td>"
            f"</tr>"
        )
    return f"""
    <table style="width:100%;border-collapse:collapse;margin-bottom:16px;">
        <thead>
            <tr style="background:#f5f5f5;text-align:left;">
                <th style="padding:6px 12px;">Poste</th>
                <th style="padding:6px 12px;">Nom</th>
                <th style="padding:6px 12px;">Statut</th>
                <th style="padding:6px 12px;text-align:center;">Présence</th>
            </tr>
        </thead>
        <tbody>{lignes}</tbody>
    </table>
    """


def html_recap_sous_taches(sous_taches, data_projet):
    """Tableau récap nb ressources par sous-tâche."""
    lignes = ""
    for st_data in sous_taches:
        nom_st = st_data["tache"]
        nb = data_projet.get(nom_st, {}).get("Nb_ressources", 0)
        lignes += (
            f"<tr style='border-bottom:1px solid #eee;'>"
            f"<td style='padding:6px 12px;'><b>{nom_st}</b></td>"
            f"<td style='padding:6px 12px;color:#666;'>{st_data['start']} → {st_data['end']}</td>"
            f"<td style='padding:6px 12px;text-align:center;'>{nb}</td>"
            f"</tr>"
        )
    return f"""
    <table style="width:100%;border-collapse:collapse;margin-bottom:20px;">
        <thead>
            <tr style="background:#f5f5f5;text-align:left;">
                <th style="padding:6px 12px;">Sous-tâche</th>
                <th style="padding:6px 12px;">Période</th>
                <th style="padding:6px 12px;text-align:center;">Nb ressources</th>
            </tr>
        </thead>
        <tbody>{lignes}</tbody>
    </table>
    """


def html_detail_sous_tache(st_data, data_st, ressources_base):
    """Tableau d'une sous-tâche avec ressources assignées triées par poste."""
    assignations = data_st.get("Assignations", [])
    if not assignations:
        return None

    ordre_postes = list(POSTES.keys())
    ress_dict = {r["Nom"]: r for r in ressources_base}
    assignations_enrichies = sorted(
        [
            {**a, "Poste": ress_dict.get(a["Nom"], {}).get("Poste", "Autres")}
            for a in assignations
        ],
        key=lambda x: ordre_postes.index(x["Poste"])
        if x["Poste"] in ordre_postes else len(ordre_postes)
    )

    lignes = ""
    for a in assignations_enrichies:
        couleur_poste = get_couleur_poste(a["Poste"])
        lignes += (
            f"<tr style='border-bottom:1px solid #eee;'>"
            f"<td style='background-color:{couleur_poste}22;color:{couleur_poste};"
            f"font-weight:bold;padding:6px 12px;border-left:4px solid {couleur_poste};'>"
            f"{a['Poste']}</td>"
            f"<td style='padding:6px 12px;'>{a['Nom']}</td>"
            f"<td style='padding:6px 12px;text-align:center;color:#666;'>{a['Pct']}%</td>"
            f"</tr>"
        )

    nom_st = st_data["tache"]
    header = (
        f"<p style='font-weight:bold;margin-top:16px;margin-bottom:6px;'>{nom_st} "
        f"<span style='font-weight:normal;color:#888;font-size:0.9em;'>"
        f"— {st_data['start']} → {st_data['end']}</span></p>"
    )
    tableau = f"""
    <table style="width:100%;border-collapse:collapse;margin-bottom:16px;">
        <thead>
            <tr style="background:#f5f5f5;text-align:left;">
                <th style="padding:6px 12px;">Poste</th>
                <th style="padding:6px 12px;">Nom</th>
                <th style="padding:6px 12px;text-align:center;">Charge</th>
            </tr>
        </thead>
        <tbody>{lignes}</tbody>
    </table>
    """
    return header + tableau


# -------------------------------------------------------
# ONGLET PRINCIPAL
# -------------------------------------------------------

def recap_tab():
    st.subheader("Récapitulatif")

    projets = st.session_state.Projets_gantt
    ressources = st.session_state.Ressources_base
    data_proj = st.session_state.Data_proj

    # ---- Tableau projets ----
    st.markdown("### Projets")
    if projets:
        st.markdown(html_tableau_projets(projets), unsafe_allow_html=True)
    else:
        st.info("Aucun projet créé.")

    # ---- Tableau ressources ----
    st.markdown("### Équipe")
    if ressources:
        st.markdown(html_tableau_ressources(ressources), unsafe_allow_html=True)
    else:
        st.info("Aucune ressource créée.")

    # ---- Détail par projet ----
    st.markdown("### Détail par projet")
    if not projets:
        st.info("Aucun projet à afficher.")
    else:
        for projet in projets:
            nom_projet = projet["projet"]
            titre_expander = f"**{nom_projet}**"
            if projet.get("client"):
                titre_expander += f" — {projet['client']}"

            with st.expander(titre_expander):
                sous_taches = projet.get("sous_taches", [])
                if not sous_taches:
                    st.info("Ce projet n'a pas encore de sous-tâches.")
                    continue

                data_projet = data_proj.get(nom_projet, {})

                # Tableau récap
                st.markdown("**Récapitulatif par sous-tâche**")
                st.markdown(
                    html_recap_sous_taches(sous_taches, data_projet),
                    unsafe_allow_html=True
                )

                # Un tableau par sous-tâche avec assignations
                any_assignation = False
                for st_data in sous_taches:
                    nom_st = st_data["tache"]
                    data_st = data_projet.get(nom_st, {})
                    html = html_detail_sous_tache(st_data, data_st, ressources)
                    if html:
                        any_assignation = True
                        st.markdown(html, unsafe_allow_html=True)

                if not any_assignation:
                    st.info("Aucune ressource assignée sur ce projet.")
