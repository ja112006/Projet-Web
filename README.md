# Projet Web 

## Reservation de rendez-vous enseignants/etudiants

Application Flask simple pour gerer la prise de rendez-vous entre etudiants et enseignants.

## Collaborateurs (Groupe 1)

- Dylan Becheker
- Jaber Benyacoub

## Fonctionnalites

- Inscription et connexion avec deux roles: `etudiant` et `enseignant`
- Gestion des disponibilites enseignant (date + heure debut/fin)
- Reservation de rendez-vous cote etudiant
- Annulation de rendez-vous
- Tableaux de bord separes selon le role

## Structure du projet

- app.py: routes Flask, session, logique web
- models/: methodes pour tables SQL (users, disponibilites, rendez_vous)
- templates/: vues HTML Jinja2
- static/: CSS et JavaScript
- schema.sql: schema SQLite
- init_db.py: creation/initialisation de la base


