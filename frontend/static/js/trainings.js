// Ferme la modale
function closeTrainingModal() {
    document.getElementById("trainingModal").style.display = "none";
}

// Ouvre la modale
function openTrainingModal() {
    document.getElementById("trainingForm").reset();
    document.getElementById("trainingModal").style.display = "block";
}

// Injecte les formations dans le tableau
function renderTrainings(trainings) {
    const tbody = document.getElementById("trainingTableBody");
    tbody.innerHTML = "";

    if (trainings.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center">Aucune formation trouvée</td></tr>`;
        return;
    }

    trainings.forEach(t => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${t.title}</td>
            <td>${t.domain}</td>
            <td>${t.level}</td>
            <td>${t.start_date}</td>
            <td>${t.end_date}</td>
            <td>${t.target_department}</td>
        `;
        tbody.appendChild(tr);
    });
}

//modifier une formation,supprimer une formation
function renderTrainings(trainings) {
    const tbody = document.getElementById("trainingTableBody");
    tbody.innerHTML = "";

    if (trainings.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center">Aucune formation trouvée</td></tr>`;
        return;
    }

    trainings.forEach(training => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${training.title}</td>
            <td>${training.domain}</td>
            <td>${training.level}</td>
            <td>${training.start_date}</td>
            <td>${training.end_date}</td>
            <td>${training.target_department}</td>
            <td class="text-center">
                <button class="btn btn-sm btn-primary me-1" onclick='editTraining(${JSON.stringify(training)})'>
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick='deleteTraining(${training.id})'>
                    <i class="fas fa-trash-alt"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Charge les formations depuis l'API
async function loadTrainings() {
    const loading = document.getElementById("loadingMessage");
    const tbody = document.getElementById("trainingTableBody");

    try {
        loading.style.display = "block";
        const response = await fetch("/api/trainings");
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const trainings = await response.json();
        renderTrainings(trainings);
    } catch (error) {
        console.error("Erreur lors du chargement :", error);
        tbody.innerHTML = `<tr><td colspan="6" class="text-danger text-center">
            Erreur de chargement: ${error.message}
        </td></tr>`;
    } finally {
        if (loading) loading.style.display = "none";
    }
}

// Soumission du formulaire
async function submitTrainingForm(event) {
    event.preventDefault();

    const data = {
        title: document.getElementById("title").value,
        description: document.getElementById("description").value,
        domain: document.getElementById("domain").value,
        level: document.getElementById("level").value,
        start_date: document.getElementById("start_date").value,
        end_date: document.getElementById("end_date").value,
        target_department: document.getElementById("target_department").value
    };

    try {
        const response = await fetch("/api/trainings", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error("Erreur lors de la création");

        alert("Formation créée avec succès !");
        closeTrainingModal();
        loadTrainings();
    } catch (error) {
        alert("Erreur: " + error.message);
    }
}
function editTraining(training) {
    document.getElementById("trainingId").value = training.id;
    document.getElementById("title").value = training.title;
    document.getElementById("description").value = training.description;
    document.getElementById("domain").value = training.domain;
    document.getElementById("level").value = training.level;
    document.getElementById("start_date").value = training.start_date;
    document.getElementById("end_date").value = training.end_date;
    document.getElementById("target_department").value = training.target_department;

    document.getElementById("modalTitle").textContent = "Modifier la formation";
    document.getElementById("trainingModal").style.display = "block";
}

async function deleteTraining(id) {
    if (!confirm("Confirmez la suppression de cette formation ?")) return;

    try {
        const response = await fetch(`/api/trainings/${id}`, {
            method: "DELETE"
        });

        if (!response.ok) {
            throw new Error("Échec de la suppression");
        }

        alert("Formation supprimée.");
        loadTrainings();

    } catch (error) {
        console.error("Erreur suppression :", error);
        alert("Erreur lors de la suppression.");
    }
}
document.addEventListener("DOMContentLoaded", () => {
    const showBtn = document.getElementById("showRequestsBtn");
    const container = document.getElementById("requestsContainer");
    const tbody = document.getElementById("requestsTableBody");

    if (showBtn) {
        console.log("bouton détecté");

        showBtn.addEventListener("click", async () => {
            console.log("Bouton cliqué");
            try {
                const response = await fetch("/api/training-requests/full");
                if (!response.ok) throw new Error("Erreur serveur");

                const requests = await response.json();
                console.log("Requêtes reçues :", requests);

                tbody.innerHTML = ""; // vide le tableau

                if (requests.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="5" class="text-center">Aucune demande trouvée</td></tr>`;
                } else {
                    requests.forEach(req => {
                        const row = document.createElement("tr");
                        row.innerHTML = `
                            <td>${req.employee_name}</td>
                            <td>${req.employee_email}</td>
                            <td>${req.training_title}</td>
                            <td>${req.status}</td>
                            <td>${req.commentaire || ""}</td>
                            <td>
                                <button class="btn btn-sm btn-warning" onclick="sendToSupervisor(${req.id})">
                                Envoyer au superviseur
                                </button>
                            </td>
                        `;
                        tbody.appendChild(row);
                    });
                }

                container.style.display = "block"; // rend le tableau visible
            } catch (error) {
                console.error("Erreur lors de l'affichage des demandes :", error);
                alert("Erreur lors du chargement des demandes de formation");
            }
        });
    }
});
// Envoie la demande de formation au superviseur
async function sendToSupervisor(requestId) {
    try {
        const response = await fetch(`/api/training-requests/send-to-supervisor/${requestId}`, {
            method: "POST"
        });

        if (!response.ok) {
            throw new Error("Échec de l'envoi au superviseur.");
        }

        alert("Demande envoyée au superviseur !");
    } catch (err) {
        console.error("Erreur :", err);
        alert("Erreur lors de l'envoi au superviseur.");
    }
}

// Initialisation
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("addTrainingBtn").addEventListener("click", openTrainingModal);
    document.getElementById("trainingForm").addEventListener("submit", submitTrainingForm);
    loadTrainings();
});
console.log("trainings.js chargé");
