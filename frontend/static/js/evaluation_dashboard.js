// Fonction pour récupérer la liste des employés
function fetchEmployees() {
    fetch('/api/employees')
    .then(response => {
        if (!response.ok) {
            throw new Error("Erreur lors de la récupération des employés");
        }
        return response.json();
    })
    .then(data => {
        const employeeTable = document.getElementById("employee-table");
        if (!employeeTable) {
            console.log("L'élément employee-table n'existe pas sur cette page");
            return;
        }
        
        employeeTable.innerHTML = "";  // Vider la table avant d'ajouter les données
        
        data.forEach(employee => {
            const row = document.createElement("tr");
            
            // Créer les cellules avec les informations de l'employé
            row.innerHTML = `
                <td>${employee.id}</td>
                <td>${employee.name}</td>
                <td>${employee.email}</td>
                <td>
                    <button class="btn btn-sm btn-primary evaluate-btn" data-employee-id="${employee.id}">
                        Évaluer
                    </button>
                </td>
                <td>
                    <button class="btn btn-sm btn-info objectives-btn" data-employee-id="${employee.id}">
                        Voir objectifs
                    </button>
                </td>
                <td>
                    <button class="btn btn-sm btn-success report-btn" data-employee-id="${employee.id}">
                        Générer Rapport
                    </button>
                </td>
            `;
            
            employeeTable.appendChild(row);
        });
        
        // Ajouter les écouteurs d'événements pour les boutons
        document.querySelectorAll('.evaluate-btn').forEach(button => {
            button.addEventListener('click', function() {
                const employeeId = this.getAttribute('data-employee-id');
                // Afficher le modal d'évaluation
                document.getElementById('employee-id').value = employeeId;
                const evaluationModal = new bootstrap.Modal(document.getElementById('evaluationModal'));
                evaluationModal.show();
            });
        });
        
        document.querySelectorAll('.objectives-btn').forEach(button => {
            button.addEventListener('click', function() {
                const employeeId = this.getAttribute('data-employee-id');
                // Charger et afficher les objectifs
                fetchEmployeeObjectives(employeeId);
                const objectivesModal = new bootstrap.Modal(document.getElementById('objectivesModal'));
                objectivesModal.show();
            });
        });
        
        document.querySelectorAll('.report-btn').forEach(button => {
            button.addEventListener('click', function() {
                const employeeId = this.getAttribute('data-employee-id');
                generateEmployeeReport(employeeId);
            });
        });
    })
    .catch(error => {
        console.error("Erreur:", error);
        const employeeTable = document.getElementById("employee-table");
        if (employeeTable) {
            employeeTable.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Erreur lors du chargement des employés: ${error.message}</td></tr>`;
        }
    });
}

// Fonction pour ouvrir le modal d'évaluation
function openEvaluationForm(employeeId, employeeName) {
    document.getElementById('employee-id').value = employeeId;
    document.getElementById('evaluationModal').querySelector('.modal-title').textContent = `Évaluer ${employeeName}`;
    document.getElementById('evaluation-form').reset();
    // Ouvrir le modal
    new bootstrap.Modal(document.getElementById('evaluationModal')).show();
}

// Fonction pour ouvrir le modal des objectifs
function openObjectivesModal(employeeId, employeeName) {
    document.getElementById('employee-objectives-list').innerHTML = '';  // Vider la liste avant d'ajouter de nouveaux éléments
    document.getElementById('objectivesModal').querySelector('.modal-title').textContent = `Objectifs de ${employeeName}`;
    
    // Appeler la fonction pour récupérer les objectifs de l'employé
    fetchEmployeeObjectives(employeeId);
    
    // Ouvrir le modal
    new bootstrap.Modal(document.getElementById('objectivesModal')).show();
}

// Fonction pour récupérer les objectifs d'un employé
function fetchEmployeeObjectives(employeeId) {
    if (!employeeId) {
        console.error('L\'ID de l\'employé est manquant.');
        alert('L\'ID de l\'employé est manquant.');
        return;
    }

    fetch(`/api/objectives/${employeeId}`)  // Utilisez la route correcte
    .then(response => {
        if (!response.ok) {
            throw new Error("Erreur lors de la récupération des objectifs.");
        }
        return response.json();
    })
    .then(data => {
        let list = document.getElementById("employee-objectives-list");
        if (!list) {
            console.log("L'élément employee-objectives-list n'existe pas sur cette page");
            return;
        }
        list.innerHTML = "";  // Vider la liste avant d'ajouter les nouvelles données
        
        data.forEach(objective => {
            let item = document.createElement("li");
            item.classList.add("list-group-item");
            
            // Create a container for each objective
            let objectiveContainer = document.createElement("div");
            objectiveContainer.classList.add("objective-container");
            
            // Create and append the Objective ID
            let idElement = document.createElement("p");
            idElement.classList.add("objective-id");
            idElement.textContent = `Objectif ID: ${objective.id}`;
            objectiveContainer.appendChild(idElement);
            
            // Create and append the Description
            let descriptionElement = document.createElement("p");
            descriptionElement.classList.add("objective-description");
            descriptionElement.textContent = `Description: ${objective.description}`;
            objectiveContainer.appendChild(descriptionElement);
            
            // Create and append the Start Date
            let startDateElement = document.createElement("p");
            startDateElement.classList.add("objective-start-date");
            startDateElement.textContent = `Date de début: ${objective.start_date}`;
            objectiveContainer.appendChild(startDateElement);
            
            // Create and append the End Date
            let endDateElement = document.createElement("p");
            endDateElement.classList.add("objective-end-date");
            endDateElement.textContent = `Date de fin: ${objective.end_date}`;
            objectiveContainer.appendChild(endDateElement);
        
            // Append the objectiveContainer to the list item
            item.appendChild(objectiveContainer);
        
            // Append the list item to the list
            list.appendChild(item);
        });
        
    })
    .catch(error => {
        console.error("Erreur:", error);
        alert("Une erreur est survenue lors de la récupération des objectifs.");
    });
}

// Fonction pour soumettre un objectif
const objectivesForm = document.getElementById('objectives-form');
if (objectivesForm) {
    objectivesForm.addEventListener('submit', function(event) {
        event.preventDefault();  // Empêcher l'envoi du formulaire par défaut

        const formData = new FormData(this);
        const data = {
            employee_id: formData.get('employee-id'),
            description: formData.get('description'),
            start_date: formData.get('start-date'),
            end_date: formData.get('end-date')
        };

        fetch('/api/objectives', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Erreur lors de l'ajout de l'objectif.");
            }
            return response.json();
        })
        .then(result => {
            alert("Objectif ajouté avec succès!");
            fetchEmployeeObjectives(data.employee_id); // Recharger les objectifs
        })
        .catch(error => {
            console.error("Erreur:", error);
            alert("Une erreur est survenue lors de l'ajout de l'objectif.");
        });
    });
}

// Charger la liste des employés au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log("Page chargée, chargement des employés...");
    fetchEmployees();
    
    // Ajout du gestionnaire d'événement pour le formulaire d'évaluation
    const evaluationForm = document.getElementById('evaluation-form');
    if (evaluationForm) {
        evaluationForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const employeeId = document.getElementById('employee-id').value;
            const score = document.getElementById('score').value;
            const feedback = document.getElementById('feedback').value;
            
            // Validation des données
            if (!employeeId || !score || !feedback) {
                alert("Veuillez remplir tous les champs obligatoires.");
                return;
            }
            
            const data = {
                employee_id: parseInt(employeeId),
                score: parseInt(score),
                feedback: feedback,
                date: new Date().toISOString().split('T')[0]
            };
            
            // Envoi de l'évaluation au serveur
            fetch('/api/evaluations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Erreur lors de l'enregistrement de l'évaluation");
                }
                return response.json();
            })
            .then(result => {
                // Fermer le modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('evaluationModal'));
                modal.hide();
                
                // Montrer un message de succès
                alert("Évaluation enregistrée avec succès!");
                
                // Rafraîchir la liste des employés
                fetchEmployees();
            })
            .catch(error => {
                console.error("Erreur:", error);
                alert("Une erreur est survenue lors de l'enregistrement de l'évaluation: " + error.message);
            });
        });
    }
});

// Fonction pour récupérer les évaluations d'un employé
function fetchEmployeeEvaluations(employeeId) {
    fetch(`/api/evaluations/${employeeId}`)
    .then(response => response.json())
    .then(data => {
        const evaluationsList = document.getElementById("employee-evaluations");
        if (!evaluationsList) {
            console.log("L'élément employee-evaluations n'existe pas sur cette page");
            return;
        }
        
        evaluationsList.innerHTML = "";

        data.forEach(evaluation => {
            const item = document.createElement("li");
            item.classList.add("list-group-item");
            item.textContent = `Score: ${evaluation.score}, Commentaire: ${evaluation.feedback}, Date: ${evaluation.date}`;
            evaluationsList.appendChild(item);
        });
    })
    .catch(error => {
        console.error("Erreur lors de la récupération des évaluations:", error);
        const evaluationsList = document.getElementById("employee-evaluations");
        if (evaluationsList) {
            evaluationsList.innerHTML = `<li class="list-group-item text-danger">Erreur: ${error.message}</li>`;
        }
    });
}

// Fonction pour générer le rapport d'un employé
function generateEmployeeReport(employeeId) {
    if (!employeeId) {
        console.error('L\'ID de l\'employé est manquant.');
        alert('L\'ID de l\'employé est manquant.');
        return;
    }
    
    // Rediriger vers l'URL de génération de rapport pour télécharger directement le PDF
    window.open(`/api/reports/${employeeId}`, '_blank');
}
