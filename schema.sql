-- Schéma de la base de données pour l'application de prise de RDV

-- Table des utilisateurs (étudiants et enseignants)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK(role IN ('etudiant', 'enseignant')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des disponibilités des enseignants
CREATE TABLE IF NOT EXISTS disponibilites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enseignant_id INTEGER NOT NULL,
    jour DATE NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin TIME NOT NULL,
    est_disponible BOOLEAN DEFAULT 1,
    FOREIGN KEY (enseignant_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table des rendez-vous
CREATE TABLE IF NOT EXISTS rendez_vous (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    disponibilite_id INTEGER NOT NULL,
    etudiant_id INTEGER NOT NULL,
    enseignant_id INTEGER NOT NULL,
    date_heure_debut DATETIME NOT NULL,
    date_heure_fin DATETIME NOT NULL,
    motif TEXT,
    statut VARCHAR(20) DEFAULT 'confirmé' CHECK(statut IN ('confirmé', 'annulé')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (disponibilite_id) REFERENCES disponibilites(id) ON DELETE CASCADE,
    FOREIGN KEY (etudiant_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (enseignant_id) REFERENCES users(id) ON DELETE CASCADE
);