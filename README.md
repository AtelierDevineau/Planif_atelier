# Planif_atelier
-------------------------Fichiers .json : 
Les fichiers en .json sont des fichiers de sauvegarde, ils permettent de garder en mémoire les intractions faites par l'utilisateur jusque dans le Repo Github. Cela permet notamment de ne pas perdre de données quand l'app streamlit se met "en sommeil".
  -Le fichier assignations.json garde en mémoire toutes les assignations de ressources au différents projets (et leurs sous-tâches), leur nombre, mais aussi la charge de travail (en %) affectée.
  - Le fichier projets.json garde en mémoire les noms des projets, leur couleur, les sous-tâches et les dates correspondates.
  - Le fichier ressources.json garde en mémoire les noms des ressources, leur dispo de base, leur dispo restante et leurs congés.


-------------------------Assignation.py : 
création de l'onglet "assignation des équipes" qui permet de :
  - Choisir un projet parmi ceux créés dans l'onglet "Création de projet"
  - Choisir une sous-tâche de ce projet
  - Assigner un nombre de ressources pour cette sous-tâche
    Pour chacune de ces ressources :
      - On associe en % une disponibilité qui va dépendre de son taux horaire, ses congés et des projets sur lequels iel travaille
      - On lui donne une charge de travail en pourcentage (en se basant sur sa disponibilité)
  On enregistre le tout avec un bouton, un tableau récapitulatif s'affiche en-dessous avec :
    -Le nombre de ressources assignées par projet
    - Par ressource, des barres qui donnent leur charge par projet de manière visuelle avec des couleurs.
  Sous le nom d'une personne ayant pris des congés pendant une sous-tâche un message d'alerte d'affiche.
   

  
-------------------------Calendrier.py : 
Création de l'onglet calendrier qui permet de :
  Option 1 :
    Avoir un diagramme de Gantt des projets en cours avec la possibilité de n'afficher qu'un certain nombre de semaines pour une question de lisibilité.
  Option 2 :
    Avoir un calendrier sur lequel s'affichent les absences des employés. Un formulaire permet de sélectionner un employé pour lui donner des congés (date de début et date de fin). Ces congés s'affichent sur le calendrier de la couleur associé à leur poste.

-------------------------Crea_proj.py : 
Création de l'onglet projet qui permet de créer un nouveau projet ou modifier les projets existants. Un formulaire pour mettre un nom s'affiche, lorsque le bouton créer un projet est cliqué il est alors possible de :
  - Modifier le nom du projet
  - Choisir une couleur à lui assigner
  - Créer des sous-tâches en leur donnant un nom, un début et une fin


-------------------------Crea_ress.py : 
Cration de l'onglet des ressources qui permet de créer, selon la liste de postes
POSTES = {
    "BE":             "#4E9AF1",  # bleu
    "Serrurerie":     "#F1874E",  # orange
    "Construction":   "#A0C45A",  # vert olive
    "Usinage":        "#A64EF1",  # violet
    "Déco":           "#F1C84E",  # jaune
    "Administration": "#4EF1C8",  # turquoise
    "Régisseur":      "#F14E7A",  # rose
    "Autres":         "#A0A0A0",  # gris
}
des "ressources". On peut alors les nommer et les intégrer dans un de ces postes. 











# Planification Projets — Atelier Devineau

Application web interne de planification des projets et des équipes de l'Atelier Devineau, développée avec [Streamlit](https://streamlit.io) et déployée sur [Streamlit Cloud](https://streamlit.io/cloud).

---

## Fonctionnalités

- **Calendrier** — Diagramme de Gantt interactif trié par type de sous-tâche, avec vue d'ensemble et vue détaillée par projet. Export CSV et Excel. Calendrier des absences de l'équipe.
- **Projets** — Création et gestion des projets avec leurs sous-tâches, dates, couleurs, client et description.
- **Ressources** — Gestion de l'équipe par poste (BE, Serrurerie, Construction, etc.) avec type de contrat et disponibilité de base.
- **Assignation** — Affectation des ressources aux sous-tâches de chaque projet, avec suivi des disponibilités et alertes en cas de congés.
- **Récapitulatif** — Vue synthétique des projets, de l'équipe et des assignations.
- **Accueil** — Page d'accueil avec notes (post-its), phrase du jour et image aléatoire.

---

## Structure du projet

```
├── Accueil.py                  # Page d'accueil (point d'entrée Streamlit)
├── auth.py                     # Gestion de l'authentification par cookie
├── style_sidebar.py            # CSS global (police, sidebar)
├── donnees.py                  # Données, accès GitHub, initialisation session
├── Logique.py                  # Calculs de disponibilité et charge
├── Calendrier.py               # Onglet Calendrier / Gantt
├── Crea_proj.py                # Onglet Création de projets
├── Assignation.py              # Onglet Assignation des équipes
├── Crea_ress.py                # Onglet Gestion des ressources
├── Recap.py                    # Onglet Récapitulatif
│
├── pages/
│   ├── 01_Calendrier.py
│   ├── 02_Projets.py
│   ├── 03_Ressources.py
│   ├── 04_Assignation.py
│   └── 05_Recap.py
│
├── fonts/
│   └── GT-Walsheim-Regular.ttf # Police de caractères (licence requise)
│
├── images/
│   ├── lion.png
│   ├── bateau.png
│   └── fusee.png
│
├── projets.json                # Données des projets (géré par l'app)
├── ressources.json             # Données des ressources (géré par l'app)
├── assignations.json           # Données des assignations (géré par l'app)
├── postits.json                # Notes de la page d'accueil (géré par l'app)
│
├── requirements.txt            # Dépendances Python
└── README.md
```

---

## Installation et déploiement

### Prérequis

- Un compte [GitHub](https://github.com) avec ce repo
- Un compte [Streamlit Cloud](https://streamlit.io/cloud)
- Python 3.9+ (pour développement local)

### Développement local

```bash
# Cloner le repo
git clone https://github.com/AtelierDevineau/Atelier_planif.git
cd Atelier_planif

# Installer les dépendances
pip install -r requirements.txt

# Créer le fichier de secrets local
mkdir .streamlit
# Créer .streamlit/secrets.toml avec le contenu suivant :
# MOT_DE_PASSE = "votre_mot_de_passe"
# GITHUB_TOKEN = "votre_token_github"
# GITHUB_REPO = "AtelierDevineau/Atelier_planif"

# Lancer l'application
streamlit run Accueil.py
```

### Déploiement sur Streamlit Cloud

1. Connectez-vous sur [share.streamlit.io](https://share.streamlit.io)
2. Cliquez **New app** → sélectionnez ce repo GitHub
3. Définissez **Main file path** : `Accueil.py`
4. Allez dans **Settings → Secrets** et ajoutez les secrets (voir section ci-dessous)
5. Cliquez **Deploy**

---

## Configuration des secrets

L'application utilise trois secrets stockés dans Streamlit Cloud (jamais dans le code).

Allez sur **share.streamlit.io → votre app → Settings → Secrets** et ajoutez :

```toml
MOT_DE_PASSE = "votre_mot_de_passe_ici"
GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxx"
GITHUB_REPO = "AtelierDevineau/Atelier_planif"
```

### Mot de passe

Le mot de passe protège l'accès à l'application. Choisissez-en un robuste et ne le partagez qu'avec les personnes autorisées. Il est stocké uniquement dans les secrets Streamlit, jamais dans le code.

### Token GitHub

Le token GitHub permet à l'application d'écrire dans les fichiers JSON du repo (projets, ressources, assignations, post-its) via l'API GitHub.

**Pourquoi en a-t-on besoin ?** Streamlit Cloud ne peut pas écrire sur le disque entre deux sessions. Les données sont donc persistées directement dans le repo GitHub via l'API, ce qui garantit qu'elles survivent aux redémarrages.

**Comment créer un token GitHub :**

1. Connectez-vous sur [github.com](https://github.com)
2. Cliquez sur votre avatar en haut à droite → **Settings**
3. Dans le menu gauche, tout en bas : **Developer settings**
4. **Personal access tokens → Tokens (classic)**
5. Cliquez **Generate new token (classic)**
6. Donnez-lui un nom (ex. `streamlit-planif`) et cochez uniquement **`repo`**
7. Cliquez **Generate token** et **copiez-le immédiatement** — il ne sera plus visible après
8. Collez-le dans les secrets Streamlit comme indiqué ci-dessus

> ⚠️ Un token GitHub est comme un mot de passe : ne le partagez pas, ne le mettez pas dans le code, et ne le poussez pas sur GitHub. Si un token est compromis, supprimez-le immédiatement depuis les paramètres GitHub et recréez-en un nouveau.

**Durée de vie du token :** par défaut les tokens n'expirent pas, mais GitHub peut vous envoyer un mail de rappel. Si l'app arrête de sauvegarder, vérifiez que le token est toujours valide.

---

## Données

Les données de l'application sont stockées dans quatre fichiers JSON à la racine du repo :

| Fichier | Contenu |
|---|---|
| `projets.json` | Liste des projets avec leurs sous-tâches, dates, couleurs, client, description |
| `ressources.json` | Liste des ressources avec poste, contrat, disponibilité de base, absences |
| `assignations.json` | Assignations des ressources par projet et sous-tâche |
| `postits.json` | Notes de la page d'accueil |

Ces fichiers sont mis à jour automatiquement par l'application à chaque modification. Vous pouvez les éditer manuellement sur GitHub si nécessaire, mais respectez le format JSON existant.

---

## Dépendances principales

| Librairie | Usage |
|---|---|
| `streamlit` | Framework web |
| `streamlit-calendar` | Calendrier des absences |
| `plotly` | (conservé pour usage futur) |
| `streamlit-cookies-controller` | Persistance de l'authentification entre pages |
| `openpyxl` | Export Excel du Gantt |
| `requests` | Appels API GitHub |

---

## Authentification

L'application est protégée par un mot de passe simple. À la connexion, un cookie est écrit dans le navigateur avec une durée de vie de 7 jours. Ce cookie permet à l'utilisateur de naviguer entre les pages sans ressaisir le mot de passe.

Si vous souhaitez déconnecter un utilisateur, supprimez le cookie `atelier_auth` depuis les outils développeur du navigateur, ou attendez son expiration.

---

## Notes de développement

- Le Gantt est généré en HTML pur (tableau avec cellules fusionnées) pour permettre le scroll horizontal et les clics de navigation.
- La police GT Walsheim est chargée en base64 depuis le fichier TTF du repo — une licence commerciale est requise pour l'utiliser.
- Toutes les sauvegardes GitHub passent par l'API REST avec le SHA du fichier pour éviter les conflits d'écriture.












