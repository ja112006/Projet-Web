import sqlite3
import bcrypt

DATABASE = 'rdv.db'

def init_database():
    #creation de la base et des tables
    print("Initialisation de la bdd")
    
    # Connexion à la base de données (la crée si elle n'existe pas)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Lire et exécuter le schéma sql
    with open('schema.sql', 'r', encoding='utf-8') as f:
        schema = f.read()
    
    cursor.executescript(schema)
    conn.commit()
    
    # Créer des utilisateurs de test
    create_test_users(conn)
    
    conn.close()
    print("Bdd créee avec succès")


def create_test_users(conn):
    #pour creer des utilisateurs test sans passer par l'inscription manuellement
    cursor = conn.cursor()
    
     #Exemple enseignant
    password_enseignant = "test1234"
    hashed_password_enseignant = bcrypt.hashpw(password_enseignant.encode('utf-8'), bcrypt.gensalt())
    
    cursor.execute("INSERT INTO users (email, password_hash, nom, prenom, role) VALUES (?, ?, ?, ?, ?)", ('professeur@universite.fr', hashed_password_enseignant.decode('utf-8'), 'prof', 'prof', 'enseignant'))
    
    #exemple etudiant
    password_etudiant = "test1234"
    hashed_password_etudiant = bcrypt.hashpw(password_etudiant.encode('utf-8'), bcrypt.gensalt())
    
    cursor.execute("INSERT INTO users (email, password_hash, nom, prenom, role) VALUES (?, ?, ?, ?, ?)", ('etudiant@etu.univ-amu.fr', hashed_password_etudiant.decode('utf-8'), 'etu', 'etu', 'etudiant'))
    
    conn.commit()
    
if __name__ == '__main__':
    init_database()
