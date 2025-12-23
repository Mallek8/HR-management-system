// ==========================
// Utilitaire : Récupération de l'email via cookie
// ==========================

function getUserEmailFromCookie() {
    return document.cookie
        .replace(/(?:(?:^|.*;\s*)user_email\s*=\s*([^;]*).*$)|^.*$/, "$1")
        .replace(/(^"|"$)/g, '');
}

// ==========================
// Chargement des congés à approuver par le superviseur
// ==========================

document.addEventListener("DOMContentLoaded", async function () {
    const supervisorEmail = getUserEmailFromCookie();
    if (!supervisorEmail) return;

    try {
        const res = await fetch(`/api/leaves/supervisor-leaves/${supervisorEmail}`);
        if (!res.ok) throw new Error("Erreur récupération des congés");
        const leaves = await res.json();

        const tbody = document.getElementById("leaves-table-body");
        if (!tbody) return;

        tbody.innerHTML = "";

        leaves.forEach(leave => {
            const tr = document.createElement("tr");

            const approveButtons = leave.status === "en attente"
                ? `
                    <button class="btn btn-success btn-sm" onclick="approveLeave(${leave.id})">Approuver</button>
                    <button class="btn btn-danger btn-sm" onclick="rejectLeave(${leave.id})">Refuser</button>
                `
                : "—";

            tr.innerHTML = `
                <td>${leave.employee_name}</td>
                <td>${leave.start_date}</td>
                <td>${leave.end_date}</td>
                <td>${leave.status}</td>
                <td>${approveButtons}</td>
            `;

            tbody.appendChild(tr);
        });

    } catch (error) {
        console.error("Erreur lors du chargement des congés superviseur :", error);
    }
});

// ==========================
// Approuver une demande
// ==========================

async function approveLeave(leaveId) {
    try {
        const response = await fetch(`/api/leaves/${leaveId}/approve`, {
            method: "PUT"
        });

        if (response.ok) {
            alert("Congé approuvé avec succès.");
            location.reload();
        } else {
            alert("Erreur lors de l'approbation.");
        }

    } catch (error) {
        console.error("Erreur réseau lors de l'approbation :", error);
    }
}

// ==========================
// Rejeter une demande
// ==========================

async function rejectLeave(leaveId) {
    try {
        const response = await fetch(`/api/leaves/${leaveId}/reject`, {
            method: "PUT"
        });

        if (response.ok) {
            alert("Congé rejeté avec succès.");
            location.reload();
        } else {
            alert("Erreur lors du rejet.");
        }

    } catch (error) {
        console.error("Erreur réseau lors du rejet :", error);
    }
}

// ==========================
// Chargement des employés actuellement en congé
// ==========================

(async function loadEmployeesOnLeave() {
    const supervisorEmail = getUserEmailFromCookie();
    if (!supervisorEmail) return;

    try {
        const res = await fetch(`/api/leaves/on-leave/${supervisorEmail}`);
        if (!res.ok) throw new Error("Erreur récupération des absences");
        const employees = await res.json();

        const tbody = document.getElementById("on-leave-table-body");
        if (!tbody) return;

        tbody.innerHTML = "";

        employees.forEach(emp => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${emp.employee_name}</td>
                <td>${emp.role}</td>
                <td>${emp.start_date}</td>
                <td>${emp.end_date}</td>
            `;
            tbody.appendChild(tr);
        });

    } catch (error) {
        console.error("Erreur lors du chargement des employés en congé :", error);
    }
})();

// Fonction pour charger les demandes en attente
async function loadPendingRequests() {
    try {
        const response = await fetch('/api/leaves/supervisor/requests');
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Erreur HTTP: ${response.status}`);
        }
        const requests = await response.json();
        displayRequests(requests);
    } catch (error) {
        console.error('Erreur lors du chargement des demandes:', error);
        alert('Erreur lors du chargement des demandes: ' + error.message);
    }
}

// Fonction pour afficher les demandes
function displayRequests(requests) {
    const container = document.getElementById('requestsList');
    if (!container) {
        console.error('Élément requestsList non trouvé');
        return;
    }

    if (requests.length === 0) {
        container.innerHTML = '<div class="alert alert-info">Aucune nouvelle demande de congé</div>';
        return;
    }

    container.innerHTML = requests.map(request => `
        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">Demande de ${request.employee_name}</h5>
                <p class="card-text">
                    Période : du ${request.start_date} au ${request.end_date}<br>
                    Type : ${request.type}
                </p>
                <div class="btn-group">
                    <button onclick="approveRequest(${request.id})" class="btn btn-success">Approuver</button>
                    <button onclick="rejectRequest(${request.id})" class="btn btn-danger">Refuser</button>
                </div>
            </div>
        </div>
    `).join('');
}

// Fonction pour approuver une demande
async function approveRequest(leaveId) {
    try {
        const response = await fetch(`/api/leaves/supervisor/${leaveId}/approve`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Erreur HTTP: ${response.status}`);
        }

        const result = await response.json();
        alert(result.message);
        loadPendingRequests(); // Recharger les demandes
    } catch (error) {
        console.error('Erreur lors de l\'approbation:', error);
        alert('Erreur lors de l\'approbation: ' + error.message);
    }
}

// Fonction pour rejeter une demande
async function rejectRequest(leaveId) {
    try {
        const response = await fetch(`/api/leaves/supervisor/${leaveId}/reject`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Erreur HTTP: ${response.status}`);
        }

        const result = await response.json();
        alert(result.message);
        loadPendingRequests(); // Recharger les demandes
    } catch (error) {
        console.error('Erreur lors du rejet:', error);
        alert('Erreur lors du rejet: ' + error.message);
    }
}

// Charger les demandes au chargement de la page
document.addEventListener('DOMContentLoaded', loadPendingRequests);
