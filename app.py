from datetime import datetime
from functools import wraps
import re

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session

from models.disponibilite import (
    create_disponibilite,
    delete_disponibilite,
    generer_creneaux_disponibles,
    get_disponibilites_enseignant,
    get_jours_avec_disponibilites,
)
from models.rendez_vous import (
    annuler_rendez_vous,
    create_rendez_vous,
    get_rendez_vous_enseignant,
    get_rendez_vous_enseignant_futurs,
    get_rendez_vous_etudiant,
    get_rendez_vous_etudiant_futurs,
)
from models.user import create_user, get_all_enseignants, get_user_by_id, verify_password

# Créer l'application Flask
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'dyljab1234'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['DATABASE'] = 'rdv.db'

# Initialiser les sessions
Session(app)


def validate_email(email):
    # Vérifier le bon format du mail
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    # Vérifie que le mot de passe a au moins 8 caractères
    return len(password) >= 8


def login_required(f):
    # Vérifie si l'utilisateur est connecté
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vous devez être connecté pour accéder à cette page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def etudiant_required(f):
    # Vérifie si l'utilisateur est un étudiant
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'etudiant':
            flash('Accès réservé aux étudiants', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def enseignant_required(f):
    # Vérifie si l'utilisateur est connecté en tant qu'enseignant
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'enseignant':
            flash('Accès réservé aux enseignants', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


# route principale
@app.route('/')
def index():
    #Retourne sur la bonne page selon la session
    if 'user_id' not in session:
        return redirect(url_for('login'))

    role = session.get('role')
    if role == 'etudiant':
        return redirect(url_for('etudiant_dashboard'))
    if role == 'enseignant':
        return redirect(url_for('enseignant_dashboard'))
    return redirect(url_for('logout'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Formulaire de login
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        #Vérifier les identifiants
        user = verify_password(email, password)

        if user:
            # Créer la session
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['nom'] = user['nom']
            session['prenom'] = user['prenom']

            #Rediriger vers le dashboard approprié
            if user['role'] == 'etudiant':
                return redirect(url_for('etudiant_dashboard'))
            return redirect(url_for('enseignant_dashboard'))

        flash('Email ou mot de passe incorrect', 'error')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    #Formulaire d'inscription
    if request.method == 'POST':
        email = request.form.get('email', '').strip() # strip pour retirer les espaces inutiles
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        nom = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        role = request.form.get('role', '')

        # On créer un tableau d'erreur
        errors = []

        # On verifie avant d'insert dans la db que tous les champs sont ok, si il y a une erreur on l'insert dans le tableau errors
        if not validate_email(email):
            errors.append("Format d'email invalide")
        if not validate_password(password):
            errors.append("Le mot de passe doit contenir au moins 8 caractères")
        if password != password_confirm:
            errors.append("Les mots de passe ne correspondent pas")
        if not nom or not prenom:
            errors.append("Le nom et le prénom sont obligatoires")
        if role not in ['etudiant', 'enseignant']:
            errors.append("Rôle invalide")

        # Si le tableau errors n'est pas vide alors on affiche l'erreur en question
        if errors:
            for error in errors:
                flash(error, 'error')
        # Sinon tout est OK et donc on peut insert dans la table
        else:
            user_id = create_user(email, password, nom, prenom, role)
            if user_id:
                flash('Compte créé avec succès,Vous pouvez maintenant vous connecter.', 'success')
                return redirect(url_for('login'))
            flash('Cet email est déjà utilisé', 'error')

    return render_template('signup.html')


@app.route('/logout')
def logout():
    #Déconnecte l'utilisateur
    session.clear()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('login'))


#Dashboard etudiant
@app.route('/etudiant/dashboard')
@login_required
@etudiant_required
def etudiant_dashboard():
    enseignants = get_all_enseignants()
    rdv_futurs = get_rendez_vous_etudiant_futurs(session['user_id'])
    return render_template('dashboard_etudiant.html', enseignants=enseignants, rdv_futurs=rdv_futurs)


#Affiche les creneaux d'un enseignant par l'id de celui-ci
@app.route('/etudiant/rdv/<int:enseignant_id>')
@login_required
@etudiant_required
def selection_creneau(enseignant_id):
    # On get toutes les informations de l'enseignant à partir de son id
    enseignant = get_user_by_id(enseignant_id)

    # On check si l'enseignant existe
    if not enseignant or enseignant['role'] != 'enseignant':
        flash('Enseignant non trouvé', 'error')
        return redirect(url_for('etudiant_dashboard'))

    # On get les jours disponibles du prof
    jours_disponibles = get_jours_avec_disponibilites(enseignant_id)
    jour_selectionne = request.args.get('jour')
    creneaux = []

    # On verifie les créneaux disponibles le jour selectionné en question
    if jour_selectionne and jour_selectionne in jours_disponibles:
        creneaux = generer_creneaux_disponibles(enseignant_id, jour_selectionne)

    # Puis on affiche
    return render_template(
        'selection_creneau.html',
        enseignant=enseignant,
        jours_disponibles=jours_disponibles,
        jour_selectionne=jour_selectionne,
        creneaux=creneaux,
    )


# Reservation du RDV par un eleve
@app.route('/etudiant/rdv', methods=['POST'])
@login_required
@etudiant_required
def reserver_rdv():
    disponibilite_id = request.form.get('disponibilite_id')
    enseignant_id = request.form.get('enseignant_id')
    date_heure_debut = request.form.get('date_heure_debut')
    date_heure_fin = request.form.get('date_heure_fin')
    motif = request.form.get('motif', '').strip()

    # Si une donnée manque on previent l'utilisateur (au cas où ça arrive)
    if not all([disponibilite_id, enseignant_id, date_heure_debut, date_heure_fin]):
        flash('Données manquantes', 'error')
        return redirect(url_for('etudiant_dashboard'))

    # On crée le rdv 
    rdv_id = create_rendez_vous(
        disponibilite_id=disponibilite_id,
        etudiant_id=session['user_id'],
        enseignant_id=enseignant_id,
        date_heure_debut=date_heure_debut,
        date_heure_fin=date_heure_fin,
        motif=motif,
    )

    # On previent que la création s'est passée avec succès et on redirige vers la page de tous les rdv pris par l'utilisateur
    if rdv_id:
        flash('Rendez-vous crée avec succès', 'success')
        return redirect(url_for('mes_rdv_etudiant'))

    # Sinon on prévient que le créneau n'est plus disponible et on redirige sur la même page qu'avant
    flash("Ce créneau n'est plus disponible", 'error')
    return redirect(url_for('selection_creneau', enseignant_id=enseignant_id))


# Affiche les rdv reservée de l'etudiant
@app.route('/etudiant/mes-rdv')
@login_required
@etudiant_required
def mes_rdv_etudiant():
    rendez_vous = get_rendez_vous_etudiant(session['user_id'])
    return render_template('mes_rendez_vous.html', rendez_vous=rendez_vous, role='etudiant')


# Annulation d'un rdv
@app.route('/etudiant/rdv/<int:rdv_id>/annuler', methods=['POST'])
@login_required
@etudiant_required
def annuler_rdv(rdv_id):
    if annuler_rendez_vous(rdv_id, session['user_id']):
        flash('Rendez-vous annulé avec succès', 'success')
    else:
        flash("Impossible d'annuler ce rendez-vous", 'error')
    return redirect(url_for('mes_rdv_etudiant'))


# Dashboard principal d'un utilisateur enseignant
@app.route('/enseignant/dashboard')
@login_required
@enseignant_required
def enseignant_dashboard():
    disponibilites = get_disponibilites_enseignant(session['user_id'])
    rdv_futurs = get_rendez_vous_enseignant_futurs(session['user_id'])
    return render_template('dashboard_enseignant.html', disponibilites=disponibilites, rdv_futurs=rdv_futurs)


# Get tous les créneaux de l'enseignants
@app.route('/enseignant/disponibilites')
@login_required
@enseignant_required
def disponibilites():
    dispos = get_disponibilites_enseignant(session['user_id'])
    return render_template('disponibilites.html', disponibilites=dispos)


# Ajouter un créneau enseignant
@app.route('/enseignant/disponibilites', methods=['POST'])
@login_required
@enseignant_required
def ajouter_disponibilite():
    # Recup les informations du formulaire
    jour = request.form.get('jour')
    heure_debut = request.form.get('heure_debut')
    heure_fin = request.form.get('heure_fin')

    # On crée un tableau errors
    errors = []


    # Gestion des erreurs qu'on ajoute dans le tableau errors
    if not jour:
        errors.append("La date est obligatoire")
    if not heure_debut or not heure_fin:
        errors.append("Les heures de début et fin sont obligatoires")

    # On verifie les incohérences de temps, pour éviter de prendre rdv avant la date d'aujourd'hui
    try:
        date_jour = datetime.strptime(jour, "%Y-%m-%d").date()
        if date_jour < datetime.now().date():
            errors.append("Impossible de créer une disponibilité dans le passé")
    # Ici on verifie simplement le format de date (on ne sait jamais)
    except ValueError:
        errors.append("Format de date invalide")
    # On verifie que l'heure de fin ne soit pas avant l'heure de début
    try:
        debut = datetime.strptime(heure_debut, "%H:%M").time()
        fin = datetime.strptime(heure_fin, "%H:%M").time()
        if fin <= debut:
            errors.append("L'heure de fin doit être après l'heure de début")
    # Idem ici on verifie le format de date
    except ValueError:
        errors.append("Format d'heure invalide")

    # On affiche les erreurs et on redirige sur la même page si il y en a
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('disponibilites'))

    # Sinon on insert dans la table de disponibilité le créneau en question
    dispo_id = create_disponibilite(
        enseignant_id=session['user_id'],
        jour=jour,
        heure_debut=heure_debut,
        heure_fin=heure_fin,
    )

    # On affiche si l'insertion s'est fait avec succès ou non
    if dispo_id:
        flash('Disponibilité ajoutée avec succès !', 'success')
    else:
        flash("Erreur lors de l'ajout de la disponibilité", 'error')

    return redirect(url_for('disponibilites'))


# Supprimer une disponibilité
@app.route(
    '/enseignant/disponibilites/<int:dispo_id>/supprimer',
    methods=['POST'],
)
@login_required
@enseignant_required
def supprimer_disponibilite(dispo_id):
    if delete_disponibilite(dispo_id):
        flash('Disponibilité supprimée avec succès', 'success')
    else:
        flash('Impossible de supprimer cette disponibilité (des rendez-vous sont déjà planifiés)', 'error')
    return redirect(url_for('disponibilites'))


# Affiche les rdv de l'enseignant
@app.route('/enseignant/mes-rdv')
@login_required
@enseignant_required
def mes_rdv_enseignant():
    rendez_vous = get_rendez_vous_enseignant(session['user_id'])
    return render_template('mes_rendez_vous.html', rendez_vous=rendez_vous, role='enseignant')


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
