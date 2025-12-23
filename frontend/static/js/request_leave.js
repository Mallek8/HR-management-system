// ------------------------------------------------------
// Récupérer l'email utilisateur depuis les cookies
// ------------------------------------------------------
function getUserEmailFromCookie() {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith('user_email=')) {
            // Enlever les guillemets si présents
            const email = decodeURIComponent(cookie.substring('user_email='.length)).trim();
            return email.replace(/^"(.*)"$/, '$1'); // Enlever les guillemets au début et à la fin
        }
    }
    return null;
}

// ------------------------------------------------------
// Récupérer l'ID employé à partir de l'email
// ------------------------------------------------------
async function fetchEmployeeIdByEmail(email) {
    if (!email) {
        console.error("Email non trouvé dans les cookies");
        return null;
    }

    try {
        // Nettoyer l'email des guillemets potentiels
        const cleanEmail = email.replace(/^"(.*)"$/, '$1');
        const response = await fetch(`/api/leaves/employee/${encodeURIComponent(cleanEmail)}`);
        
        if (response.status === 404) {
            console.warn("Employé non trouvé dans la base de données");
            return null;
        }
        
        if (!response.ok) {
            console.error("Erreur lors de la récupération de l'ID de l'employé", response.statusText);
            const errorText = await response.text();
            console.error("Détails de l'erreur:", errorText);
            return null;
        }
        
        const data = await response.json();
        console.log("Données de l'employé:", data);
        
        // Mettre à jour le nom de l'employé sur la page s'il existe
        const employeeNameElement = document.getElementById('employee-name');
        if (employeeNameElement && data.name) {
            employeeNameElement.textContent = data.name;
        }
        
        return data.id;
    } catch (error) {
        console.error("Exception lors de la récupération de l'ID:", error);
        return null;
    }
}

// ------------------------------------------------------
// Soumission du formulaire de demande de congé
// ------------------------------------------------------
async function handleSubmit(event) {
    event.preventDefault();
    
    // Récupérer les données du formulaire
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const leaveType = document.getElementById('leaveType').value;
    
    // Vérifier que tous les champs obligatoires sont remplis
    if (!startDate || !endDate || !leaveType) {
        showError("Veuillez remplir tous les champs obligatoires");
        return;
    }
    
    // Récupérer l'email de l'utilisateur
    const email = getUserEmailFromCookie();
    if (!email) {
        showError("Impossible de récupérer votre email");
        return;
    }
    
    // Récupérer l'ID de l'employé
    const employeeId = await fetchEmployeeIdByEmail(email);
    if (!employeeId) {
        showError("Impossible de récupérer votre identifiant");
        return;
    }
    
    // Convertir les dates en objets Date
    const startDateTime = new Date(startDate + 'T00:00:00');
    const endDateTime = new Date(endDate + 'T23:59:59');
    
    // Vérifier que la date de fin est après la date de début
    if (endDateTime < startDateTime) {
        showError("La date de fin doit être après la date de début");
        return;
    }
    
    // Préparer les données à envoyer
    const leaveData = {
        employee_id: employeeId,
        start_date: startDateTime.toISOString(),  // Format ISO pour le backend
        end_date: endDateTime.toISOString(),      // Format ISO pour le backend
        type: leaveType,
        status: "en attente",
        admin_approved: false
    };
    
    // Afficher un indicateur de chargement sur le bouton
    const submitButton = document.getElementById('submitButton');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Envoi en cours...';
    }
    
    try {
        // Envoyer la demande
        console.log("Envoi des données:", leaveData);

        const response = await fetch('/request-leave/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(leaveData)
        });
        
        console.log("Réponse reçue:", response);
        
        // Récupérer la réponse en JSON
        const responseData = await response.json();
        console.log("Données de réponse:", responseData);
        
        // Vérifier si la réponse est OK
        if (!response.ok) {
            throw new Error(responseData.detail || "Erreur lors de l'envoi de la demande");
        }
        
        // Afficher le message de succès et le contenu de la réponse
        const successMessage = `Demande de congé créée avec succès!\nID: ${responseData.id}\nStatut: ${responseData.status}`;
        showSuccess(successMessage);
        
        // Réinitialiser le formulaire
        document.getElementById('leaveRequestForm').reset();
        
        // Actualiser les données
        await Promise.all([
            fetchAndDisplayLeaveRequests(),
            fetchAndDisplayLeaveBalance(),
            fetchAndCalculateStats()
        ]);
        
    } catch (error) {
        console.error("Erreur lors de l'envoi de la demande:", error);
        showError(error.message);
    } finally {
        // Rétablir le bouton
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.innerHTML = '<i class="bi bi-send me-1"></i> Soumettre la demande';
        }
    }
}

// ------------------------------------------------------
// Récupérer et afficher les statistiques de congés
// ------------------------------------------------------
async function fetchAndCalculateStats() {
    const email = getUserEmailFromCookie();
    if (!email) {
        console.error("Email non trouvé dans les cookies");
        return;
    }
    
    const employeeId = await fetchEmployeeIdByEmail(email);
    if (!employeeId) {
        console.error("Impossible de récupérer l'ID de l'employé");
        return;
    }
    
    try {
        // Récupérer les demandes de congés de l'utilisateur
        const response = await fetch('/api/leaves/all');
        
        if (!response.ok) {
            console.error("Erreur lors de la récupération des demandes de congé:", response.statusText);
            return;
        }
        
        const data = await response.json();
        
        // Filtrer pour n'avoir que les demandes de l'utilisateur connecté
        const userLeaves = data.filter(leave => leave.employee_id === employeeId);
        
        // Compter les congés utilisés et en attente
        const currentYear = new Date().getFullYear();
        const startOfYear = new Date(currentYear, 0, 1); // 1er janvier de l'année courante
        
        let usedDays = 0;
        let pendingCount = 0;
        
        userLeaves.forEach(leave => {
            const startDate = new Date(leave.start_date);
            const endDate = new Date(leave.end_date);
            
            // Calculer le nombre de jours
            const diffTime = Math.abs(endDate - startDate);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
            
            if (leave.status === 'approuvé' && startDate >= startOfYear) {
                usedDays += diffDays;
            } else if (leave.status === 'en attente') {
                pendingCount++;
            }
        });
        
        // Mettre à jour les valeurs sur la page
        const leaveUsedElement = document.getElementById('leave-used');
        const leavePendingElement = document.getElementById('leave-pending');
        
        if (leaveUsedElement) {
            leaveUsedElement.textContent = usedDays;
        }
        
        if (leavePendingElement) {
            leavePendingElement.textContent = pendingCount;
        }
        
        // Mettre à jour le badge de vérification du solde
        const leaveBalanceCheckElement = document.getElementById('leave-balance-check');
        if (leaveBalanceCheckElement) {
            const balance = parseInt(document.getElementById('leave-balance').textContent);
            if (!isNaN(balance)) {
                leaveBalanceCheckElement.textContent = balance + ' jours';
            }
        }
        
    } catch (error) {
        console.error("Erreur lors du calcul des statistiques:", error);
    }
}

// ------------------------------------------------------
// Récupérer et afficher le solde de congés
// ------------------------------------------------------
async function fetchAndDisplayLeaveBalance(employeeId) {
    try {
        if (!employeeId) {
            throw new Error("ID employé non fourni");
        }
        
        console.log(`Récupération du solde de congés pour l'employé ID: ${employeeId}`);
        const response = await fetch(`/api/leaves/balance/${employeeId}`);
        
        if (!response.ok) {
            console.error(`Erreur HTTP: ${response.status} - ${response.statusText}`);
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        console.log("Données de solde reçues:", data);
        
        const balanceElement = document.getElementById('leave-balance');
        
        if (data && typeof data.balance !== 'undefined') {
            balanceElement.textContent = `${data.balance} jours`;
            balanceElement.classList.add('bg-primary');
            balanceElement.classList.remove('bg-danger');
        } else {
            throw new Error("Solde de congés non disponible");
        }
        
    } catch (error) {
        console.error("Erreur lors de la récupération du solde de congés:", error);
        
        // Options pour gérer l'erreur:
        // 1. Masquer la section de solde
        const balanceElement = document.getElementById('leave-balance');
        const balanceRow = balanceElement.closest('p');
        
        if (balanceRow) {
            // Option 1: Masquer complètement
            balanceRow.style.display = 'none';
            
            // Option 2: Afficher un message d'erreur à la place
            // balanceElement.textContent = "Non disponible";
            // balanceElement.classList.remove('bg-primary');
            // balanceElement.classList.add('bg-danger');
        }
    }
}

// ------------------------------------------------------
// Écouteur d'événements pour le chargement de la page
// ------------------------------------------------------
document.addEventListener("DOMContentLoaded", async function () {
    console.log("Page chargée, initialisation...");
    
    try {
        // Vérifier si FullCalendar est disponible
        if (typeof FullCalendar === 'undefined') {
            console.error("FullCalendar n'est pas disponible");
            // Attendre que FullCalendar soit chargé
            await new Promise((resolve) => {
                const checkFullCalendar = setInterval(() => {
                    if (typeof FullCalendar !== 'undefined') {
                        clearInterval(checkFullCalendar);
                        resolve();
                    }
                }, 100);
            });
        }

        // Initialiser le calendrier une fois FullCalendar disponible
        console.log("Initialisation du calendrier...");
        await initializeLeaveCalendar();
        
        // Charger les autres données
        console.log("Chargement des données...");
        await Promise.all([
            fetchAndDisplayLeaveBalance(),
            fetchAndDisplayLeaveRequests(),
            fetchDepartments()
        ]);
        
        console.log("Initialisation terminée");
    } catch (error) {
        console.error("Erreur lors de l'initialisation:", error);
    }
});

// ------------------------------------------------------
// Affichage des demandes de congé
// ------------------------------------------------------   
async function fetchAndDisplayLeaveRequests() {
    console.log("Chargement des demandes de congé...");
    const leaveRequestsList = document.getElementById('leave-requests-list');
    if (!leaveRequestsList) {
        console.error("Élément 'leave-requests-list' non trouvé");
        return;
    }

    const email = getUserEmailFromCookie();
    if (!email) {
        leaveRequestsList.innerHTML = '<li class="list-group-item text-danger">Impossible de récupérer votre email</li>';
        return;
    }
    
    const employeeId = await fetchEmployeeIdByEmail(email);
    if (!employeeId) {
        leaveRequestsList.innerHTML = '<li class="list-group-item text-danger">Impossible de récupérer votre identifiant</li>';
        return;
    }
    
    // Afficher un message de chargement
    leaveRequestsList.innerHTML = '<li class="list-group-item text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement...</span></div></li>';
    
    try {
        // Récupérer toutes les demandes
        const response = await fetch('/api/leaves/all');
        
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        console.log("Données des demandes de congé:", data);
        
        // Filtrer pour n'afficher que les demandes de l'utilisateur connecté
        const userLeaves = data.filter(leave => leave.employee_id === employeeId);
        
        if (userLeaves.length === 0) {
            leaveRequestsList.innerHTML = '<li class="list-group-item text-center text-muted">Aucune demande de congé trouvée</li>';
            return;
        }
        
        // Mettre à jour la liste des demandes
        leaveRequestsList.innerHTML = '';
        
        userLeaves.forEach(leave => {
            const startDate = new Date(leave.start_date).toLocaleDateString('fr-FR');
            const endDate = new Date(leave.end_date).toLocaleDateString('fr-FR');
            
            // Déterminer la couleur et l'icône en fonction du statut
            let statusBadgeClass = 'bg-warning';
            let icon = 'bi-hourglass-split';
            let statusText = 'En attente';
            
            if (leave.status === 'approuvé') {
                statusBadgeClass = 'bg-success';
                icon = 'bi-check-circle-fill';
                statusText = 'Approuvé';
            } else if (leave.status === 'refusé') {
                statusBadgeClass = 'bg-danger';
                icon = 'bi-x-circle-fill';
                statusText = 'Refusé';
            }
            
            const leaveItem = document.createElement('li');
            leaveItem.className = 'list-group-item';
            leaveItem.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <span class="badge ${statusBadgeClass} me-2">
                            <i class="bi ${icon} me-1"></i>${statusText}
                        </span>
                        <strong>${leave.type || 'Congé'}</strong>
                    </div>
                    <small class="text-muted">#${leave.id}</small>
                </div>
                <div class="mt-1">
                    <i class="bi bi-calendar3 me-1"></i> ${startDate} - ${endDate}
                </div>
                ${leave.supervisor_comment ? `<div class="mt-1 small text-muted">Réponse du superviseur: "${leave.supervisor_comment}"</div>` : ''}
            `;
            leaveRequestsList.appendChild(leaveItem);
        });
    } catch (error) {
        console.error("Exception lors de la récupération des demandes:", error);
        leaveRequestsList.innerHTML = `<li class="list-group-item text-danger">Erreur technique: ${error.message}</li>`;
    }
}

// ------------------------------------------------------
// Récupérer et afficher les départements
// ------------------------------------------------------
async function fetchDepartments() {
    const selectElement = document.getElementById('department-filter');
    if (!selectElement) return;
    
    try {
        const response = await fetch('/api/leaves/departments');
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        
        const departments = await response.json();
        
        // Vider le select sauf l'option "Tous les départements"
        selectElement.innerHTML = '<option value="">Tous les départements</option>';
        
        // Ajouter les départements de la base de données
        departments.forEach(dept => {
            const option = document.createElement('option');
            option.value = dept.id;
            option.textContent = dept.name;
            selectElement.appendChild(option);
        });
        
    } catch (error) {
        console.error("Erreur lors de la récupération des départements:", error);
        selectElement.innerHTML = '<option value="">Erreur de chargement</option>';
    }
}

// ------------------------------------------------------
// Filtre le calendrier par département
// ------------------------------------------------------
function filterCalendarByDepartment(departmentId) {
    const calendar = document.querySelector('#leave-calendar')?.calendar;
    if (!calendar) return;
    
    calendar.refetchEvents();
}

// Fonction pour initialiser le calendrier des absences
function initializeLeaveCalendar(retryCount = 0) {
    console.log('Tentative d\'initialisation du calendrier...');
    
    // Vérifier que FullCalendar est disponible
    if (typeof FullCalendar === 'undefined') {
        console.warn(`FullCalendar n'est pas disponible (tentative ${retryCount + 1}/5)`);
        if (retryCount < 5) {
            setTimeout(() => initializeLeaveCalendar(retryCount + 1), 1000);
        } else {
            console.error("Impossible de charger FullCalendar après 5 tentatives");
            const calendarEl = document.getElementById('leave-calendar');
            if (calendarEl) {
                calendarEl.innerHTML = '<div class="alert alert-danger">Erreur: Impossible de charger le calendrier. Veuillez rafraîchir la page.</div>';
            }
        }
        return;
    }

    const calendarEl = document.getElementById('leave-calendar');
    if (!calendarEl) {
        console.error("Élément 'leave-calendar' non trouvé");
        return;
    }

    try {
        console.log('Initialisation du calendrier...');
        
        // Initialiser le calendrier
        const calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'fr',
            height: 'auto',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek'
            },
            events: async function(info, successCallback, failureCallback) {
                try {
                    // Récupérer le département sélectionné
                    const departmentFilter = document.getElementById('department-filter');
                    const departmentId = departmentFilter ? departmentFilter.value : '';
                    
                    // Récupérer les congés
                    const response = await fetch('/api/leaves/all');
                    if (!response.ok) {
                        throw new Error('Erreur lors de la récupération des congés');
                    }
                    
                    const leaves = await response.json();
                    console.log('Congés récupérés:', leaves);
                    
                    // Filtrer par département si nécessaire
                    const filteredLeaves = departmentId 
                        ? leaves.filter(leave => leave.department_id === parseInt(departmentId))
                        : leaves;
                    
                    // Convertir les congés en événements du calendrier
                    const events = filteredLeaves.map(leave => ({
                        title: `${leave.employee_name || 'Employé'} - ${leave.type}`,
                        start: leave.start_date,
                        end: new Date(new Date(leave.end_date).getTime() + 86400000).toISOString(),
                        backgroundColor: getStatusColor(leave.status),
                        borderColor: getStatusColor(leave.status),
                        extendedProps: {
                            status: leave.status,
                            type: leave.type,
                            employeeName: leave.employee_name,
                            departmentName: leave.department_name || 'Département inconnu'
                        }
                    }));
                    
                    successCallback(events);
                } catch (error) {
                    console.error('Erreur lors du chargement des événements:', error);
                    failureCallback(error);
                    // Afficher un message d'erreur dans le calendrier
                    calendarEl.innerHTML = '<div class="alert alert-danger">Erreur lors du chargement des événements. Veuillez rafraîchir la page.</div>';
                }
            },
            eventDidMount: function(info) {
                // Ajouter des infobulles avec Tippy.js
                if (typeof tippy !== 'undefined') {
                    tippy(info.el, {
                        content: `
                            <strong>${info.event.extendedProps.employeeName}</strong><br>
                            Département: ${info.event.extendedProps.departmentName}<br>
                            Type: ${info.event.extendedProps.type}<br>
                            Statut: ${info.event.extendedProps.status}
                        `,
                        allowHTML: true,
                        theme: 'light'
                    });
                }
            }
        });

        // Sauvegarder l'instance du calendrier
        calendarEl.calendar = calendar;
        
        // Rendre le calendrier
        console.log('Rendu du calendrier...');
        calendar.render();
        console.log('Calendrier initialisé avec succès');
        
        // Ajouter l'écouteur d'événements pour le filtre de département
        const departmentFilter = document.getElementById('department-filter');
        if (departmentFilter) {
            departmentFilter.addEventListener('change', function() {
                calendar.refetchEvents();
            });
        }
    } catch (error) {
        console.error("Erreur lors de l'initialisation du calendrier:", error);
        calendarEl.innerHTML = `<div class="alert alert-danger">Erreur lors de l'initialisation du calendrier: ${error.message}</div>`;
    }
}

// Fonction utilitaire pour obtenir la couleur en fonction du statut
function getStatusColor(status) {
    switch (status) {
        case 'approuvé':
            return '#28a745';  // vert
        case 'refusé':
            return '#dc3545';  // rouge
        case 'en attente':
            return '#ffc107';  // jaune
        default:
            return '#6c757d';  // gris
    }
}

// ------------------------------------------------------
// Afficher un message d'erreur
// ------------------------------------------------------
function showError(message) {
    console.error('Erreur:', message);
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed top-0 end-0 m-3';
    errorDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.body.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 5000);
}

// ------------------------------------------------------
// Afficher un message de succès
// ------------------------------------------------------
function showSuccess(message) {
    console.log('Succès:', message);
    const successDiv = document.createElement('div');
    successDiv.className = 'alert alert-success alert-dismissible fade show position-fixed top-0 end-0 m-3';
    successDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.body.appendChild(successDiv);
    setTimeout(() => successDiv.remove(), 5000);
}

// Helper function to get a cookie by its name
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

async function chargerNotifications() {
    try {
        const email = getUserEmailFromCookie();
        if (!email) {
            console.error("Email utilisateur non trouvé");
            return;
        }

        const container = document.getElementById("notifications-liste");
        if (!container) {
            console.error("Conteneur de notifications non trouvé");
            return;
        }

        console.log("Chargement des notifications pour:", email);
        const response = await fetch(`/api/leaves/notifications?email=${encodeURIComponent(email)}`);
        
        if (!response.ok) {
            console.error(`Erreur API notifications: ${response.status}`);
            container.innerHTML = "<li class='list-group-item'>Erreur lors du chargement des notifications.</li>";
            return;
        }

        const notifications = await response.json();
        console.log(`${notifications.length} notifications récupérées:`, notifications);

        if (notifications.length === 0) {
            container.innerHTML = "<li class='list-group-item text-muted'>Aucune notification.</li>";
            return;
        }

        let html = '';
        notifications.forEach(notif => {
            const date = new Date(notif.created_at).toLocaleDateString('fr-FR');
            const statusClass = notif.status === 'approuvé' ? 'bg-success' : 'bg-danger';
            
            html += `
                <li class="list-group-item">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="badge ${statusClass} me-2">${notif.status}</span>
                        <small class="text-muted">${date}</small>
                    </div>
                    <p class="mb-1 mt-2">${notif.message}</p>
                    <small class="text-muted">Type: ${notif.type}</small>
                </li>
            `;
        });
        
        container.innerHTML = html;
    } catch (error) {
        console.error("Erreur lors du chargement des notifications:", error);
        const container = document.getElementById("notifications-liste");
        if (container) {
            container.innerHTML = "<li class='list-group-item text-danger'>Erreur lors du chargement des notifications.</li>";
        }
    }
}

// ------------------------------------------------------
// Récupérer et afficher les soldes des derniers employés
// ------------------------------------------------------
async function fetchAndDisplayRecentBalances() {
    const container = document.getElementById('recent-leave-balances');
    if (!container) return;

    try {
        // Récupérer toutes les demandes de congés
        const response = await fetch('/api/leaves/all');
        if (!response.ok) {
            throw new Error('Erreur lors de la récupération des congés');
        }

        const leaves = await response.json();
        
        // Obtenir les 3 derniers employés uniques ayant fait une demande
        const uniqueEmployees = [...new Map(
            leaves
                .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                .map(leave => [leave.employee_id, {
                    id: leave.employee_id,
                    name: leave.employee_name,
                    department: leave.department_name
                }])
        ).values()].slice(0, 3);

        // Récupérer le solde pour chaque employé
        const employeesWithBalance = await Promise.all(
            uniqueEmployees.map(async (employee) => {
                try {
                    const balanceResponse = await fetch(`/api/leaves/balance/${employee.id}`);
                    if (balanceResponse.ok) {
                        const balanceData = await balanceResponse.json();
                        return {
                            ...employee,
                            balance: balanceData.balance
                        };
                    }
                    return {
                        ...employee,
                        balance: 'N/A'
                    };
                } catch (error) {
                    console.error(`Erreur pour l'employé ${employee.id}:`, error);
                    return {
                        ...employee,
                        balance: 'Erreur'
                    };
                }
            })
        );

        // Générer le HTML pour afficher les soldes
        const html = employeesWithBalance.map(employee => `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <strong>${employee.name || 'Employé inconnu'}</strong>
                    ${employee.department ? `<br><small class="text-muted">${employee.department}</small>` : ''}
                </div>
                <span class="badge ${getBadgeClass(employee.balance)} fs-6">
                    ${typeof employee.balance === 'number' ? employee.balance + ' jours' : employee.balance}
                </span>
            </div>
        `).join('');

        container.innerHTML = html || '<div class="text-center text-muted">Aucune donnée disponible</div>';

    } catch (error) {
        console.error("Erreur lors de la récupération des soldes récents:", error);
        container.innerHTML = '<div class="alert alert-danger">Erreur lors du chargement des données</div>';
    }
}

// Fonction utilitaire pour déterminer la classe du badge
function getBadgeClass(balance) {
    if (typeof balance !== 'number') return 'bg-secondary';
    if (balance <= 0) return 'bg-danger';
    if (balance < 5) return 'bg-warning';
    return 'bg-success';
}

// ------------------------------------------------------
// Initialiser la page lorsque le DOM est chargé
// ------------------------------------------------------
document.addEventListener('DOMContentLoaded', async function() {
    console.log('Initialisation de la page de demande de congés...');
    try {
        console.log('Initialisation des composants...');
        
        // Initialiser les sélecteurs de date
        initializeDatePickers();
        
        // Charger les informations de l'employé
        await loadEmployeeInfo();
        
        // Charger les demandes en cours uniquement si la section existe dans le DOM
        if (document.querySelector('#current-requests-table')) {
            await loadCurrentRequests();
        } else {
            console.log("Section des demandes en cours non trouvée dans le DOM, chargement ignoré.");
        }
        
        // Initialiser le formulaire
        initializeForm();
        
        console.log('Initialisation terminée avec succès');
    } catch (error) {
        console.error("Erreur d'initialisation:", error);
        showError("Une erreur s'est produite lors du chargement de la page.");
    }
});

// ------------------------------------------------------
// Chargement des demandes en cours
// ------------------------------------------------------
async function loadCurrentRequests() {
    try {
        const email = getUserEmailFromCookie();
        if (!email) {
            console.error("Email non trouvé dans les cookies");
            return;
        }

        // Vérifier que la table existe avant de continuer
        const tbody = document.querySelector('#current-requests-table tbody');
        if (!tbody) {
            console.error("Élément #current-requests-table tbody non trouvé dans le DOM");
            return;
        }

        // Utiliser l'endpoint /api/leaves/all qui fonctionne
        const response = await fetch('/api/leaves/all');
        if (!response.ok) {
            throw new Error('Erreur lors du chargement des demandes');
        }
        
        const data = await response.json();
        console.log('Toutes les demandes reçues:', data);
        
        // Filtrer pour n'afficher que les demandes de l'employé connecté
        const userLeaves = data.filter(leave => leave.employee_email === email);
        console.log('Demandes filtrées pour l\'employé:', userLeaves);
        
        displayLeaves(userLeaves);
    } catch (error) {
        console.error('Erreur:', error);
        // Ne rien faire si tbody n'existe pas, sinon afficher l'erreur
        const tbody = document.querySelector('#current-requests-table tbody');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-danger">
                        Erreur: ${error.message}
                    </td>
                </tr>
            `;
        }
    }
}

// ------------------------------------------------------
// Charger les informations de l'employé
// ------------------------------------------------------
async function loadEmployeeInfo() {
    try {
        // Récupérer l'email de l'utilisateur connecté
        const email = getUserEmailFromCookie();
        if (!email) {
            console.error("Email non trouvé dans les cookies");
            hideEmployeeInfoSection();
            return;
        }

        // Récupérer les informations de l'employé avec le nouvel endpoint
        const response = await fetch(`/api/employees/by-email/${encodeURIComponent(email)}`);
        
        if (!response.ok) {
            console.error("Erreur lors de la récupération des informations de l'employé:", response.statusText);
            hideEmployeeInfoSection();
            return;
        }
        
        const employee = await response.json();
        console.log("Informations de l'employé:", employee);
        
        // Afficher les informations de l'employé
        document.getElementById('employee-name').textContent = employee.name || 'Non disponible';
        
        // Gestion explicite du département
        const departmentElement = document.getElementById('employee-department');
        const departmentRow = departmentElement.closest('p');
        
        if (employee.department) {
            departmentElement.textContent = employee.department;
            departmentRow.style.display = ''; // Assurer que c'est visible
        } else {
            // Trois options ici:
            // 1. Masquer complètement la ligne (comme actuellement)
            departmentRow.style.display = 'none';
            
            // 2. Afficher "Non assigné" au lieu de masquer
            // departmentElement.textContent = "Non assigné";
            
            // 3. Afficher "Non disponible" (autre option)
            // departmentElement.textContent = "Non disponible";
        }
        
        // Récupérer et afficher le solde de congés
        await fetchAndDisplayLeaveBalance(employee.id);
        
    } catch (error) {
        console.error("Erreur lors du chargement des informations de l'employé:", error);
        hideEmployeeInfoSection();
    }
}

// ------------------------------------------------------
// Masquer la section d'information de l'employé si les données ne sont pas disponibles
// ------------------------------------------------------
function hideEmployeeInfoSection() {
    const infoSection = document.querySelector('.card.shadow-sm.mb-4');
    if (infoSection) {
        infoSection.style.display = 'none';
    }
}

// ------------------------------------------------------
// Initialiser les sélecteurs de dates avec flatpickr
// ------------------------------------------------------
function initializeDatePickers() {
    // Configuration de base pour les dates
    const dateConfig = {
        dateFormat: 'd/m/Y',
        locale: 'fr',
        minDate: 'today',
        disableMobile: true
    };
    
    // Initialiser les sélecteurs de dates
    const startDatePicker = flatpickr('#start-date', dateConfig);
    const endDatePicker = flatpickr('#end-date', dateConfig);
    
    // Mettre à jour la date de fin lorsque la date de début change
    startDatePicker.config.onChange = function(selectedDates) {
        endDatePicker.set('minDate', selectedDates[0]);
    };
}

// ------------------------------------------------------
// Initialiser le formulaire
// ------------------------------------------------------
function initializeForm() {
    const form = document.getElementById('leave-request-form');
    if (!form) return;
    
    // Gestionnaire pour la soumission du formulaire
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        submitLeaveRequest();
    });
    
    // Gestionnaire pour le bouton de vérification de disponibilité
    const checkButton = document.getElementById('check-availability-btn');
    if (checkButton) {
        checkButton.addEventListener('click', checkAvailability);
    }
}

// ------------------------------------------------------
// Soumettre la demande de congé
// ------------------------------------------------------
async function submitLeaveRequest() {
    try {
        // Récupérer les valeurs du formulaire
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;
        const leaveType = document.getElementById('leave-type').value;
        const comment = document.getElementById('comment').value;
        
        // Valider le formulaire
        if (!startDate || !endDate || !leaveType) {
            showError("Veuillez remplir tous les champs obligatoires.");
            return;
        }
        
        // Récupérer l'email de l'utilisateur
        const email = getUserEmailFromCookie();
        if (!email) {
            showError("Impossible de récupérer votre identifiant. Veuillez vous reconnecter.");
            return;
        }
        
        // Préparer les données pour l'API
        const leaveData = {
            email: email,
            start_date: formatDateForApi(startDate),
            end_date: formatDateForApi(endDate),
            leave_type: leaveType,
            comment: comment
        };
        
        // Envoyer la demande
        const response = await fetch('/api/leaves/request', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(leaveData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Erreur lors de la soumission de la demande.");
        }
        
        // Traiter la réponse
        const result = await response.json();
        
        // Afficher un message de succès
        showSuccess("Votre demande de congé a été envoyée avec succès!");
        
        // Réinitialiser le formulaire
        document.getElementById('leave-request-form').reset();
        
        // Mettre à jour le solde de congés si nécessaire
        await loadEmployeeInfo();
        
    } catch (error) {
        console.error("Erreur lors de la soumission de la demande:", error);
        showError(error.message);
    }
}

// ------------------------------------------------------
// Vérifier la disponibilité pour les dates sélectionnées
// ------------------------------------------------------
async function checkAvailability() {
    try {
        // Récupérer les valeurs du formulaire
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;
        
        // Valider les dates
        if (!startDate || !endDate) {
            showError("Veuillez sélectionner les dates de début et de fin.");
            return;
        }
        
        // Récupérer l'email de l'utilisateur
        const email = getUserEmailFromCookie();
        if (!email) {
            showError("Impossible de récupérer votre identifiant. Veuillez vous reconnecter.");
            return;
        }
        
        // Préparer les données pour l'API
        const checkData = {
            email: email,
            start_date: formatDateForApi(startDate),
            end_date: formatDateForApi(endDate)
        };
        
        // Envoyer la demande de vérification
        const response = await fetch('/api/leaves/check-availability', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(checkData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Erreur lors de la vérification de disponibilité.");
        }
        
        // Traiter la réponse
        const result = await response.json();
        
        // Afficher le résultat
        if (result.available) {
            showSuccess("Ces dates sont disponibles! Vous pouvez soumettre votre demande.");
        } else {
            showError("Ces dates ne sont pas disponibles: " + result.reason);
        }
        
    } catch (error) {
        console.error("Erreur lors de la vérification de disponibilité:", error);
        showError(error.message);
    }
}

// ------------------------------------------------------
// Formater une date pour l'API (format ISO)
// ------------------------------------------------------
function formatDateForApi(dateStr) {
    // Convertir de 'DD/MM/YYYY' à 'YYYY-MM-DD'
    const parts = dateStr.split('/');
    if (parts.length === 3) {
        return `${parts[2]}-${parts[1]}-${parts[0]}`;
    }
    return dateStr;
}

// Affichage des demandes dans le tableau
function displayLeaves(leaves) {
    const tbody = document.querySelector('#current-requests-table tbody');
    
    // Vérifier si tbody existe avant de continuer
    if (!tbody) {
        console.log("Élément tbody non trouvé. La section des demandes en cours pourrait être absente du DOM.");
        return; // Sortir de la fonction si tbody n'existe pas
    }
    
    tbody.innerHTML = '';

    if (leaves.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Aucune demande en cours</td></tr>';
        return;
    }

    leaves.forEach(leave => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${formatDateRange(leave.start_date, leave.end_date)}</td>
            <td>${leave.type}</td>
            <td><span class="badge bg-${getStatusColor(leave.status)}">${leave.status}</span></td>
            <td>${leave.comment || '-'}</td>
            <td>
                ${leave.status === 'En attente' ? `
                    <button class="btn btn-sm btn-danger" onclick="cancelRequest('${leave.id}')">
                        <i class="bi bi-x-circle"></i> Annuler
                    </button>
                ` : '-'}
            </td>
        `;
        tbody.appendChild(tr);
    });
}
