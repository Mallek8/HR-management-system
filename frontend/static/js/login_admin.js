// ==============================
// login_admin.js
// ==============================
// Script de gestion de la connexion administrateur
// ==============================

// Attente de la soumission du formulaire d'authentification
document.getElementById("adminLoginForm").addEventListener("submit", async function (event) {
    event.preventDefault(); // Empêche le rechargement de la page

    // Récupération des valeurs du formulaire
    const email = document.getElementById("admin_email").value;
    const password = document.getElementById("admin_password").value;

    // Envoi de la requête POST vers l'API d'authentification admin
    const response = await fetch("/api/auth/login_admin", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    // Gestion de la réponse
    if (response.ok) {
        const data = await response.json();
        // Redirection vers le dashboard si succès
        window.location.href = data.redirect;
    } else {
        // Affiche une erreur si les identifiants sont invalides
        alert("Email ou mot de passe incorrect");
    }
});
