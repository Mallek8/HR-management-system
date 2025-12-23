document.addEventListener("DOMContentLoaded", () => {
    fetch("/api/training-requests/supervisor/requests")
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById("trainingRequestsList");
            if (!container) return;

            if (data.length === 0) {
                container.innerHTML = `<p class="text-muted">Aucune demande de formation.</p>`;
                return;
            }

            container.innerHTML = data.map(req => `
                <div class="border rounded p-3 mb-3 shadow-sm">
                    <p><strong>Demande de :</strong> ${req.employee_name} (${req.employee_email})</p>
                    <p><strong>Formation :</strong> ${req.training_title}</p>
                    <p><strong>Statut :</strong> ${req.status}</p>
                    <p><strong>Commentaire :</strong> ${req.commentaire || "Aucun"}</p>
                    <div class="mt-2">
                        <button class="btn btn-success me-2" onclick="handleTrainingApproval(${req.id}, 'approuvé')">Approuver</button>
                        <button class="btn btn-danger" onclick="handleTrainingApproval(${req.id}, 'refusé')">Refuser</button>
                    </div>
                </div>
            `).join("");
        })
        .catch(err => {
            console.error("Erreur lors du chargement des demandes de formation", err);
        });
});
function handleTrainingApproval(requestId, decision) {
    const comment = prompt("Ajouter un commentaire (optionnel) :");

    fetch(`/api/training-requests/supervisor/validate/${requestId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ decision, comment })
    })
    .then(res => {
        if (!res.ok) throw new Error("Erreur serveur");
        return res.json();
    })
    .then(() => {
        alert("Décision enregistrée !");
        location.reload(); // Recharge les données
    })
    .catch(err => {
        console.error("Erreur", err);
        alert("Erreur lors de la validation.");
    });
}
