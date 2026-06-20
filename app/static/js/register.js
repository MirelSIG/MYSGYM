document.getElementById("register-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const data = Object.fromEntries(new FormData(e.target));

    const res = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    const json = await res.json();

    if (res.ok) {
        alert("Cuenta creada con éxito");
        window.location.href = "/login";
    } else {
        alert(json.message || "Error al registrar");
    }
});
