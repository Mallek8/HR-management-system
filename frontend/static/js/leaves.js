// ------------------------------------------------------
// Constants
// ------------------------------------------------------
// Couleurs pour les différents types de congés
const LEAVE_COLORS = {
    'approuvé': '#22c55e',    // Vert émeraude pour les congés approuvés
    'en attente': '#a78bfa',  // Violet lavande pour les congés en attente
    'refusé': '#ef4444',      // Rouge doux pour les congés refusés
};

/**
 * Retourne la classe Bootstrap en fonction du statut
 */
function getStatusClass(status) {
    switch (status) {
        case 'approuvé':
            return 'bg-success';
        case 'en attente':
            return 'bg-notification';
        case 'refusé':
            return 'bg-danger';
        default:
            return 'bg-secondary';
    }
}

// ------------------------------------------------------
// Initialisation après chargement du DOM
// ------------------------------------------------------
document.addEventListener("DOMContentLoaded", async function () {
    console.log("DOM chargé, démarrage du script leaves.js");
    
    // Vérifier les éléments essentiels du DOM
    const hasTable = !!document.getElementById("leave-requests-table");
    const hasCalendar = !!document.getElementById("leave-calendar");
    console.log("Table des congés présente:", hasTable);
    console.log("Calendrier présent:", hasCalendar);
    
    // Charger les données initiales
    await Promise.all([
        fetchLeaves(),
        fetchDepartments()
    ]);
    
    // Afficher le solde de congés si l'élément existe
    const leaveBalanceElement = document.getElementById('leave-balance');
    if (leaveBalanceElement) {
        await fetchAndDisplayLeaveBalance();
    }
    
    // Initialiser le calendrier
    if (hasCalendar) {
        // Attendre que FullCalendar soit chargé
        await new Promise((resolve) => {
            const checkFullCalendar = setInterval(() => {
                if (typeof FullCalendar !== 'undefined') {
                    clearInterval(checkFullCalendar);
                    resolve();
                }
            }, 100);
        });
        
        initCalendar();
    }
    
    // Charger et afficher les soldes récents
    await displayRecentBalances();
    
    // Test d'appel direct à l'API
    await testApiDirectly();
});

// ------------------------------------------------------
// Fonctions du calendrier
// ------------------------------------------------------

/**
 * Initialisation du calendrier FullCalendar
 */
function initCalendar() {
    const calendarEl = document.getElementById('leave-calendar');
    if (!calendarEl) {
        console.error("Élément calendrier non trouvé");
        return;
    }

    try {
        const calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'fr',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,listWeek'
            },
            height: '600px',
            events: async function(info, successCallback, failureCallback) {
                try {
                    const response = await fetch('/api/leaves/all');
                    if (!response.ok) {
                        throw new Error(`Erreur HTTP: ${response.status}`);
                    }
                    const events = await response.json();
                    
                    // Transformer les données pour FullCalendar
                    const calendarEvents = events.map(event => ({
                        id: event.id,
                        title: `${event.employee_name || 'Employé'} - ${event.type || 'Congé'}`,
                        start: event.start_date,
                        end: event.end_date,
                        backgroundColor: LEAVE_COLORS[event.status] || LEAVE_COLORS['en attente'],
                        borderColor: LEAVE_COLORS[event.status] || LEAVE_COLORS['en attente'],
                        extendedProps: {
                            status: event.status,
                            type: event.type,
                            employee: event.employee_name
                        }
                    }));
                    
                    successCallback(calendarEvents);
                } catch (error) {
                    console.error('Erreur lors du chargement des événements:', error);
                    failureCallback(error);
                }
            },
            eventClick: function(info) {
                showEventDetails(info.event);
            }
        });

        calendar.render();
        console.log('Calendrier initialisé avec succès');
    } catch (error) {
        console.error('Erreur lors de l\'initialisation du calendrier:', error);
    }
}

/**
 * Affiche les détails d'un événement
 */
function showEventDetails(event) {
    const modalTitle = document.getElementById('eventModalLabel');
    const modalBody = document.getElementById('eventModalBody');
    
    if (!modalTitle || !modalBody) {
        console.error('Éléments de modal non trouvés');
        return;
    }

    modalTitle.textContent = event.title;
    modalBody.innerHTML = `
        <p><strong>Statut:</strong> <span class="badge ${getStatusClass(event.extendedProps.status)}">${event.extendedProps.status}</span></p>
        <p><strong>Type:</strong> ${event.extendedProps.type}</p>
        <p><strong>Employé:</strong> ${event.extendedProps.employee}</p>
        <p><strong>Début:</strong> ${event.start ? event.start.toLocaleDateString() : 'Non défini'}</p>
        <p><strong>Fin:</strong> ${event.end ? event.end.toLocaleDateString() : 'Non défini'}</p>
    `;

    const modal = new bootstrap.Modal(document.getElementById('eventModal'));
    modal.show();
}

// Fonctions pour la gestion des congés

/**
 * Récupère et affiche le solde de congés de l'utilisateur connecté
 */
async function fetchAndDisplayLeaveBalance() {
    const email = getUserEmailFromCookie();
    if (!email) {
        document.getElementById('leave-balance').innerText = 'Non disponible';
        return;
    }
    
    try {
        const response = await fetch(`/request-leave/by-email?email=${encodeURIComponent(email)}`);
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status} ${response.statusText}`);
        }
        
        const employeeData = await response.json();
        if (!employeeData || !employeeData.id) {
            throw new Error("Données de l'employé non trouvées");
        }
        
        const balanceResponse = await fetch(`/api/leaves/balance/${employeeData.id}`);
        if (!balanceResponse.ok) {
            throw new Error(`Erreur HTTP: ${balanceResponse.status} ${balanceResponse.statusText}`);
        }
        
        const balanceData = await balanceResponse.json();
        document.getElementById('leave-balance').innerText = balanceData.balance;
    } catch (error) {
        console.error("Erreur lors de la récupération du solde:", error);
        document.getElementById('leave-balance').innerText = 'Non disponible';
    }
}

/**
 * Récupère et affiche les demandes de congés
 */
async function fetchLeaves() {
    console.log("Récupération des demandes de congés...");
    
    const tableBody = document.querySelector('#leave-requests-table tbody');
    if (!tableBody) {
        console.error("Corps de tableau non trouvé");
        return;
    }
    
    // Afficher un message de chargement
    tableBody.innerHTML = `
        <tr>
            <td colspan="8" class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Chargement...</span>
                </div>
            </td>
        </tr>
    `;
    
    try {
        // Récupérer les données des congés
        const response = await fetch('/api/leaves/');
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();
        
        console.log(`${data.length} demandes de congés récupérées`);
        
        if (!Array.isArray(data)) {
            tableBody.innerHTML = '<tr><td colspan="8" class="text-center">Format de données invalide</td></tr>';
            return;
        }
        
        if (data.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="8" class="text-center">Aucune demande trouvée</td></tr>';
            return;
        }

        // Calculer le nombre de congés approuvés par employé
        const approvedLeavesByEmployee = {};
        data.forEach(leave => {
            if (leave.status === 'approuvé') {
                if (!approvedLeavesByEmployee[leave.employee_name]) {
                    approvedLeavesByEmployee[leave.employee_name] = 0;
                }
                approvedLeavesByEmployee[leave.employee_name]++;
            }
        });
        
        // Vider le tableau
        tableBody.innerHTML = '';
        
        // Ajouter chaque demande
        data.forEach(leave => {
            const approvedCount = approvedLeavesByEmployee[leave.employee_name] || 0;
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${leave.id || ''}</td>
                <td>${leave.employee_name || 'Inconnu'}</td>
                <td>${leave.type || 'Congé'}</td>
                <td>${leave.start_date || 'Non défini'} - ${leave.end_date || 'Non défini'}</td>
                <td>
                    <span class="badge ${getStatusClass(leave.status)}">
                        ${leave.status || 'en attente'}
                    </span>
                </td>
                <td>${leave.comment || '-'}</td>
                <td>
                    <div class="btn-group">
                        <button class="btn btn-sm btn-primary" onclick="showResponseForm(${leave.id})">
                            Répondre
                        </button>
                    </div>
                </td>
                <td>
                    <span class="badge bg-info">
                        ${approvedCount} congé${approvedCount > 1 ? 's' : ''} approuvé${approvedCount > 1 ? 's' : ''}
                    </span>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error("Erreur lors de la récupération des demandes:", error);
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-danger">
                    <i class="bi bi-exclamation-triangle-fill me-2"></i>
                    Erreur: ${error.message}
                </td>
            </tr>
        `;
    }
}

/**
 * Affiche des congés de démonstration lorsque l'API ne retourne pas de données
 */
function displayDemoLeaves(tableBody) {
    const demoLeaves = [
        {
            id: 1,
            employee_name: "Martin Dupont",
            start_date: new Date(Date.now() + 7*24*60*60*1000).toISOString().split('T')[0],
            end_date: new Date(Date.now() + 14*24*60*60*1000).toISOString().split('T')[0],
            type: "Congé annuel",
            status: "en attente",
            comment: ""
        },
        {
            id: 2,
            employee_name: "Sophie Martin",
            start_date: new Date(Date.now() + 3*24*60*60*1000).toISOString().split('T')[0],
            end_date: new Date(Date.now() + 5*24*60*60*1000).toISOString().split('T')[0],
            type: "RTT",
            status: "approuvé",
            comment: "Bon repos"
        },
        {
            id: 3,
            employee_name: "Jean Dupuis",
            start_date: new Date(Date.now() - 2*24*60*60*1000).toISOString().split('T')[0],
            end_date: new Date(Date.now() + 3*24*60*60*1000).toISOString().split('T')[0],
            type: "Congé maladie",
            status: "approuvé",
            comment: "Prompt rétablissement"
        }
    ];
    
    // Vider le tableau
    tableBody.innerHTML = '';
    
    // Ajouter les congés de démonstration
    demoLeaves.forEach(leave => {
        const statusClass = getStatusClass(leave.status);
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${leave.id}</td>
            <td>${leave.employee_name}</td>
            <td>${leave.type}</td>
            <td>${leave.start_date} - ${leave.end_date}</td>
            <td><span class="badge ${statusClass}">${leave.status}</span></td>
            <td>${leave.comment || '-'}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="showResponseForm(${leave.id})">Répondre</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
    
    // Ajouter un message expliquant que ce sont des données de démo
    const infoRow = document.createElement('tr');
    infoRow.innerHTML = `
        <td colspan="7" class="text-center text-muted">
            <small><i>Ces données sont affichées à titre de démonstration uniquement.</i></small>
            <button class="btn btn-sm btn-outline-secondary mt-2" onclick="createTestLeaveManually()">
                Créer une véritable demande de test
            </button>
        </td>
    `;
    tableBody.appendChild(infoRow);
}

/**
 * Approuve une demande de congé
 */
async function approveLeave(leaveId) {
    try {
        const response = await fetch(`/api/leaves/${leaveId}/approve`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        alert(data.message);
        location.reload();
    } catch (error) {
        console.error('Erreur lors de l\'approbation:', error);
        alert('Erreur lors de l\'approbation: ' + error.message);
    }
}

/**
 * Rejette une demande de congé
 */
async function rejectLeave(leaveId) {
    try {
        const response = await fetch(`/api/leaves/${leaveId}/reject`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        alert(data.message);
        location.reload();
    } catch (error) {
        console.error('Erreur lors du rejet:', error);
        alert('Erreur lors du rejet: ' + error.message);
    }
}

// Fonction pour mettre à jour le tableau des congés
function updateLeaveTable(leaves) {
    const tableBody = document.querySelector('#leave-requests-table tbody');
    if (!tableBody) return;

    tableBody.innerHTML = leaves.map(leave => `
        <tr>
            <td>${leave.id}</td>
            <td>${leave.employee_name}</td>
            <td>${leave.type}</td>
            <td>${formatDateRange(leave.start_date, leave.end_date)}</td>
            <td>
                <span class="badge" style="background-color: ${LEAVE_COLORS[leave.status]}">
                    ${leave.status}
                </span>
            </td>
            <td>${leave.comment || '-'}</td>
            <td>
                <div class="btn-group">
                    <button class="btn btn-sm" style="background-color: ${LEAVE_COLORS['approuvé']}" onclick="approveLeave(${leave.id})">
                        <i class="bi bi-check-circle text-white"></i>
                    </button>
                    <button class="btn btn-sm" style="background-color: ${LEAVE_COLORS['refusé']}" onclick="rejectLeave(${leave.id})">
                        <i class="bi bi-x-circle text-white"></i>
                    </button>
                </div>
            </td>
            <td>${leave.balance || '-'}</td>
        </tr>
    `).join('');
}

// Fonction pour formater la plage de dates
function formatDateRange(start, end) {
    const startDate = new Date(start);
    const endDate = new Date(end);
    const options = { day: 'numeric', month: 'short', year: 'numeric' };
    return `${startDate.toLocaleDateString('fr-FR', options)} - ${endDate.toLocaleDateString('fr-FR', options)}`;
}

/**
 * Teste directement l'API pour vérifier si elle fonctionne
 */
async function testApiDirectly() {
    console.log("Test direct de l'API...");
    
    try {
        const response = await fetch('/api/leaves/');
        const status = response.status;
        const contentType = response.headers.get('content-type');
        
        let data = "Non disponible";
        try {
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
                data = JSON.stringify(data, null, 2);
            } else {
                data = await response.text();
            }
        } catch (e) {
            data = "Erreur lors de la lecture des données: " + e.message;
        }
        
        console.log(`API test result: Status ${status}, Content-Type: ${contentType}`);
        
        const resultDiv = document.getElementById('debug-info');
        if (resultDiv) {
            resultDiv.innerHTML = `
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <strong>Mes nouvelles réponses</strong>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Employé</th>
                                        <th>Dates</th>
                                        <th>Type</th>
                                        <th>Status</th>
                                        
                                    </tr>
                                </thead>
                                <tbody>
                                    ${JSON.parse(data).map(item => `
                                        <tr>
                                            <td>${item.id}</td>
                                            <td>${item.employee_name}</td>
                                            <td>${item.start_date} - ${item.end_date}</td>
                                            <td>${item.type}</td>
                                            <td>
                                                <span class="badge ${item.status === 'approuvé' ? 'bg-success' : 
                                                                    item.status === 'en attente' ? 'bg-warning' : 
                                                                    'bg-danger'}">
                                                    ${item.status}
                                                </span>
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
        }
        
        return {
            status,
            contentType,
            success: response.ok
        };
    } catch (error) {
        console.error("Erreur lors du test API:", error);
        
        const resultDiv = document.getElementById('debug-info');
        if (resultDiv) {
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    <h5 class="alert-heading">
                        <i class="bi bi-exclamation-triangle-fill me-2"></i>
                        Erreur lors du chargement des données
                    </h5>
                    <p class="mb-0">${error.message}</p>
                </div>
            `;
        }
        
        return {
            error: error.message,
            success: false
        };
    }
}

/**
 * Affiche des informations de débogage
 */
function refreshDebugInfo(error = null) {
    console.log("Rafraîchissement des informations de débogage");
    
    const debugElement = document.getElementById('debug-info');
    if (!debugElement) {
        console.error("Élément de débogage non trouvé");
        return;
    }
    
    const now = new Date().toLocaleTimeString();
    let html = `
        <div class="card">
            <div class="card-header bg-secondary text-white">
                <strong>Informations de débogage</strong> <small>(Mis à jour: ${now})</small>
            </div>
            <div class="card-body">
                <h6>Données utilisateur:</h6>
                <ul>
                    <li>Email connecté: <code>${getUserEmailFromCookie() || 'Non connecté'}</code></li>
                </ul>
                
                <h6>Éléments DOM:</h6>
                <ul>
                    <li>Table des congés: ${document.getElementById('leave-requests-table') ? '<span class="text-success">Trouvé</span>' : '<span class="text-danger">Non trouvé</span>'}</li>
                    <li>Calendrier: ${document.getElementById('leave-calendar') ? '<span class="text-success">Trouvé</span>' : '<span class="text-danger">Non trouvé</span>'}</li>
                    <li>FullCalendar: ${typeof FullCalendar !== 'undefined' ? '<span class="text-success">Disponible</span>' : '<span class="text-danger">Non disponible</span>'}</li>
                </ul>
                
                <h6>Structure de la table leaves:</h6>
                <pre class="small bg-light p-2">
employee_id (integer) | start_date (timestamp) | end_date (timestamp) | status (character) | admin_approved (boolean) | supervisor_id (integer) | type (character) | supervisor_comment (character)
                </pre>
                
                <button class="btn btn-sm btn-primary mb-3" onclick="testApiDirectly()">
                    Tester l'API directement
                </button>
            </div>
        </div>
    `;
    
    if (error) {
        html += `
            <div class="alert alert-danger">
                <h6>Dernière erreur:</h6>
                <strong>${error.message}</strong>
                <pre class="mt-2 small">${error.stack || 'Stack trace non disponible'}</pre>
            </div>
        `;
    }
    
    debugElement.innerHTML = html;
}

// Exposer les fonctions nécessaires au contexte global
window.showResponseForm = showResponseForm;
window.closeResponseForm = closeResponseForm;
window.submitResponse = submitResponse;
window.fetchLeaves = fetchLeaves;
window.approveLeave = approveLeave;
window.rejectLeave = rejectLeave;

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', async function() {
    console.log("Initialisation de la page...");
    
    try {
        // Charger les données initiales
        await fetchLeaves();
        
        // Initialiser les gestionnaires d'événements pour le modal
        const responseModal = document.getElementById('responseModal');
        if (responseModal) {
            responseModal.addEventListener('hidden.bs.modal', function () {
                // Réinitialiser le formulaire quand le modal est fermé
                const form = responseModal.querySelector('form');
                if (form) form.reset();
            });
        }
        
        // Charger les autres données en parallèle
        await Promise.all([
            displayCurrentBalance(),
            displayRecentBalances()
        ]);
        
        // Initialiser le calendrier si FullCalendar est disponible
        if (typeof FullCalendar !== 'undefined') {
            initCalendar();
        }
    } catch (error) {
        console.error("Erreur lors de l'initialisation:", error);
    }
});

/**
 * Affiche le formulaire de réponse pour une demande de congé
 */
function showResponseForm(leaveId) {
    console.log("Ouverture du modal de réponse pour la demande:", leaveId);
    const modal = document.getElementById('responseModal');
    if (!modal) {
        console.error("Modal de réponse non trouvé");
        return;
    }

    // Mettre à jour l'ID de la demande dans le formulaire
    const leaveIdInput = document.getElementById('leaveIdInput');
    if (leaveIdInput) {
        leaveIdInput.value = leaveId;
    }

    // Afficher le modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

// Ajouter un écouteur pour le changement de réponse
document.addEventListener('DOMContentLoaded', function() {
    const responseForm = document.getElementById('responseModal');
    if (responseForm) {
        const radioButtons = responseForm.querySelectorAll('input[name="response"]');
        const supervisorSection = document.getElementById('supervisorSection');
        
        radioButtons.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'forward') {
                    supervisorSection.style.display = 'block';
                } else {
                    supervisorSection.style.display = 'none';
                }
            });
        });
    }
});

/**
 * Soumet la réponse à une demande de congé
 */
async function submitResponse(event) {
    event.preventDefault();
    console.log("Soumission de la réponse...");
    
    const leaveId = document.getElementById('leaveIdInput').value;
    const response = document.querySelector('input[name="response"]:checked').value;
    const comment = document.getElementById('responseComment').value;

    try {
        let endpoint;
        let requestBody = { comment };

        if (response === 'forward') {
            const supervisorEmail = document.getElementById('supervisorEmail').value;
            if (!supervisorEmail) {
                alert("L'email du superviseur est requis pour transférer la demande.");
                return;
            }
            endpoint = `/api/leaves/${leaveId}/forward`;
            requestBody.supervisorEmail = supervisorEmail;
        } else {
            endpoint = response === 'approve' ? 
                `/api/leaves/${leaveId}/approve` : 
                `/api/leaves/${leaveId}/reject`;
        }

        console.log(`Envoi de la réponse à ${endpoint}`);
        const result = await fetch(endpoint, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!result.ok) {
            throw new Error(`Erreur HTTP: ${result.status}`);
        }

        const data = await result.json();
        alert(data.message || 'Réponse enregistrée avec succès');
        
        // Fermer le modal et rafraîchir la liste
        closeResponseForm();
        fetchLeaves();
        
    } catch (error) {
        console.error("Erreur lors de l'envoi de la réponse:", error);
        alert(`Erreur lors de l'envoi de la réponse: ${error.message}`);
    }
}

/**
 * Transfère une demande de congé au superviseur
 */
async function forwardToSupervisor(leaveId) {
    try {
        const comment = document.getElementById('responseComment').value;
        const response = await fetch(`/api/leaves/${leaveId}/forward`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                comment: comment
            })
        });

        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const data = await response.json();
        alert(data.message || 'Demande transférée au superviseur avec succès');
        
        // Fermer le modal et rafraîchir la liste
        closeResponseForm();
        fetchLeaves();
    } catch (error) {
        console.error("Erreur lors du transfert au superviseur:", error);
        alert(`Erreur lors du transfert au superviseur: ${error.message}`);
    }
}

/**
 * Ferme le formulaire de réponse
 */
function closeResponseForm() {
    console.log("Fermeture du modal de réponse");
    const modal = document.getElementById('responseModal');
    if (!modal) return;

    const bsModal = bootstrap.Modal.getInstance(modal);
    if (bsModal) {
        bsModal.hide();
    }
}

async function fetchDepartments() {
    try {
        const response = await fetch('/api/leaves/departments');
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        const departments = await response.json();
        updateDepartmentFilter(departments);
    } catch (error) {
        console.error("Erreur lors de la récupération des départements:", error);
        const deptFilter = document.getElementById('department-filter');
        if (deptFilter) {
            deptFilter.innerHTML = `
                <option value="">Erreur lors du chargement des départements</option>
            `;
        }
    }
}

function updateDepartmentFilter(departments) {
    const filter = document.getElementById('department-filter');
    if (!filter) return;

    // Ajouter l'option "Tous les départements"
    filter.innerHTML = '<option value="">Tous les départements</option>';
    
    departments.forEach(dept => {
        const option = document.createElement('option');
        option.value = dept.id;
        option.textContent = dept.name;
        filter.appendChild(option);
    });
}

function filterCalendarByDepartment(departmentId) {
    const calendar = document.getElementById('leave-calendar');
    if (!calendar) return;

    // Recharger les événements du calendrier avec le filtre
    const calendarApi = calendar.fullCalendar;
    if (calendarApi) {
        calendarApi.refetchEvents();
    }
}

// Fonction pour afficher les détails d'un employé
function displayEmployeeDetails(employeeData) {
    const modal = document.getElementById('employeeDetailsModal');
    if (!modal) return;

    const content = `
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Détails de l'employé</h5>
                <button type="button" class="close" data-dismiss="modal">&times;</button>
            </div>
            <div class="modal-body">
                <p><strong>Nom:</strong> ${employeeData.name}</p>
                <p><strong>Email:</strong> ${employeeData.email}</p>
                <p><strong>Rôle:</strong> ${employeeData.role}</p>
                <p><strong>Département:</strong> ${employeeData.department}</p>
                <p><strong>Solde de congés:</strong> ${employeeData.leave_balance} jours</p>
                <h6>Demandes en attente:</h6>
                <ul>
                    ${employeeData.pending_leaves.map(leave => `
                        <li>${leave.type} - Du ${leave.start_date} au ${leave.end_date}</li>
                    `).join('')}
                </ul>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-dismiss="modal">Fermer</button>
            </div>
        </div>
    `;

    modal.innerHTML = content;
    $(modal).modal('show');
}

/**
 * Crée manuellement une demande de congé de test
 */
function createTestLeaveManually() {
    console.log("Création manuelle d'une demande de test");
    
    const currentUser = getCurrentUser();
    const email = currentUser.email || 'test@example.com';
    
    // Dates de début et de fin (aujourd'hui + 1 jour et aujourd'hui + 5 jours)
    const today = new Date();
    const startDate = new Date(today);
    startDate.setDate(today.getDate() + 1);
    const endDate = new Date(today);
    endDate.setDate(today.getDate() + 5);
    
    const leaveData = {
        email: email,
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
        type: "Congé annuel",
        status: "en attente"
    };
    
    fetch('/api/leaves/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(leaveData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status} ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("Demande de test créée avec succès", data);
        fetchLeaves(); // Rafraîchir la liste
    })
    .catch(error => {
        console.error("Erreur lors de la création de la demande:", error);
        alert("Erreur lors de la création de la demande: " + error.message);
        
        // En cas d'échec, essayer l'endpoint de création de test
        console.log("Tentative avec l'endpoint de création de test...");
        createTestLeave();
    });
}

/**
 * Crée une demande de congé de test pour les démonstrations
 */
function createTestLeave() {
    console.log("Création d'une demande de congé de test...");
    
    return fetch('/api/leaves/create-test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok && response.status !== 500) {
            throw new Error(`Erreur HTTP: ${response.status} ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("Demande de test créée avec succès:", data);
        return data;
    })
    .catch(error => {
        console.error("Erreur lors de la création de la demande de test:", error);
        throw error;
    });
}

/**
 * Récupère l'email de l'utilisateur à partir des cookies
 */
function getUserEmailFromCookie() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'user_email') {
            return decodeURIComponent(value);
        }
    }
    return null;
}

/**
 * Récupère les informations de l'utilisateur courant
 */
function getCurrentUser() {
    const email = getUserEmailFromCookie();
    return { email };
}

/**
 * Filtre les demandes de congé par statut
 */
function filterLeavesByStatus(status) {
    // Récupérer toutes les lignes du tableau principal
    const allRows = document.querySelectorAll('#leave-requests-table tbody tr');
    
    // Si aucun statut spécifié, afficher toutes les lignes
    if (!status) {
        allRows.forEach(row => {
            row.style.display = '';
        });
        return;
    }
    
    // Sinon, masquer les lignes qui ne correspondent pas au statut spécifié
    allRows.forEach(row => {
        const statusCell = row.querySelector('td:nth-child(5) .badge');
        if (statusCell) {
            const rowStatus = statusCell.textContent.trim();
            if (rowStatus === status) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    });
    
    // Si aucune ligne visible, afficher un message
    let visibleCount = 0;
    allRows.forEach(row => {
        if (row.style.display !== 'none') {
            visibleCount++;
        }
    });
    
    if (visibleCount === 0) {
        const tbody = document.querySelector('#leave-requests-table tbody');
        if (tbody) {
            const messageRow = document.createElement('tr');
            messageRow.id = 'no-matching-leaves-message';
            messageRow.innerHTML = `
                <td colspan="7" class="text-center">
                    Aucune demande de congé avec le statut "${status}" trouvée.
                </td>
            `;
            tbody.appendChild(messageRow);
        }
    } else {
        // Supprimer le message s'il existe
        const message = document.getElementById('no-matching-leaves-message');
        if (message) {
            message.remove();
        }
    }
}

// Fonction pour obtenir la couleur du badge selon le solde
function getBalanceBadgeClass(balance) {
    if (typeof balance !== 'number') return 'bg-secondary';
    if (balance <= 0) return 'bg-danger';
    if (balance < 5) return 'bg-warning';
    return 'bg-success';
}

// Fonction pour afficher les soldes récents
async function displayRecentBalances() {
    const container = document.getElementById('recent-balances');
    if (!container) return;

    try {
        // Récupérer les absences de l'équipe
        const response = await fetch('/api/leaves/team-absences');
        if (!response.ok) {
            throw new Error('Erreur lors de la récupération des absences');
        }

        const absences = await response.json();
        console.log("Absences récupérées:", absences);
        
        if (absences.length === 0) {
            container.innerHTML = '<div class="alert alert-info">Aucune absence approuvée à afficher</div>';
            return;
        }

        // Créer un objet pour regrouper les absences par employé
        const employeeAbsences = {};
        absences.forEach(absence => {
            if (!employeeAbsences[absence.employee_id]) {
                employeeAbsences[absence.employee_id] = {
                    name: absence.employee_name,
                    department: absence.department_name,
                    absences: [],
                    totalDays: 0
                };
            }
            employeeAbsences[absence.employee_id].absences.push(absence);
            employeeAbsences[absence.employee_id].totalDays += absence.days;
        });

        // Convertir en tableau et trier par total de jours
        const sortedEmployees = Object.values(employeeAbsences)
            .sort((a, b) => b.totalDays - a.totalDays)
            .slice(0, 3); // Prendre les 3 premiers

        // Générer le HTML
        const html = `
            <div class="list-group">
                ${sortedEmployees.map(employee => `
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <div>
                                <h6 class="mb-0">${employee.name}</h6>
                                <small class="text-muted">${employee.department}</small>
                            </div>
                            <span class="badge bg-primary rounded-pill">
                                ${employee.totalDays} jour${employee.totalDays > 1 ? 's' : ''}
                            </span>
                        </div>
                        <div class="small">
                            ${employee.absences.map(absence => `
                                <div class="mb-1">
                                    <i class="bi bi-calendar-check text-success"></i>
                                    ${absence.type}: ${absence.start_date} au ${absence.end_date}
                                    <span class="badge bg-success">${absence.days} j</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        container.innerHTML = html;

    } catch (error) {
        console.error("Erreur lors de la récupération des absences:", error);
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                Erreur lors du chargement des données: ${error.message}
            </div>
        `;
    }
}

// Fonction pour afficher le solde de l'employé connecté
async function displayCurrentBalance() {
    const email = getUserEmailFromCookie();
    if (!email) {
        console.error("Email non trouvé");
        return;
    }

    try {
        const response = await fetch(`/api/leaves/balance/email/${encodeURIComponent(email)}`);
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const data = await response.json();
        const balanceElement = document.getElementById('current-balance');
        if (balanceElement) {
            const balance = data.balance;
            balanceElement.className = `badge ${getBalanceBadgeClass(balance)}`;
            balanceElement.textContent = typeof balance === 'number' ? 
                `${balance} jour${balance > 1 ? 's' : ''}` : 
                'Non disponible';
        }
    } catch (error) {
        console.error("Erreur lors de la récupération du solde:", error);
        const balanceElement = document.getElementById('current-balance');
        if (balanceElement) {
            balanceElement.className = 'badge bg-danger';
            balanceElement.textContent = 'Erreur';
        }
    }
}

/**
 * Vérifie automatiquement la disponibilité pour une demande de congés
 */
async function checkLeaveAvailability(employeeId, startDate, endDate) {
    try {
        // 1. Vérifier le solde de congés
        const balanceResponse = await fetch(`/api/leaves/balance/${employeeId}`);
        if (!balanceResponse.ok) {
            throw new Error(`Erreur lors de la vérification du solde: ${balanceResponse.status}`);
        }
        const balanceData = await balanceResponse.json();
        
        // Calculer le nombre de jours demandés
        const start = new Date(startDate);
        const end = new Date(endDate);
        const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1;
        
        if (balanceData.balance < days) {
            return {
                available: false,
                reason: `Solde insuffisant (${balanceData.balance} jours disponibles pour ${days} jours demandés)`
            };
        }
        
        // 2. Vérifier les congés de l'équipe
        const teamResponse = await fetch(`/api/leaves/all?start=${startDate}&end=${endDate}`);
        if (!teamResponse.ok) {
            throw new Error(`Erreur lors de la vérification des congés d'équipe: ${teamResponse.status}`);
        }
        const teamLeaves = await teamResponse.json();
        
        // Vérifier les conflits
        const conflicts = teamLeaves.filter(leave => 
            leave.employee_id !== employeeId && // Exclure les congés de l'employé actuel
            ((new Date(leave.start_date) <= end && new Date(leave.end_date) >= start)) // Vérifier le chevauchement
        );
        
        if (conflicts.length > 0) {
            return {
                available: false,
                reason: "Conflits avec d'autres congés dans l'équipe",
                conflicts: conflicts.map(leave => ({
                    employee: leave.employee_name,
                    period: `${leave.start_date} au ${leave.end_date}`
                }))
            };
        }
        
        return {
            available: true,
            balance: balanceData.balance,
            daysRequested: days
        };
    } catch (error) {
        console.error("Erreur lors de la vérification de disponibilité:", error);
        throw error;
    }
}

/**
 * Traite une nouvelle demande de congés
 */
async function processLeaveRequest(employeeId, startDate, endDate, type, comment) {
    try {
        // 1. Vérifier la disponibilité
        const availability = await checkLeaveAvailability(employeeId, startDate, endDate);
        
        if (!availability.available) {
            return {
                success: false,
                message: availability.reason
            };
        }
        
        // 2. Créer la demande
        const response = await fetch('/api/leaves/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                employee_id: employeeId,
                start_date: startDate,
                end_date: endDate,
                type: type,
                comment: comment
            })
        });
        
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        // 3. Notifier le responsable
        await notifySupervisor(data.id);
        
        return {
            success: true,
            message: "Demande créée avec succès",
            leaveId: data.id
        };
    } catch (error) {
        console.error("Erreur lors du traitement de la demande:", error);
        throw error;
    }
}

/**
 * Notifie le responsable d'une nouvelle demande
 */
async function notifySupervisor(leaveId) {
    try {
        const response = await fetch(`/api/leaves/${leaveId}/notify`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error("Erreur lors de la notification:", error);
        throw error;
    }
}