document.addEventListener("DOMContentLoaded", () => {
    const tableRows = document.querySelectorAll("tbody tr");
    tableRows.forEach((row) => {
        row.addEventListener("click", () => {
            const id = row.dataset.id;
            const entity = row.dataset.entity;
            if (id && entity) {
                window.location.href = `/seccion/${entity}?edit=${id}`;
            }
        });
    });
});

function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

async function reloadPage() {
    window.location.reload();
}