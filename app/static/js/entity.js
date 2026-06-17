document.addEventListener('DOMContentLoaded', () => {
    const entity = window.MYSGYM_ENTITY;
    const config = window.MYSGYM_CONFIG;
    const idField = config.id_field;
    const fields = config.fields || [];
    const formFields = config.form_fields || fields;
    const isStaff = ApiService.isStaff();

    const tbody = document.getElementById('entity-table-body');
    const form = document.getElementById('entity-form');
    const formSection = document.getElementById('formulario');
    const resetButton = document.getElementById('form-reset');
    const newRecordLink = document.getElementById('new-record-link');
    const formTitle = document.getElementById('form-title');
    const formCopy = document.getElementById('form-copy');
    const submitButton = form.querySelector('button[type="submit"]');
    const countEls = [
        document.getElementById('entity-count'),
        document.getElementById('entity-footer-count'),
    ];
    const integerFields = new Set([
        'capacidad',
        'monitor_id',
        'sala_id',
        'horario_id',
        'aforo_maximo',
        'usuario_id',
        'actividad_id',
        'empleado_id',
        'material_id',
    ]);
    const decimalFields = new Set(['monto']);

    function setPasswordRequired(required) {
        if (form.elements.password) {
            form.elements.password.required = required;
        }
    }

    function normalizePayloadValue(field, value) {
        if (value === '') return '';
        if (integerFields.has(field)) return Number.parseInt(value, 10);
        if (decimalFields.has(field)) return Number.parseFloat(value);
        return value;
    }

    function normalizeList(response) {
        if (Array.isArray(response)) return response;
        if (response && Array.isArray(response.data)) return response.data;
        if (response && Array.isArray(response.results)) return response.results;
        return [];
    }

    function statusClass(value) {
        const normalized = String(value || '').trim().toLowerCase();
        const mapping = {
            activa: 'activo',
            activo: 'activo',
            confirmada: 'activo',
            operativo: 'activo',
            cobrado: 'cobrado',
            pendiente: 'pendiente',
            'en espera': 'pendiente',
            'en proceso': 'pendiente',
            revision: 'pendiente',
            abierta: 'inactivo',
            inactiva: 'inactivo',
            inactivo: 'inactivo',
        };
        return mapping[normalized] || 'pendiente';
    }

    async function load() {
        const colspan = fields.length + (isStaff ? 2 : 1);
        tbody.innerHTML = `<tr><td colspan="${colspan}">Cargando...</td></tr>`;
        try {
            const rows = normalizeList(await ApiService.get(entity));
            render(rows);
            setCount(rows.length);
        } catch (err) {
            tbody.innerHTML = `<tr><td colspan="${colspan}">${err.message || 'Error al cargar datos'}</td></tr>`;
            setCount(0);
        }
    }

    function render(rows) {
        const colspan = fields.length + (isStaff ? 2 : 1);
        if (!rows.length) {
            tbody.innerHTML = `<tr><td colspan="${colspan}">No hay registros</td></tr>`;
            return;
        }

        tbody.innerHTML = '';
        rows.forEach((row) => {
            const tr = document.createElement('tr');
            appendCell(tr, row[idField]);
            fields.forEach((field) => appendValueCell(tr, field, row[field]));

            if (!isStaff) {
                if (entity === 'actividades') {
                    const actions = document.createElement('td');
                    const bookBtn = document.createElement('button');
                    bookBtn.className = 'btn-link';
                    bookBtn.textContent = 'Apuntarse';
                    bookBtn.addEventListener('click', async () => {
                        try {
                            await ApiService.create('reservas', { actividad_id: row[idField] });
                            alert('Te has apuntado con éxito');
                        } catch (err) {
                            alert(err.message || 'Error al apuntarse');
                        }
                    });
                    actions.appendChild(bookBtn);
                    tr.appendChild(actions);
                } else if (entity === 'reservas') {
                    const actions = document.createElement('td');
                    const cancelBtn = document.createElement('button');
                    cancelBtn.className = 'btn-link danger';
                    cancelBtn.textContent = 'Cancelar';
                    cancelBtn.addEventListener('click', async () => {
                        if (!confirm('¿Seguro que quieres cancelar tu reserva?')) return;
                        try {
                            await ApiService.delete('reservas', row[idField]);
                            await load();
                            alert('Reserva cancelada');
                        } catch (err) {
                            alert(err.message || 'Error al cancelar');
                        }
                    });
                    actions.appendChild(cancelBtn);
                    tr.appendChild(actions);
                } else {
                    const emptyAction = document.createElement('td');
                    tr.appendChild(emptyAction);
                }
                tbody.appendChild(tr);
                return;
            }

            const actions = document.createElement('td');
            const group = document.createElement('div');
            group.className = 'action-group';

            const editButton = document.createElement('button');
            editButton.className = 'btn-link';
            editButton.type = 'button';
            editButton.textContent = 'Editar';
            editButton.dataset.editId = row[idField];
            editButton.addEventListener('click', () => editRecord(row));

            const deleteButton = document.createElement('button');
            deleteButton.className = 'btn-link danger';
            deleteButton.type = 'button';
            deleteButton.textContent = 'Borrar';
            deleteButton.addEventListener('click', () => deleteRecord(row[idField]));

            group.append(editButton, deleteButton);
            actions.appendChild(group);
            tr.appendChild(actions);
            tbody.appendChild(tr);
        });
    }

    function appendCell(row, value) {
        const cell = document.createElement('td');
        cell.textContent = value ?? '';
        row.appendChild(cell);
    }

    function appendValueCell(row, field, value) {
        const cell = document.createElement('td');
        if (['estado', 'metodo'].includes(field)) {
            const status = document.createElement('span');
            status.className = `status ${statusClass(value)}`;
            status.textContent = value ?? '';
            cell.appendChild(status);
        } else {
            cell.textContent = value ?? '';
        }
        row.appendChild(cell);
    }

    function setCount(count) {
        countEls.forEach((el) => {
            if (el) el.textContent = count;
        });
    }

    function editRecord(record) {
        if (!isStaff) return;
        try {
            fillForm(record);
            history.replaceState(null, '', `/seccion/${entity}?edit=${record[idField]}`);
            document.getElementById('formulario').scrollIntoView({ behavior: 'smooth' });
        } catch (err) {
            alert(err.message || 'Error al cargar registro');
        }
    }

    async function deleteRecord(id) {
        if (!isStaff) return;
        if (!confirm('¿Borrar registro?')) return;
        try {
            await ApiService.delete(entity, id);
            resetForm();
            await load();
        } catch (err) {
            alert(err.message || 'Error al borrar');
        }
    }

    function fillForm(record) {
        form.elements[idField].value = record[idField] ?? '';
        formFields.forEach((field) => {
            form.elements[field].value = record[field] ?? '';
        });
        formTitle.textContent = 'Modificar registro';
        formCopy.textContent = `Estas editando el registro ${record[idField]} de ${config.title.toLowerCase()}.`;
        submitButton.textContent = 'Guardar cambios';
        newRecordLink.textContent = 'Editando registro';
        setPasswordRequired(false);
    }

    function resetForm() {
        form.reset();
        form.elements[idField].value = '';
        formTitle.textContent = 'Nuevo registro';
        formCopy.textContent = `Formulario para insertar datos en la entidad ${config.title.toLowerCase()}.`;
        submitButton.textContent = 'Guardar registro';
        newRecordLink.textContent = '+ Nuevo registro';
        history.replaceState(null, '', `/seccion/${entity}`);
        setPasswordRequired(true);
    }

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        if (!isStaff) {
            alert('Tu cuenta no tiene permisos para modificar estos datos.');
            return;
        }
        const id = form.elements[idField].value;
        const payload = {};
        formFields.forEach((field) => {
            const value = form.elements[field].value.trim();
            if (!(id && field === 'password' && value === '')) {
                payload[field] = normalizePayloadValue(field, value);
            }
        });

        try {
            if (id) {
                await ApiService.update(entity, id, payload);
            } else {
                await ApiService.create(entity, payload);
            }
            resetForm();
            await load();
        } catch (err) {
            alert(err.message || 'Error al guardar');
        }
    });

    resetButton.addEventListener('click', resetForm);
    newRecordLink.addEventListener('click', resetForm);

    if (!isStaff) {
        if (newRecordLink) newRecordLink.style.display = 'none';
        if (formSection) formSection.style.display = 'none';
        const actionsHeader = document.querySelector('.data-table thead th:last-child');
        if (actionsHeader) actionsHeader.style.display = 'none';
    }

    document.querySelectorAll('.btn-example').forEach((btn) => {
        btn.addEventListener('click', () => {
            try {
                const payload = JSON.parse(btn.dataset.payload);
                // Rellenar el formulario con los datos del ejemplo
                Object.keys(payload).forEach(key => {
                    if (form.elements[key]) {
                        form.elements[key].value = payload[key];
                    }
                });
                // Hacer scroll al formulario para que el usuario lo vea
                document.getElementById('formulario').scrollIntoView({ behavior: 'smooth' });
            } catch (err) {
                console.error('Error al aplicar ejemplo:', err);
            }
        });
    });

    const editId = new URLSearchParams(window.location.search).get('edit');
    load().then(() => {
        if (editId && isStaff) {
            const editButton = tbody.querySelector(`button[data-edit-id="${editId}"]`);
            if (editButton) editButton.click();
        }
    });
});
