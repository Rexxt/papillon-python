![image](https://user-images.githubusercontent.com/32978709/205500141-cf7be394-9929-4c2c-90a3-977cffc3f16f.png)

## Pourquoi faire ?
Auparavant, [Papillon](https://github.com/ecnivtwelve/Papillon) utilisait [@Litarvan/pronote-api](https://github.com/Litarvan/pronote-api), mais cette API non maintenue depuis Avril 2021 commence à poser de plus en plus de problèmes à cause de son retard, et en plus est compliquée à héberger. Voila pourquoi je transitionne vers [@bain3/pronotepy](https://github.com/bain3/pronotepy), qui est encore maintenu et bien plus complet en fonctionnalités.

Le but est de l'intégrer le plus vite possible dans [Papillon](https://github.com/ecnivtwelve/Papillon), et d'arrêter complètement l'ancien backend [node-pronote](https://github.com/ecnivtwelve/node-pronote) pour attribuer plus de ressources à papillon-python.

## Roadmap
- [x] Données de l'utilisateur
- [x] Emploi du temps
- [x] Travail à faire
- [x] Notes
- [ ] Compétences
- [ ] Fichiers
- [x] Actualités **(ne contient pas les pièces jointes)**
- [x] Absences et retards
- [x] Messagerie **(n'a pas l'air de fonctionner)**

## Requêtes
Un client doit faire la requête initiale `POST /generatetoken` avec le body suivant :
| Paramètre | Utilité | Exemple |
|--|--|--|
| `url` | URL vers l'instance pronote **(avec le eleve.html)** | `https://0152054e.index-education.net/pronote/eleve.html` |
| `username` | Nom d'utilisateur **PRONOTE** | `l.martin` |
| `password` | Mot de passe en clair | `azertyuiop12345` |
| `ent` | Nom de l'ENT tel que listé [ici](https://github.com/bain3/pronotepy/blob/master/pronotepy/ent/ent.py) | `ac_rennes` |

Le client doit ensuite garder le token généré. Si il ya eu un délai d'au moins 5 minutes entre deux interactions, le client doit regénérer un nouveau token.

Ensuite chaque appel à une fonction de l'API doit avoir le paramètre `token` défini.
Voici la liste des URLs pour obtenir des données :

| URL | Utilité | Paramètres |
|--|--|--|
| `/user` | Obtient les infos sur l'utilisateur (nom, classe...) |  |
| `/timetable` | Affiche l'emploi du temps sur une date donnée | `dateString` : date au format **`année-mois-jour`** |
| `/homework` | Affiche les devoirs entre deux dates données | `dateFrom` : date de début au format **`année-mois-jour`**, et `dateTo` date de fin au même format |
| `/grades` | Affiche les notes |  |
| `/absences` | Affiche les absences |  |
| `/news` | Affiche les actualités |  |
| `/messagerie` | Affiche les messages |  |

Voici la liste des URL qui éffectuent une simple fonction :
| URL | Utilité | Paramètres | Réponse
|--|--|--|--|
| `/export/ical` | Exporte le calendrier en iCal |  | *(l'url du fichier iCal)* |
| `/homework/setAsDone` **(ne fonctionne pas)** | Change l'état d'un devoir (fait/non fait) | `dateFrom` : date de début au format **`année-mois-jour`**, et `dateTo` date de fin au même format, et `homeworkId` l'id du devoir à changer | *(état du devoir changé)* |