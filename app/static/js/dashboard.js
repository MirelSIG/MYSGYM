document.addEventListener('DOMContentLoaded', () => {
    const tbody = document.getElementById('socios-table-body');
    const clientPanel = document.getElementById('client-panel');
    const clientTbody = document.getElementById('client-table-body');
    const modal = document.getElementById('modal');
    const modalForm = document.getElementById('modal-form');
    const modalTitle = document.getElementById('modal-title');
    const btnNew = document.getElementById('btn-new');
    const btnLogout = document.getElementById('btn-logout');

    if (btnLogout) btnLogout.addEventListener('click', () => ApiService.logout());

    if (btnNew) btnNew.addEventListener('click', () => openModal());

    document.getElementById('modal-cancel').addEventListener('click', closeModal);

    modalForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const form = e.target;
        const id = form.id_usuario.value;
        const payload = {
            nombre: form.nombre.value.trim(),
            email: form.email.value.trim(),
            password: form.password.value,
            telefono: form.telefono.value.trim(),
            fecha_registro: form.fecha_registro.value,
            estado: form.estado.value.trim(),
        };

        try {
            if (id) {
                await ApiService.update('usuarios', id, payload);
            } else {
                await ApiService.create('usuarios', payload);
            }
            closeModal();
            await load();
        } catch (err) {
            alert(err.message || 'Error');
        }
    });

    async function load() {
        // Decide qué panel mostrar según el role
        if (ApiService.isClient()) {
            if (clientPanel) clientPanel.style.display = '';
            if (tbody) tbody.closest('section').style.display = 'none';
            // ocultar botón nuevo para clientes
            if (btnNew) btnNew.style.display = 'none';
            clientTbody.innerHTML = '<tr><td colspan="4">Cargando...</td></tr>';
            try {
                const profile = await ApiService.request('/usuarios/perfil');
                renderClient(profile ? [profile] : []);
            } catch (err) {
                clientTbody.innerHTML = `<tr><td colspan="4">${err.message}</td></tr>`;
            }
            return;
        }

        if (!ApiService.isStaff()) {
            if (btnNew) btnNew.style.display = 'none';
            tbody.innerHTML = '<tr><td colspan="7">Tu cuenta no tiene permisos para administrar socios.</td></tr>';
            return;
        }

        // default: admin panel (incluye admin y empleado)
        if (clientPanel) clientPanel.style.display = 'none';
        if (tbody) tbody.closest('section').style.display = '';
        if (btnNew) btnNew.style.display = '';
        tbody.innerHTML = '<tr><td colspan="7">Cargando...</td></tr>';
        try {
            const items = await ApiService.get('usuarios');
            render(items);
        } catch (err) {
            tbody.innerHTML = `<tr><td colspan="7">${err.message}</td></tr>`;
        }
    }

    function renderClient(items) {
        if (!items || items.length === 0) {
            clientTbody.innerHTML = '<tr><td colspan="4">No hay registros</td></tr>';
            return;
        }
        clientTbody.innerHTML = '';
        items.forEach((it) => {
            // mostrar solo información básica para clientes
            const tr = document.createElement('tr');
            appendCell(tr, it.id_usuario);
            appendCell(tr, it.nombre);
            appendCell(tr, it.email);
            appendCell(tr, it.telefono);
            clientTbody.appendChild(tr);
        });
    }

    function render(items) {
        if (!items || items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7">No hay registros</td></tr>';
            return;
        }
        tbody.innerHTML = '';
        items.forEach((it) => {
            const tr = document.createElement('tr');
            appendCell(tr, it.id_usuario);
            appendCell(tr, it.nombre);
            appendCell(tr, it.email);
            appendCell(tr, it.telefono);
            appendCell(tr, it.fecha_registro);
            appendCell(tr, it.estado);

            const actions = document.createElement('td');
            const editButton = document.createElement('button');
            editButton.className = 'btn-link btn-edit';
            editButton.dataset.id = it.id_usuario;
            editButton.textContent = 'Editar';
            const deleteButton = document.createElement('button');
            deleteButton.className = 'btn-link btn-delete';
            deleteButton.dataset.id = it.id_usuario;
            deleteButton.textContent = 'Borrar';
            actions.append(editButton, deleteButton);
            tr.appendChild(actions);
            tbody.appendChild(tr);
        });

        document.querySelectorAll('.btn-edit').forEach((btn) => {
            btn.addEventListener('click', async (e) => {
                const id = e.target.dataset.id;
                try {
                    const record = await ApiService.getById('usuarios', id);
                    openModal(record);
                } catch (err) {
                    alert(err.message || 'Error al cargar registro');
                }
            });
        });

        document.querySelectorAll('.btn-delete').forEach((btn) => {
            btn.addEventListener('click', async (e) => {
                const id = e.target.dataset.id;
                if (!confirm('¿Borrar registro?')) return;
                try {
                    await ApiService.delete('usuarios', id);
                    await load();
                } catch (err) {
                    alert(err.message || 'Error al borrar');
                }
            });
        });
    }

    function openModal(record = null) {
        modalForm.reset();
        modalForm.id_usuario.value = record ? record.id_usuario : '';
        modalForm.nombre.value = record ? record.nombre : '';
        modalForm.email.value = record ? record.email : '';
        modalForm.password.value = '';
        modalForm.telefono.value = record ? record.telefono : '';
        modalForm.fecha_registro.value = record ? record.fecha_registro : '';
        modalForm.estado.value = record ? record.estado : '';
        modalTitle.textContent = record ? `Editar: ${record.nombre}` : 'Nuevo socio';
        modal.style.display = 'flex';
    }

    function closeModal() {
        modal.style.display = 'none';
    }

    function appendCell(row, value) {
        const cell = document.createElement('td');
        cell.textContent = value ?? '';
        row.appendChild(cell);
    }

    // inicializar
    load();
});
