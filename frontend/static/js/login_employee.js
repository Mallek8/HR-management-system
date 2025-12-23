// ==============================
// login_employee.js
// ==============================
// Script de gestion de la connexion des employés
// ==============================

// Attente de la soumission du formulaire de connexion
document.getElementById("employeeLoginForm").addEventListener("submit", async function (event) {
    event.preventDefault(); // Empêche le rechargement automatique de la page

    // Récupération des champs du formulaire
    const email = document.getElementById("employee_email").value;
    const password = document.getElementById("employee_password").value;

    // Envoi d'une requête POST à l'API de connexion employé
    const response = await fetch("/api/auth/login_employee", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    // Analyse de la réponse
    if (response.ok) {
        const data = await response.json();
        // Redirection selon le rôle (dashboard employé ou superviseur)
        window.location.href = data.redirect;
    } else {
        // En cas d'erreur (identifiants incorrects)
        alert("Email ou mot de passe incorrect");
    }
});
