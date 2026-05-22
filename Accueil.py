import streamlit as st
import random
import json
import requests
import base64
from style_sidebar import inject_style

# ── Configuration page ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Atelier Devineau — Accueil",
    page_icon="🔧",
)

inject_style()

# ── Authentification ──────────────────────────────────────────────────────────
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False

if not st.session_state.authentifie:
    st.title("Accès à l'application")
    mdp = st.text_input("Mot de passe", type="password")
    if st.button("Connexion"):
        if mdp == st.secrets["MOT_DE_PASSE"]:
            st.session_state.authentifie = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect")
    st.stop()

# ── GitHub ────────────────────────────────────────────────────────────────────
GITHUB_REPO = st.secrets["GITHUB_REPO"]
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/contents/postits.json"

def _headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

def charger_postits():
    response = requests.get(GITHUB_API, headers=_headers())
    if response.status_code == 200:
        data = response.json()
        contenu = base64.b64decode(data["content"]).decode("utf-8")
        return json.loads(contenu), data["sha"]
    return [], None

def sauvegarder_postits(postits, sha):
    contenu_encode = base64.b64encode(
        json.dumps(postits, ensure_ascii=False, indent=4).encode("utf-8")
    ).decode("utf-8")
    payload = {
        "message": "Mise à jour post-its via l'app",
        "content": contenu_encode,
        "sha": sha
    }
    response = requests.put(GITHUB_API, headers=_headers(), json=payload)
    if response.status_code in (200, 201):
        return response.json()["content"]["sha"]
    st.error(f"Erreur sauvegarde GitHub ({response.status_code})")
    return sha

# ── Chargement post-its ───────────────────────────────────────────────────────
if "postits" not in st.session_state:
    postits, sha = charger_postits()
    st.session_state.postits = postits
    st.session_state.postits_sha = sha

# ── Phrases ───────────────────────────────────────────────────────────────────
PHRASES = [
    "Le canard a une paupière transparente pour voir sous l'eau. Vous, vous avez du café. C'est comparable.",
    "En moyenne, un humain prend 23 000 décisions par jour. Bonne chance pour aujourd'hui.",
    "La Tour Eiffel grandit de 15 cm en été à cause de la dilatation thermique. Même l'acier a besoin d'espace.",
    "Les abeilles prennent des décisions collectives par vote. Aucune n'a jamais demandé à voir le compte rendu.",
    "Un éclair contient assez d'énergie pour griller 100 000 tartines.",
    "Le Colisée de Rome a été construit en 8 ans. Avec un bon planning, tout est possible.",
    "IKEA emploie plus de monde que certains pays ont d'habitants. Et pourtant, il manque toujours une vis.",
    "Le premier prototype de Post-it était un échec : la colle ne collait pas assez.",
    "Shakespeare écrivait en moyenne 1,5 pièce par an. Sans ordinateur, sans correcteur, sans café en capsules.",
    "Oxford University est plus vieille que les Aztèques. Certaines réunions aussi.",
    "Un humain au repos produit assez de chaleur pour faire bouillir un litre d'eau en 30 minutes.",
]

if "phrase_du_jour" not in st.session_state:
    st.session_state.phrase_du_jour = random.choice(PHRASES)

IMAGES_BANNIERE = ["lion.png", "bateau.png", "fusee.png"]

if "image_banniere" not in st.session_state:
    st.session_state.image_banniere = random.choice(IMAGES_BANNIERE)

# ── Style CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.postit {
    background-color: #F5D627;
    border-radius: 4px;
    padding: 16px;
    min-height: 120px;
    box-shadow: 3px 3px 8px rgba(0,0,0,0.15);
    font-size: 0.95em;
    white-space: pre-wrap;
    word-wrap: break-word;
    margin-bottom: 8px;
}
.phrase-accueil {
    text-align: center;
    font-style: italic;
    color: #555;
    font-size: 1.05em;
    margin: 8px 0 32px 0;
}
</style>
""", unsafe_allow_html=True)

# ── Logo ──────────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("Atelier Devineau logo.png", use_container_width=True)

# ── Bannière image aléatoire ──────────────────────────────────────────────────
st.image(st.session_state.image_banniere, use_container_width=True)

# ── Phrase d'accueil ──────────────────────────────────────────────────────────
st.markdown(
    f'<div class="phrase-accueil">✨ {st.session_state.phrase_du_jour}</div>',
    unsafe_allow_html=True
)

# ── Post-its ──────────────────────────────────────────────────────────────────
st.markdown("### 📌 Notes")
postits = st.session_state.postits

if postits:
    cols = st.columns(3)
    for idx, postit in enumerate(postits):
        with cols[idx % 3]:
            st.markdown(
                f'<div class="postit">{postit["texte"]}</div>',
                unsafe_allow_html=True
            )
            if st.button("🗑️", key=f"del_postit_{idx}", help="Supprimer ce post-it"):
                postits.pop(idx)
                nouveau_sha = sauvegarder_postits(postits, st.session_state.postits_sha)
                st.session_state.postits_sha = nouveau_sha
                st.rerun()
else:
    st.info("Aucune note pour l'instant. Ajoutez-en une ci-dessous !")

# ── Ajout d'un post-it ────────────────────────────────────────────────────────
st.divider()
with st.form("form_postit", clear_on_submit=True):
    nouveau_texte = st.text_area(
        "Nouvelle note",
        placeholder="Écrivez votre note ici...",
        height=100,
        label_visibility="collapsed"
    )
    submitted = st.form_submit_button("➕ Ajouter une note")

if submitted:
    if not nouveau_texte.strip():
        st.error("Merci de saisir un texte.")
    else:
        postits.append({"texte": nouveau_texte.strip()})
        nouveau_sha = sauvegarder_postits(postits, st.session_state.postits_sha)
        st.session_state.postits_sha = nouveau_sha
        st.rerun()
