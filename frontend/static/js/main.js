// Fonction pour récupérer l'email de l'utilisateur connecté depuis les cookies
/**
 * Fonction pour récupérer l'email de l'utilisateur connecté depuis les cookies.
 * Cela permet d'identifier l'utilisateur pour effectuer des actions basées sur son email.
 * @returns {string} L'email de l'utilisateur
 */
function getEmailUtilisateur() {
    const email = document.cookie
        .replace(/(?:(?:^|.*;\s*)user_email\s*=\s*([^;]*).*$)|^.*$/, "$1")
        .replace(/(^"|"$)/g, '');  // Supprime les guillemets éventuels
    
    console.log("Email récupéré depuis le cookie :", email);
    return email;
}

// Fonction pour récupérer l'employé par email
/**
 * Fonction asynchrone pour récupérer un employé par son email.
 * Si l'email est celui de l'administrateur, on le reconnaît directement.
 * @param {string} email L'email de l'employé à rechercher
 */
async function getEmployeeByEmail(email) {
    if (email === "admin" || email === "admin@example.com") {
        console.log("Admin reconnu, pas besoin de vérifier dans la base.");
        return; // Admin is already recognized
    }

    try {
        if (!email) {
            console.error("Email non valide.");
            return;
        }

        const response = await fetch(`/api/employees/by-email?email=${encodeURIComponent(email.trim())}`);
        if (!response.ok) {
            throw new Error(`Erreur récupération de l'employé: ${response.status}`);
        }

        const employee = await response.json();
        if (!employee) {
            console.warn("Aucun employé trouvé pour cet email.");
            return;
        }
        console.log(employee);
    } catch (error) {
        console.error("Erreur lors de la récupération de l'employé :", error);
    }
}

// ==========================
// Affichage des employés
// ==========================
/**
 * Fonction asynchrone pour afficher tous les employés dans un tableau HTML.
 * Cette fonction récupère les employés via une API et les affiche dans une table.
 */
async function fetchEmployees() {
    const table = document.getElementById("employee-table");
    const loadingMessage = document.getElementById("loadingMessage");

    if (loadingMessage) loadingMessage.style.display = "block";
    if (!table) {
        console.error("Table element not found.");
        return;
    }

    let tbody = table.querySelector("tbody");
    if (tbody) {
        tbody.innerHTML = "";  // Clear existing rows if tbody exists
    } else {
        console.warn("Tbody element not found. Creating a new one.");
        tbody = document.createElement("tbody");
        table.appendChild(tbody);  // Create tbody if not found
    }

    try {
        const response = await fetch("/api/employees/");
        if (!response.ok) {
            throw new Error(`Erreur ${response.status}: Impossible de récupérer les employés.`);
        }

        const employees = await response.json();
        if (!Array.isArray(employees)) throw new Error("Données invalides");

        // Si l'en-tête du tableau n'existe pas, le créer
        if (!table.querySelector("thead")) {
            const thead = document.createElement("thead");
            thead.className = "bg-primary text-white";
            thead.innerHTML = `
                <tr>
                    <th class="text-center">ID</th>
                    <th class="text-center">Nom</th>
                    <th class="text-center">Email</th>
                    <th class="text-center">Rôle</th>
                    <th class="text-center">Département</th>
                    <th class="text-center">Date d'Embauche</th>
                    <th class="text-center">Statut</th>
                    <th class="text-center">Actions</th>
                </tr>
            `;
            table.appendChild(thead);
        }

        employees.forEach(emp => {
            const formattedBirthDate = emp.birth_date ? new Date(emp.birth_date).toLocaleDateString() : "";
            const formattedHireDate = emp.hire_date ? new Date(emp.hire_date).toLocaleDateString() : "";
            const statusClass = emp.status ? "badge bg-success" : "badge bg-danger";

            // Create a new row for each employee
            const row = document.createElement("tr");
            row.className = "employee-row";

            // Add employee details to the row with optimized columns
            row.innerHTML = `
                <td class="text-center">${emp.id}</td>
                <td>${emp.name}</td>
                <td>${emp.email}</td>
                <td class="text-center">${emp.role}</td>
                <td class="text-center">${emp.department || ""}</td>
                <td class="text-center">${formattedHireDate}</td>
                <td class="text-center"><span class="${statusClass}">${emp.status ? "Actif" : "Inactif"}</span></td>
            `;

            // Create a cell for action buttons with better structure
            const actionsCell = document.createElement("td");
            actionsCell.className = "text-center";
            actionsCell.innerHTML = `
                <div class="d-flex justify-content-center gap-2">
                    <button class="btn btn-primary btn-sm edit-btn" data-id="${emp.id}">
                        <i class="fas fa-edit"></i> Modifier
                    </button>
                    <button class="btn btn-danger btn-sm delete-btn" data-id="${emp.id}">
                        <i class="fas fa-trash"></i> Supprimer
                    </button>
                </div>
            `;
            row.appendChild(actionsCell);
            tbody.appendChild(row);
        });

        // Add event listeners for edit buttons after rows are populated
        document.querySelectorAll(".edit-btn").forEach(button => {
            button.addEventListener("click", function() {
                const employeeId = this.getAttribute("data-id");
                editEmployee(employeeId);
            });
        });

        // Add event listeners for delete buttons
        document.querySelectorAll(".delete-btn").forEach(button => {
            button.addEventListener("click", function() {
                const employeeId = this.getAttribute("data-id");
                deleteEmployee(employeeId);
            });
        });
    } catch (error) {
        console.error("Erreur lors du chargement des employés :", error);
        if (loadingMessage) {
            loadingMessage.innerHTML = `<div class="alert alert-danger">Impossible de charger les employés.</div>`;
        }
    } finally {
        if (loadingMessage) loadingMessage.style.display = "none";
    }
}

// ==========================
// Handle Add Employee Button
// ==========================
document.addEventListener("DOMContentLoaded", function () {
    fetchEmployees();

    const addEmployeeBtn = document.getElementById("addEmployeeBtn");

    if (addEmployeeBtn) {
        addEmployeeBtn.addEventListener("click", function () {
            document.getElementById("employeeModal").style.display = "block";  // Show modal
        });
    }

    const employeeForm = document.getElementById("employeeForm");
    if (employeeForm) {
        employeeForm.addEventListener("submit", async function (e) {
            e.preventDefault();

            const formData = new FormData(this);
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });

            try {
                const response = await fetch("/api/employees/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    alert("Employé ajouté avec succès!");
                    location.reload();
                } else {
                    const error = await response.json();
                    alert("Erreur lors de l'ajout de l'employé: " + error.detail);
                }
            } catch (error) {
                console.error("Erreur de réseau :", error);
                alert("Une erreur réseau est survenue");
            }
        });
    }
});

// Function to delete an employee
async function deleteEmployee(employeeId) {
    console.log("Deleting employee with ID:", employeeId);

    const confirmDelete = confirm("Êtes-vous sûr de vouloir supprimer cet employé ?");
    if (!confirmDelete) return;

    try {
        const response = await fetch(`/api/employees/${employeeId}`, {
            method: "DELETE",
        });

        if (!response.ok) {
            const errorData = await response.json(); // Récupérer les données d'erreur
            throw new Error(`Erreur de suppression: ${errorData.detail}`);
        }

        // Afficher un message de succès et recharger les données
        showSuccessMessage("Employé supprimé avec succès.");
        fetchEmployees();
    } catch (error) {
        console.error("Erreur de suppression:", error);
        showErrorMessage(error.message);
    }
}

// Fonction pour mettre à jour un employé
async function editEmployee(employeeId) {
    console.log("Editing employee with ID:", employeeId);

    try {
        const response = await fetch(`/api/employees/${employeeId}`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            }
        });

        if (!response.ok) {
            throw new Error(`Erreur lors de la récupération des données: ${response.status}`);
        }

        const employee = await response.json();
        console.log("Employee data:", employee);

        // Remplir le formulaire avec les données de l'employé
        document.getElementById("editEmployeeId").value = employee.id;
        document.getElementById("editEmployeeName").value = employee.name;
        document.getElementById("editEmployeeEmail").value = employee.email;
        document.getElementById("editEmployeeRole").value = employee.role;
        
        // Les champs optionnels ne doivent pas être 'undefined'
        document.getElementById("editEmployeeBirthDate").value = employee.birth_date || "";
        document.getElementById("editEmployeeDepartment").value = employee.department || "";
        document.getElementById("editEmployeeSalary").value = employee.salary || "";
        document.getElementById("editEmployeeExperience").value = employee.experience || "";
        document.getElementById("editEmployeeSupervisor").value = employee.supervisor_id || "";
        document.getElementById("editEmployeeHireDate").value = employee.hire_date || "";

        // Ouvrir la modal Bootstrap
        const editModal = new bootstrap.Modal(document.getElementById('editEmployeeModal'));
        editModal.show();
    } catch (error) {
        console.error("Erreur lors de l'édition:", error);
        alert("Une erreur est survenue lors de la récupération des données de l'employé.");
    }
}

// Changeons le code de closeEditModal pour qu'il soit plus utile
function showSuccessMessage(message) {
    const alertMessage = document.createElement('div');
    alertMessage.className = 'alert alert-success alert-dismissible fade show';
    alertMessage.innerHTML = `
        <strong>Succès!</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('.card-header');
    if (container) {
        container.after(alertMessage);
        setTimeout(() => alertMessage.remove(), 3000);
    }
}

function showErrorMessage(message) {
    const alertMessage = document.createElement('div');
    alertMessage.className = 'alert alert-danger alert-dismissible fade show';
    alertMessage.innerHTML = `
        <strong>Erreur!</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('.card-header');
    if (container) {
        container.after(alertMessage);
        setTimeout(() => alertMessage.remove(), 5000);
    }
}

async function checkUserRole() {
    const userEmail = localStorage.getItem("userEmail");
    if (!userEmail) {
        window.location.href = "/login";
        return;
    }

    try {
        // Vérifier si c'est l'administrateur
        if (userEmail === "admin@example.com") {
            console.log("Admin reconnu, redirection vers le tableau de bord admin");
            window.location.href = "/dashboard_admin";
            return;
        }

        const response = await fetch(`/api/employee/profile/${userEmail}`);
        if (!response.ok) {
            throw new Error("Erreur lors de la récupération du profil");
        }
        const data = await response.json();
        
        // Vérifier le rôle dans la réponse
        if (data.role === "admin") {
            window.location.href = "/dashboard_admin";
            return;
        }

        // Si ce n'est pas un admin, continuer avec le flux normal
        const employeeId = data.id;
        if (!employeeId) {
            throw new Error("ID employé non trouvé dans la réponse");
        }
        
        localStorage.setItem("employeeId", employeeId);
        window.location.href = "/employee_evaluations";
    } catch (error) {
        console.error("Erreur:", error);
        alert("Une erreur est survenue lors de la vérification du rôle. Veuillez vous reconnecter.");
        window.location.href = "/login";
    }
}
