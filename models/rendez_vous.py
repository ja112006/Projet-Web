import sqlite3
from datetime import datetime
from db import get_db


def create_rendez_vous(disponibilite_id, etudiant_id, enseignant_id, date_heure_debut, date_heure_fin, motif=""):
    tab = get_db()
    cursor = tab.cursor()
    
    # Vérifier que le créneau est toujours libre
    cursor.execute("SELECT COUNT(*) FROM rendez_vous WHERE enseignant_id = ? AND date_heure_debut = ? AND statut = 'confirmé'", (enseignant_id, date_heure_debut))
    count = cursor.fetchone()[0] # On recupère le 1er element de la dernière ligne de la reponse de la requetes (correspond au nombre de rdv confirmé selon l'id du rdv selectionné actuellement)
    if count > 0:
        tab.close()
        return None
    
    # Créer le rdv
    try:
        cursor.execute("INSERT INTO rendez_vous (disponibilite_id, etudiant_id, enseignant_id, date_heure_debut, date_heure_fin, motif) VALUES (?, ?, ?, ?, ?, ?)", (disponibilite_id, etudiant_id, enseignant_id, date_heure_debut, date_heure_fin, motif))
        tab.commit()
        rdv_id = cursor.lastrowid
        tab.close()
        return rdv_id
    
    except sqlite3.IntegrityError:
        tab.close()
        return None


def get_rendez_vous_etudiant(etudiant_id):
    #recup tous les rdv d'un etudiant
    tab = get_db()
    cursor = tab.cursor()
    
    cursor.execute("SELECT r.id, r.date_heure_debut, r.date_heure_fin, r.motif, r.statut, u.nom, u.prenom, u.email FROM rendez_vous r JOIN users u ON r.enseignant_id = u.id WHERE r.etudiant_id = ? ORDER BY r.date_heure_debut DESC", (etudiant_id,))
    
    rows = cursor.fetchall() # On recupère toutes les lignes de réponses de la requêtes executée
    tab.close()

    # On met tous dans un tableau
    rendez_vous = []
    for row in rows:
        rendez_vous.append({
            'id': row[0],
            'date_heure_debut': row[1],
            'date_heure_fin': row[2],
            'motif': row[3],
            'statut': row[4],
            'enseignant_nom': row[5],
            'enseignant_prenom': row[6],
            'enseignant_email': row[7]
        })
    
    return rendez_vous


def get_rendez_vous_etudiant_futurs(etudiant_id):
    # Recup les rdv qui arrivent d'un etudiant
    tab = get_db()
    cursor = tab.cursor()
    
    maintenant = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Pour comparer dans la requêtes les rdv qui arrivent dans un temps superieur à la date actuelle
    
    cursor.execute("SELECT r.id, r.date_heure_debut, r.date_heure_fin, r.motif, u.nom, u.prenom, u.email FROM rendez_vous r JOIN users u ON r.enseignant_id = u.id WHERE r.etudiant_id = ? AND r.date_heure_debut >= ? AND r.statut = 'confirmé' ORDER BY r.date_heure_debut", (etudiant_id, maintenant))
    
    rows = cursor.fetchall()
    tab.close()
    
    rendez_vous = []
    for row in rows:
        rendez_vous.append({
            'id': row[0],
            'date_heure_debut': row[1],
            'date_heure_fin': row[2],
            'motif': row[3],
            'enseignant_nom': row[4],
            'enseignant_prenom': row[5],
            'enseignant_email': row[6]
        })
    
    return rendez_vous


def get_rendez_vous_enseignant(enseignant_id):
    #recup tout les rdv d'un enseignant
    tab = get_db()
    cursor = tab.cursor()
    
    cursor.execute("SELECT r.id, r.date_heure_debut, r.date_heure_fin, r.motif, r.statut, u.nom, u.prenom, u.email FROM rendez_vous r JOIN users u ON r.etudiant_id = u.id WHERE r.enseignant_id = ? ORDER BY r.date_heure_debut DESC", (enseignant_id,))
    
    rows = cursor.fetchall()
    tab.close()
    
    rendez_vous = []
    for row in rows:
        rendez_vous.append({
            'id': row[0],
            'date_heure_debut': row[1],
            'date_heure_fin': row[2],
            'motif': row[3],
            'statut': row[4],
            'etudiant_nom': row[5],
            'etudiant_prenom': row[6],
            'etudiant_email': row[7]
        })
    
    return rendez_vous


def get_rendez_vous_enseignant_futurs(enseignant_id):
    #recup tous les prochains rdv d'un enseignant
    tab = get_db()
    cursor = tab.cursor()
    
    maintenant = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Pour comparer dans la requêtes les rdv qui arrivent dans un temps superieur à la date actuelle
    
    cursor.execute("SELECT r.id, r.date_heure_debut, r.date_heure_fin, r.motif, u.nom, u.prenom, u.email FROM rendez_vous r JOIN users u ON r.etudiant_id = u.id WHERE r.enseignant_id = ? AND r.date_heure_debut >= ? AND r.statut = 'confirmé' ORDER BY r.date_heure_debut", (enseignant_id, maintenant))
    
    rows = cursor.fetchall()
    tab.close()
    
    rendez_vous = []
    for row in rows:
        rendez_vous.append({
            'id': row[0],
            'date_heure_debut': row[1],
            'date_heure_fin': row[2],
            'motif': row[3],
            'etudiant_nom': row[4],
            'etudiant_prenom': row[5],
            'etudiant_email': row[6]
        })
    
    return rendez_vous


def annuler_rendez_vous(rdv_id, user_id):
    #Annuler un rdv 
    tab = get_db()
    cursor = tab.cursor()
    
    #verifier que l'utilisateur est bien concerné par ce RDV
    cursor.execute("SELECT id FROM rendez_vous WHERE id = ? AND (etudiant_id = ? OR enseignant_id = ?)", (rdv_id, user_id, user_id))
    
    if not cursor.fetchone():
        tab.close()
        return False  # L'utilisateur n'est pas autorisé à annuler ce RDV
    
    #Annuler le rdv
    cursor.execute("UPDATE rendez_vous SET statut = 'annulé' WHERE id = ?", (rdv_id,))
    
    tab.commit()
    tab.close()
    return True


def get_rendez_vous_by_id(rdv_id):
    #recup un rdv par son id
    tab = get_db()
    cursor = tab.cursor()
    
    cursor.execute("SELECT r.id, r.disponibilite_id, r.etudiant_id, r.enseignant_id, r.date_heure_debut, r.date_heure_fin, r.motif, r.statut FROM rendez_vous r WHERE r.id = ?", (rdv_id,))
    
    row = cursor.fetchone()
    tab.close()
    
    if row:
        return {
            'id': row[0],
            'disponibilite_id': row[1],
            'etudiant_id': row[2],
            'enseignant_id': row[3],
            'date_heure_debut': row[4],
            'date_heure_fin': row[5],
            'motif': row[6],
            'statut': row[7]
        }
    return None


def check_conflit_horaire(user_id, date_heure_debut, date_heure_fin):
    # Verifier que 2 rdv à la meme horaire se chevauche en verifiant que sur un certains créneaux le nombre de rdv soit <=1
    tab = get_db()
    cursor = tab.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM rendez_vous WHERE (etudiant_id = ? OR enseignant_id = ?) AND statut = 'confirmé' AND ((date_heure_debut <= ? AND date_heure_fin > ?) OR (date_heure_debut < ? AND date_heure_fin >= ?) OR (date_heure_debut >= ? AND date_heure_fin <= ?))", (user_id, user_id, date_heure_debut, date_heure_debut, date_heure_fin, date_heure_fin, date_heure_debut, date_heure_fin))
    
    count = cursor.fetchone()[0]
    tab.close()
    
    return count > 0
