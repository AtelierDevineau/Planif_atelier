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












