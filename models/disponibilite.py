import sqlite3
from datetime import datetime, timedelta
from db import get_db


def create_disponibilite(enseignant_id, jour, heure_debut, heure_fin):
    # Creer un creneau pour un enseignant
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO disponibilites (enseignant_id, jour, heure_debut, heure_fin) VALUES (?, ?, ?, ?)", (enseignant_id, jour, heure_debut, heure_fin))
    
    conn.commit()
    dispo_id = cursor.lastrowid
    conn.close()
    
    return dispo_id


def get_disponibilites_enseignant(enseignant_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, jour, heure_debut, heure_fin, est_disponible FROM disponibilites WHERE enseignant_id = ? ORDER BY jour, heure_debut", (enseignant_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    disponibilites = []
    for row in rows:
        disponibilites.append({
            'id': row[0],
            'jour': row[1],
            'heure_debut': row[2],
            'heure_fin': row[3],
            'est_disponible': row[4]
        })
    
    return disponibilites


def get_disponibilites_futures(enseignant_id):
    # On récupere les dispo futures d'un etudiant
    conn = get_db()
    cursor = conn.cursor()
    
    aujourd_hui = datetime.now().date()
    
    cursor.execute("SELECT id, jour, heure_debut, heure_fin FROM disponibilites WHERE enseignant_id = ? AND jour >= ? AND est_disponible = 1 ORDER BY jour, heure_debut", (enseignant_id, aujourd_hui))
    
    rows = cursor.fetchall()
    conn.close()
    
    disponibilites = []
    for row in rows:
        disponibilites.append({
            'id': row[0],
            'jour': row[1],
            'heure_debut': row[2],
            'heure_fin': row[3]
        })
    
    return disponibilites


def generer_creneaux_disponibles(enseignant_id, jour):
    # Recupérer les créneaux disponibles d'un enseignant un certains jours 
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, heure_debut, heure_fin FROM disponibilites WHERE enseignant_id = ? AND jour = ? AND est_disponible = 1", (enseignant_id, jour))
    
    disponibilites = cursor.fetchall()
    
    if not disponibilites:
        conn.close()
        return []
    
    cursor.execute("SELECT date_heure_debut, date_heure_fin FROM rendez_vous WHERE enseignant_id = ? AND DATE(date_heure_debut) = ? AND statut = 'confirmé'", (enseignant_id, jour))
    
    rdv_pris = cursor.fetchall()
    conn.close()
    
    creneaux_pris = set() # On utilise un set pour éviter les repetitions plutôt qu'un tableau
    for rdv in rdv_pris:
        creneaux_pris.add(rdv[0])
    
    creneaux_disponibles = []
    
    for dispo in disponibilites:
        dispo_id, heure_debut, heure_fin = dispo
        
        debut_dt = datetime.strptime(f"{jour} {heure_debut}", "%Y-%m-%d %H:%M")
        fin_dt = datetime.strptime(f"{jour} {heure_fin}", "%Y-%m-%d %H:%M")
        
        # durée totale calculée dynamiquement
        duree_minutes = int((fin_dt - debut_dt).total_seconds() / 60)
        
        # un seul créneau = toute la plage
        creneau_debut = debut_dt.strftime("%Y-%m-%d %H:%M:%S")
        creneau_fin = fin_dt.strftime("%Y-%m-%d %H:%M:%S")
        
        if creneau_debut not in creneaux_pris: # On verifie que le debut du créneau n'est pas celui d'un créneau déjà pris (car 1 même enseignant ne peut avoir 2 rdv en même temps disponibles)
            creneaux_disponibles.append({
                'disponibilite_id': dispo_id,
                'heure_debut': heure_debut,
                'heure_fin': heure_fin,
                'date_heure_debut': creneau_debut,
                'date_heure_fin': creneau_fin,
                'duree_minutes': duree_minutes
            })
    
    return creneaux_disponibles


def get_jours_avec_disponibilites(enseignant_id):
    # On recupere les Jours ayant des disponibilités
    conn = get_db()
    cursor = conn.cursor()
    
    aujourd_hui = datetime.now().date()
    
    cursor.execute("SELECT DISTINCT jour FROM disponibilites WHERE enseignant_id = ? AND jour >= ? AND est_disponible = 1 ORDER BY jour", (enseignant_id, aujourd_hui))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [row[0] for row in rows]


def delete_disponibilite(dispo_id):
    # Pour supprimmer une disponibilité
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM rendez_vous WHERE disponibilite_id = ? AND statut = 'confirmé'", (dispo_id,))
    
    count = cursor.fetchone()[0]
    
    if count > 0:
        conn.close()
        return False
    
    cursor.execute("DELETE FROM disponibilites WHERE id = ?", (dispo_id,))
    conn.commit()
    conn.close()
    
    return True


def get_disponibilite_by_id(dispo_id):
    # Pour recup les informations d'une disponibilité via son ID
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, enseignant_id, jour, heure_debut, heure_fin FROM disponibilites WHERE id = ?", (dispo_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'enseignant_id': row[1],
            'jour': row[2],
            'heure_debut': row[3],
            'heure_fin': row[4]
        }
    return None