// Tableau de bord employé - HannaConnect
console.log('Chargement du tableau de bord employé');

// Variables globales
let dashboardData = null;
let leaveChart = null;

document.addEventListener('DOMContentLoaded', async function() {
    try {
        // Récupérer l'email de l'utilisateur
        const email = getUserEmailFromCookie();
        if (!email) {
            showErrorMessage("Session expirée. Veuillez vous reconnecter.");
            return;
        }

        // Charger toutes les données du tableau de bord en une seule requête
        await loadDashboardData(email);

    } catch (error) {
        console.error('Erreur d\'initialisation:', error);
        showErrorMessage("Une erreur est survenue lors du chargement du tableau de bord.");
    }
});

/**
 * Charge toutes les données du tableau de bord depuis l'API
 */
async function loadDashboardData(email) {
    try {
        // Afficher des indicateurs de chargement
        showLoadingIndicators();
        
        const response = await fetch(`/api/employee/dashboard/${encodeURIComponent(email)}`);
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        
        // Stocker les données dans la variable globale
        dashboardData = await response.json();
        console.log('Données du tableau de bord:', dashboardData);
        
        // Mettre à jour tous les éléments du tableau de bord
        updateEmployeeInfo();
        updateLeaveStats();
        updateTrainingStats();
        updateLeaveBalance();
        updateAttendanceRate();
        initializeLeaveEvolutionChart();
        updateRecentActivities();
        
    } catch (error) {
        console.error('Erreur lors du chargement des données du tableau de bord:', error);
        showErrorMessage("Impossible de récupérer les données du tableau de bord.");
    } finally {
        // Masquer les indicateurs de chargement
        hideLoadingIndicators();
    }
}

/**
 * Affiche les indicateurs de chargement
 */
function showLoadingIndicators() {
    // Remplacer les valeurs par des placeholders de chargement
    document.querySelectorAll('.kpi-value').forEach(el => {
        el.textContent = '--';
    });
    
    // Afficher l'icône de chargement des activités
    document.getElementById('activities-loading').classList.remove('d-none');
    document.getElementById('activities-container').classList.add('d-none');
}

/**
 * Masque les indicateurs de chargement
 */
function hideLoadingIndicators() {
    // Masquer l'icône de chargement des activités
    document.getElementById('activities-loading').classList.add('d-none');
}

/**
 * Met à jour les informations de l'employé
 */
function updateEmployeeInfo() {
    if (!dashboardData || !dashboardData.employee) return;
    
    const employeeData = dashboardData.employee;
    
    // Mettre à jour le titre de la page avec le nom de l'employé
    const pageTitleName = document.getElementById('page-title-name');
    if (pageTitleName) {
        pageTitleName.textContent = `Bienvenue ${employeeData.name}`;
    }
    
    // Informations personnelles
    document.getElementById('employee-name').textContent = employeeData.name || 'N/A';
    document.getElementById('employee-email').textContent = employeeData.email || 'N/A';
    document.getElementById('employee-department').textContent = employeeData.department || 'Non assigné';
    document.getElementById('employee-position').textContent = employeeData.position || 'Non assigné';
}

/**
 * Met à jour les statistiques de congés
 */
function updateLeaveStats() {
    if (!dashboardData || !dashboardData.leave_stats) return;
    
    const leaveStats = dashboardData.leave_stats;
    
    // Mise à jour des KPIs
    document.getElementById('leave-requests-total').textContent = leaveStats.total || 0;
    document.getElementById('leave-approved').textContent = `${leaveStats.approved || 0} Approuvées`;
    document.getElementById('leave-pending').textContent = `${leaveStats.pending || 0} En attente`;
    document.getElementById('leave-rejected').textContent = `${leaveStats.rejected || 0} Refusées`;
}

/**
 * Met à jour les statistiques de formations
 */
function updateTrainingStats() {
    if (!dashboardData || !dashboardData.training_stats) return;
    
    const trainingStats = dashboardData.training_stats;
    
    // Mise à jour des KPIs
    document.getElementById('training-requests-total').textContent = trainingStats.total || 0;
    document.getElementById('training-sent').textContent = `${trainingStats.sent || 0} Envoyées`;
    document.getElementById('training-approved').textContent = `${trainingStats.approved || 0} Validées`;
    document.getElementById('training-rejected').textContent = `${trainingStats.rejected || 0} Refusées`;
}

/**
 * Met à jour le solde de congé
 */
function updateLeaveBalance() {
    if (!dashboardData) return;
    
    // Mise à jour du KPI
    const balance = dashboardData.leave_balance && dashboardData.leave_balance.paid_leave_balance !== undefined 
        ? dashboardData.leave_balance.paid_leave_balance 
        : 0;
    document.getElementById('leave-balance').textContent = balance;
}

/**
 * Met à jour le taux de présence
 */
function updateAttendanceRate() {
    if (!dashboardData) return;
    
    // Mise à jour du KPI
    document.getElementById('attendance-rate').textContent = `${dashboardData.attendance_rate}%`;
}

/**
 * Initialise le graphique d'évolution des congés
 */
function initializeLeaveEvolutionChart() {
    if (!dashboardData) return;
    
    // Récupérer le contexte du canvas
    const ctx = document.getElementById('leave-evolution-chart').getContext('2d');
    
    // Vérifier si le graphique existe déjà
    const existingChart = Chart.getChart('leave-evolution-chart');
    if (existingChart) {
        existingChart.destroy();
    }
    
    // Créer un nouveau graphique
    leaveChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc'],
            datasets: [{
                label: 'Jours de congés pris',
                data: dashboardData.leave_evolution || [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                backgroundColor: 'rgba(74, 144, 226, 0.2)',
                borderColor: 'rgba(74, 144, 226, 1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

/**
 * Met à jour les activités récentes
 */
function updateRecentActivities() {
    if (!dashboardData || !dashboardData.recent_activities) return;
    
    const activities = dashboardData.recent_activities;
    
    // Afficher le conteneur d'activités
    const container = document.getElementById('activities-container');
    container.classList.remove('d-none');
    
    // S'il n'y a pas d'activités, afficher un message
    if (activities.length === 0) {
        container.innerHTML = '<p class="text-center text-muted">Aucune activité récente.</p>';
        return;
    }
    
    // Remplir le conteneur avec les activités
    let html = '';
    activities.forEach(activity => {
        html += `
            <div class="activity-item d-flex align-items-start mb-3">
                <div class="activity-icon bg-${activity.color || 'primary'} text-white">
                    <i class="bi bi-${activity.icon || 'info-circle'}"></i>
                </div>
                <div class="activity-content">
                    <div class="d-flex justify-content-between align-items-center">
                        <h6 class="mb-0 fw-semibold">${activity.title}</h6>
                        <span class="activity-time">${activity.time}</span>
                    </div>
                    <p class="mb-0 text-muted">${activity.message}</p>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

/**
 * Récupère l'email de l'utilisateur depuis les cookies
 */
function getUserEmailFromCookie() {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith('user_email=')) {
            const email = cookie.substring('user_email='.length);
            return email.replace(/^"(.*)"$/, '$1'); // Supprimer les guillemets si présents
        }
    }
    return null;
}

/**
 * Affiche un message d'erreur
 */
function showErrorMessage(message) {
    // Créer un élément d'alerte s'il n'existe pas déjà
    let alertContainer = document.getElementById('alert-container');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.id = 'alert-container';
        alertContainer.className = 'position-fixed top-0 start-50 translate-middle-x mt-4 z-index-1050';
        document.body.appendChild(alertContainer);
    }
    
    // Créer l'alerte
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Supprimer l'alerte après 5 secondes
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => alert.remove(), 500);
    }, 5000);
}


