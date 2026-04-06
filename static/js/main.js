"use strict";
// Validation du formulaire d'inscription
document.addEventListener('DOMContentLoaded', function() {
    const signupForm = document.getElementById('signup-form');

    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const passwordConfirm = document.getElementById('password_confirm').value;

            // Validation email
            if (!validateEmail(email)) {
                e.preventDefault();
                alert("Format d'email invalide");
                return;
            }

            //Validation mot de passe
            if (password.length < 8) {
                e.preventDefault();
                alert('Le mot de passe doit contenir au moins 8 caractères');
                return;
            }

            // Vérification correspondance mots de passe
            if (password !== passwordConfirm) {
                e.preventDefault();
                alert('Les mots de passe ne correspondent pas');
                return;
            }
        });
    }
});
// En dehors du DOM puisqu'on met uniquement dans le DOM ce qui est executée, pas ce qui est déclaré
// Fonction de validation d'email
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Confirmation avant suppression
function confirmDelete(message) {
    return confirm(message || 'Etes-vous sûr de vouloir supprimer cet élément ?');
}
