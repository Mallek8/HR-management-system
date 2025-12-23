//Fonction pour récupérer un cookie par son nom
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

//Code principal au chargement de la page
document.addEventListener("DOMContentLoaded", async () => {
    const trainingSelect = document.getElementById("training_id");
    const form = document.getElementById("trainingRequestForm");
    const successMsg = document.getElementById("requestSuccess");
    const errorMsg = document.getElementById("requestError");

    let employeeId = null;

    //Récupérer l'email depuis le cookie
    const userEmail = getCookie("user_email")?.replace(/^"|"$/g, ""); // retirer les guillemets

    if (userEmail) {
        try {
            const res = await fetch(`/request-leave/by-email?email=${encodeURIComponent(userEmail)}`);
            if (!res.ok) throw new Error("Employé non trouvé");
            const data = await res.json();
            employeeId = data.id;
            console.log("Employé trouvé :", employeeId);
            await loadSuggestions(userEmail); // Charger les suggestions de formation
        } catch (err) {
            console.error("Erreur lors de la récupération de l'employé :", err);
        }
    } else {
        console.warn("Aucun email trouvé dans les cookies");
    }

    //Charger la liste des formations
    try {
        const response = await fetch("/api/trainings");
        const trainings = await response.json();

        trainings.forEach(training => {
            const option = document.createElement("option");
            option.value = training.id;
            option.textContent = `${training.title} - ${training.domain} (${training.level})`;
            trainingSelect.appendChild(option);
        });
    } catch (err) {
        console.error("Erreur lors du chargement des formations :", err);
    }

    //Soumission de la demande de formation
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        if (!employeeId) {
            errorMsg.textContent = "Erreur : employé non identifié.";
            errorMsg.classList.remove("d-none");
            return;
        }

        const formData = {
            training_id: parseInt(trainingSelect.value),
            employee_id: employeeId
        };

        try {
            const res = await fetch("/api/training-requests/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            });

            if (res.ok) {
                successMsg.classList.remove("d-none");
                errorMsg.classList.add("d-none");
                form.reset();
                await loadTrainingPlan(employeeId); // Rafraîchir le plan après soumission
            } else {
                const data = await res.json();
                errorMsg.textContent = data.detail || "Une erreur est survenue.";
                errorMsg.classList.remove("d-none");
                successMsg.classList.add("d-none");
            }
        } catch (err) {
            console.error("Erreur réseau", err);
            errorMsg.classList.remove("d-none");
            successMsg.classList.add("d-none");
        }
    });

    //Charger le plan à l'initialisation si employé identifié
    if (employeeId) {
        await loadTrainingPlan(employeeId);
    }
});

//Fonction pour charger et afficher le plan de formation
async function loadTrainingPlan(employeeId) {
    try {
        const resPlan = await fetch(`/api/training-requests/employee/${employeeId}/training-plan`);

        if (!resPlan.ok) throw new Error("Erreur lors du chargement du plan");

        const plans = await resPlan.json();
        const section = document.createElement("section");
        section.className = "mt-5";
        section.id = "trainingPlanSection";

        if (plans.length === 0) {
            section.innerHTML = `<div class="alert alert-info">Aucun plan de formation généré pour le moment.</div>`;
        } else {
            section.innerHTML = `<h4 class="mb-3">Plan de formation</h4>`;
            const list = document.createElement("ul");
            list.className = "list-group";

            plans.forEach(plan => {
                const item = document.createElement("li");
                item.className = "list-group-item";
                item.innerHTML = `
                    <strong>${plan.title}</strong> (${plan.domain})<br>
                    Du <strong>${plan.start_date}</strong> au <strong>${plan.end_date}</strong>
                `;
                list.appendChild(item);
            });

            section.appendChild(list);
        }

        const oldSection = document.getElementById("trainingPlanSection");
        if (oldSection) oldSection.remove();

        const target = document.getElementById("trainingRequestForm");
        target.insertAdjacentElement("afterend", section);
    } catch (err) {
        console.error("Erreur lors du chargement du plan de formation :", err);
    }
}
async function loadSuggestions(email) {
    try {
        const res = await fetch(`/api/training-requests/suggestions?email=${encodeURIComponent(email)}`);
        if (!res.ok) throw new Error("Erreur lors de la récupération des suggestions.");

        const trainings = await res.json();
        if (trainings.length === 0) return;

        const suggestionsSection = document.createElement("section");
        suggestionsSection.className = "mt-4";
        suggestionsSection.innerHTML = `<h4 class="mb-3">📌 Suggestions de formation pour vous</h4>`;

        const list = document.createElement("ul");
        list.className = "list-group";

        trainings.forEach(training => {
            const item = document.createElement("li");
            item.className = "list-group-item";
            item.innerHTML = `
                <strong>${training.title}</strong> – ${training.domain} (${training.level})<br>
                <small>📅 Du ${training.start_date} au ${training.end_date}</small>
            `;
            list.appendChild(item);
        });

        suggestionsSection.appendChild(list);

        // On insère les suggestions au-dessus du formulaire
        const form = document.getElementById("trainingRequestForm");
        form.insertAdjacentElement("beforebegin", suggestionsSection);
    } catch (err) {
        console.error("Erreur suggestions :", err);
    }
}
