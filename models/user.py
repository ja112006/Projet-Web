import sqlite3
import bcrypt
from db import get_db


def create_user(email, password, nom, prenom, role):
    # Hasher le mot de passe
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    tab = get_db() # On get la db
    cursor = tab.cursor() # Obligatoire pour executer des requetes
    try:
        cursor.execute("INSERT INTO users (email, password_hash, nom, prenom, role) VALUES (?, ?, ?, ?, ?)", (email, hashed_password.decode('utf-8'), nom, prenom, role)) # On utilise password.decode pour etre sur d'avoir un string valide et pas un byte
        tab.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        tab.close()


def get_user_by_email(email):
    # Recup les infos d'un user à partir de son mail
    tab = get_db()
    cursor = tab.cursor()
    cursor.execute("SELECT id, email, password_hash, nom, prenom, role, created_at FROM users WHERE email = ?", (email,))
    row = cursor.fetchone() # Pour recup la ligne de reponse de la requetes sous forme de tuple
    tab.close()
    
    if row:
        return {
            'id': row[0],
            'email': row[1],
            'password_hash': row[2],
            'nom': row[3],
            'prenom': row[4],
            'role': row[5],
            'created_at': row[6]
        }
    return None


def get_user_by_id(user_id):
    #recup info d'un user par id
    tab = get_db()
    cursor = tab.cursor()
    
    cursor.execute("SELECT id, email, nom, prenom, role FROM users WHERE id = ?", (user_id,))
    
    row = cursor.fetchone()
    tab.close()
    
    if row:
        return {
            'id': row[0],
            'email': row[1],
            'nom': row[2],
            'prenom': row[3],
            'role': row[4]
        }
    return None


def verify_password(email, password):
    #check mdp pour login
    user = get_user_by_email(email)

    # On verifie que l'utilisateur existe et que les hash des mot de passes correspondent
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')): # Encode pour transformer en byte au lieu d'un string
        return user
    
    return None


def get_all_enseignants():
    #recup tous les user enseignants
    tab = get_db()
    cursor = tab.cursor()
    cursor.execute("SELECT id, nom, prenom, email FROM users WHERE role = 'enseignant' ORDER BY nom, prenom") 
    rows = cursor.fetchall() # Pour recup toutes les lignes de resultat de la requetes
    tab.close()
    enseignants = [] # On créer un tableau contenant les informations de tous les enseignants sur la table users
    for row in rows:
        enseignants.append({
            'id': row[0],
            'nom': row[1],
            'prenom': row[2],
            'email': row[3]
        })
    
    return enseignants
