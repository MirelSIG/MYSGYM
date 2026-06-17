document.addEventListener('DOMContentLoaded', () => {
    const shell = document.getElementById('entity-shell');
    if (!shell) return;

    const entity = shell.dataset.entity;
    const title = shell.dataset.title || entity;
    const role = (ApiService.getRole() || '').toLowerCase();

    const tableHead = document.getElementById('entity-table-head');
    const tableBody = document.getElementById('entity-table-body');
    const entityCount = document.getElementById('entity-count');
    const entityAccess = document.getElementById('entity-access');
    const entityModeTitle = document.getElementById('entity-mode-title');
    const entityModeCopy = document.getElementById('entity-mode-copy');
    const entityFormTitle = document.getElementById('entity-form-title');
    const entityFormCopy = document.getElementById('entity-form-copy');
    const entityForm = document.getElementById('entity-form');
    const entityFields = document.getElementById('entity-fields');
    const entityFormError = document.getElementById('entity-form-error');
    const entityNewBtn = document.getElementById('entity-new-btn');
    const entityRefreshBtn = document.getElementById('entity-refresh-btn');
    const entityCancelBtn = document.getElementById('entity-cancel-btn');
    const entitySubmitBtn = document.getElementById('entity-submit-btn');

    const state = {
        rows: [],
        selected: null,
    };

    const staff = isStaff(role);
    const ENTITY_DEFINITIONS = getEntityDefinitions();
    const definition = ENTITY_DEFINITIONS[entity] || null;
    const displayLabel = getDisplayLabel(entity, role, definition);
    const displayLabelLower = displayLabel.toLowerCase();
    const pageTitle = document.querySelector('.sec-title');
    const pageFooter = document.getElementById('entity-footer-copy');

    if (!definition) {
        renderAccess('pendiente', 'Entidad no soportada', 'No existe configuracion para esta pantalla.');
        return;
    }

    if (pageTitle) pageTitle.textContent = displayLabel || title;
    if (pageFooter) {
        pageFooter.textContent = `Sincronizando ${displayLabelLower} con la API`;
    }
    if (entityModeTitle) entityModeTitle.textContent = displayLabel || title;
    if (entityModeCopy) {
        entityModeCopy.textContent = definition.description || 'Listado conectado con el backend.';
    }
    document.title = `MYSGYM | ${displayLabel || definition.label || title}`;

    if (entityRefreshBtn) {
        entityRefreshBtn.addEventListener('click', () => loadEntity());
    }

    if (entityNewBtn) {
        entityNewBtn.addEventListener('click', () => {
            if (!canCreate()) return;
            openEditor(null);
        });
    }

    if (entityCancelBtn) {
        entityCancelBtn.addEventListener('click', () => openEditor(null, { silent: true }));
    }

    if (entityForm) {
        entityForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            await submitForm();
        });
    }

    async function loadEntity() {
        const listEndpoint = getListEndpoint();
        if (!listEndpoint) {
            state.rows = [];
            renderTable([]);
            renderAccess(
                'inactivo',
                'Sin acceso de lectura',
                'Tu rol actual no tiene un listado expuesto para esta entidad.'
            );
            updateFormVisibility();
            return;
        }

        renderAccess('pendiente', 'Cargando', `Consultando ${displayLabelLower} desde la API.`);
        if (entityCount) entityCount.textContent = 'Cargando registros...';
        renderTable([]);

        try {
            const data = await ApiService.request(listEndpoint);
            const rows = normalizeRows(data);
            state.rows = rows;
            renderTable(rows);
            renderAccess(
                'activo',
                'Conectado',
                `${rows.length} registro(s) cargado(s) para ${displayLabelLower}.`
            );
        } catch (error) {
            state.rows = [];
            renderTable([]);
            renderAccess('inactivo', 'Error API', error.message || 'No se pudo cargar la entidad.');
        } finally {
            openInitialEditor();
            updateFormVisibility();
        }
    }

    function openInitialEditor() {
        if (state.rows.length === 1 && !canCreate() && canEdit(state.rows[0])) {
            openEditor(state.rows[0], { silent: true });
            return;
        }

        openEditor(null, { silent: true });
    }

    function renderTable(rows) {
        if (!tableHead || !tableBody) return;

        const columns = typeof definition.getColumns === 'function' ? definition.getColumns(role) : definition.columns;
        const actionColumns = getActionColumns();
        const totalColumns = columns.length + (actionColumns.length ? 1 : 0);

        tableHead.innerHTML = `
            <tr>
                ${columns.map((col) => `<th>${escapeHtml(col.label)}</th>`).join('')}
                ${actionColumns.length ? '<th>Acciones</th>' : ''}
            </tr>
        `;

        if (!rows.length) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="${totalColumns}">${escapeHtml(definition.emptyMessage || 'No hay registros')}</td>
                </tr>
            `;
            if (entityCount) entityCount.textContent = '0 registros';
            return;
        }

        tableBody.innerHTML = '';
        rows.forEach((row, index) => {
            const rowId = getRowId(row);
            const canEditRow = canEdit(row);
            const canDeleteRow = canDelete(row);
            const actionButtons = [];

            if (canEditRow) {
                actionButtons.push(
                    `<button class="btn-link btn-edit" type="button" data-index="${index}">Editar</button>`
                );
            }

            if (canDeleteRow) {
                actionButtons.push(
                    `<button class="btn-link danger btn-delete" type="button" data-index="${index}">Borrar</button>`
                );
            }

            if (entity === 'actividades' && role === 'cliente') {
                const count = row.reservas_count ?? 0;
                const max = row.aforo_maximo ?? 10;
                const full = count >= max;
                if (full) {
                    actionButtons.push(
                        `<span class="status inactivo" title="No hay plazas disponibles">Completo</span>`
                    );
                } else {
                    actionButtons.push(
                        `<button class="btn-link btn-reserve" type="button" data-index="${index}">Reservar</button>`
                    );
                }
            }

            const tr = document.createElement('tr');
            tr.dataset.id = rowId || '';
            tr.innerHTML = `
                ${columns.map((col) => `<td>${renderCell(row, col)}</td>`).join('')}
                ${actionButtons.length ? `<td>${actionButtons.join(' ')}</td>` : ''}
            `;
            tableBody.appendChild(tr);
        });

        tableBody.querySelectorAll('.btn-edit').forEach((button) => {
            button.addEventListener('click', (event) => {
                const index = Number(event.currentTarget.dataset.index);
                openEditor(state.rows[index] || null);
            });
        });

        tableBody.querySelectorAll('.btn-delete').forEach((button) => {
            button.addEventListener('click', async (event) => {
                const index = Number(event.currentTarget.dataset.index);
                const record = state.rows[index];
                if (!record) return;
                await deleteRecord(record);
            });
        });

        tableBody.querySelectorAll('.btn-reserve').forEach((button) => {
            button.addEventListener('click', async (event) => {
                const index = Number(event.currentTarget.dataset.index);
                const record = state.rows[index];
                if (!record) return;
                await quickReserve(record);
            });
        });

        if (entityCount) {
            entityCount.textContent = `${rows.length} registro${rows.length === 1 ? '' : 's'}`;
        }
    }

    function renderCell(row, column) {
        let value = row[column.key];

        if (column.key === 'aforo_maximo' || column.key === 'capacidad') {
            const count = row.reservas_count;
            const max = value ?? 10;
            if (count !== undefined) {
                const full = count >= max;
                return `<span class="status ${full ? 'inactivo' : 'activo'}">${count} / ${max}</span>`;
            }
            return `<span class="mono">${escapeHtml(String(max))}</span>`;
        }

        if (value === null || value === undefined || value === '') {
            return '&mdash;';
        }

        if (column.type === 'status' || /estado/i.test(column.key)) {
            const status = normalizeStatus(value);
            return `<span class="status ${status}">${escapeHtml(String(value))}</span>`;
        }

        if (column.type === 'money' || /monto|importe|precio/i.test(column.key)) {
            return `<span class="price">${escapeHtml(formatMoney(value))}</span>`;
        }

        if (column.type === 'mono' || /id_|_id$/i.test(column.key)) {
            return `<span class="mono">${escapeHtml(String(value))}</span>`;
        }

        return escapeHtml(formatValue(value));
    }

    function openEditor(record, options = {}) {
        state.selected = record;
        const mode = record ? 'edit' : 'create';
        const fields = definition.getFields(role, mode, record);

        if (!entityForm) return;

        entityFormError.style.display = 'none';
        entityFormError.textContent = '';
        if (entityFields) entityFields.innerHTML = '';

        const hiddenId = entityForm.querySelector('input[name="__id"]');
        hiddenId.value = record ? getRowId(record) || '' : '';

        fields.forEach((field) => {
            const wrapper = document.createElement('label');
            wrapper.dataset.field = field.name;

            const label = document.createElement('span');
            label.textContent = field.label;

            const control = buildControl(field, record, mode);

            wrapper.appendChild(label);
            wrapper.appendChild(control);
            if (entityFields) {
                entityFields.appendChild(wrapper);
            } else {
                entityForm.appendChild(wrapper);
            }
        });

        if (entitySubmitBtn) {
            entitySubmitBtn.textContent = record ? 'Actualizar' : 'Crear';
            entitySubmitBtn.disabled = !canWrite(mode, record);
        }

        if (entityFormTitle) {
            entityFormTitle.textContent = record ? `Editar ${displayLabel}` : `Nuevo ${displayLabel}`;
        }

        if (entityFormCopy) {
            entityFormCopy.textContent = record
                ? `Actualiza el registro seleccionado de ${displayLabelLower}.`
                : `Completa el formulario para crear un nuevo registro de ${displayLabelLower}.`;
        }

        if (!options.silent) {
            const firstInput = entityForm.querySelector('input, textarea, select');
            if (firstInput) firstInput.focus();
        }

        updateFormVisibility();
    }

    function buildControl(field, record, mode) {
        const fieldValue = record ? record[field.name] : '';
        const baseName = field.name;
        const commonAttrs = {
            name: baseName,
            required: Boolean(field.required && (!field.optionalOnEdit || mode === 'create')),
            disabled: Boolean(field.disabled || !canWrite(mode, record)),
        };

        if (field.type === 'textarea') {
            const textarea = document.createElement('textarea');
            textarea.name = baseName;
            textarea.rows = field.rows || 4;
            textarea.value = fieldValue ?? '';
            textarea.required = commonAttrs.required;
            textarea.disabled = commonAttrs.disabled;
            return textarea;
        }

        if (field.type === 'select') {
            const select = document.createElement('select');
            select.name = baseName;
            select.required = commonAttrs.required;
            select.disabled = commonAttrs.disabled;
            (field.options || []).forEach((option) => {
                const optionNode = document.createElement('option');
                optionNode.value = option.value;
                optionNode.textContent = option.label;
                if (String(option.value) === String(fieldValue)) {
                    optionNode.selected = true;
                }
                select.appendChild(optionNode);
            });
            return select;
        }

        const input = document.createElement('input');
        input.type = field.type || 'text';
        input.name = baseName;
        input.value = fieldValue ?? '';
        input.required = commonAttrs.required;
        input.disabled = commonAttrs.disabled;
        if (field.placeholder) input.placeholder = field.placeholder;
        return input;
    }

    async function submitForm() {
        if (!entityForm) return;

        const formData = new FormData(entityForm);
        const id = formData.get('__id');
        const record = id ? state.rows.find((row) => String(getRowId(row)) === String(id)) || null : null;
        const mode = record ? 'edit' : 'create';
        const fields = definition.getFields(role, mode, record);

        const payload = {};
        fields.forEach((field) => {
            const raw = formData.get(field.name);
            if (raw === null || raw === undefined || String(raw).trim() === '') return;
            payload[field.name] = coerceValue(field, raw);
        });

        try {
            setFormError('');
            const endpoint = record ? definition.updateEndpoint(record, role) : definition.createEndpoint(role);
            if (!endpoint) {
                throw new Error('Esta accion no esta disponible para tu rol.');
            }

            const method = record ? 'PUT' : 'POST';
            await ApiService.request(endpoint, {
                method,
                body: payload,
            });

            await loadEntity();
        } catch (error) {
            setFormError(error.message || 'No se pudo guardar el registro.');
        }
    }

    async function deleteRecord(record) {
        const endpoint = definition.deleteEndpoint(record, role);
        if (!endpoint) {
            setFormError('Esta accion no esta disponible para tu rol.');
            return;
        }

        if (!confirm(`Borrar ${displayLabelLower}?`)) return;

        try {
            setFormError('');
            await ApiService.request(endpoint, { method: 'DELETE' });
            await loadEntity();
        } catch (error) {
            setFormError(error.message || 'No se pudo borrar el registro.');
        }
    }

    async function quickReserve(activity) {
        if (!confirm(`¿Quieres reservar una plaza en "${activity.nombre}"?`)) return;

        try {
            setFormError('');
            await ApiService.request('/reservas/', {
                method: 'POST',
                body: { actividad_id: activity.id_actividad }
            });
            alert('¡Reserva realizada con éxito!');
            await loadEntity();
        } catch (error) {
            alert(error.message || 'No se pudo realizar la reserva.');
        }
    }

    function setFormError(message) {
        if (!entityFormError) return;
        if (!message) {
            entityFormError.style.display = 'none';
            entityFormError.textContent = '';
            return;
        }
        entityFormError.style.display = 'block';
        entityFormError.textContent = message;
    }

    function updateFormVisibility() {
        const canInteract = canCreate() || canAnyEdit();
        if (entityNewBtn) {
            entityNewBtn.style.display = canCreate() ? '' : 'none';
        }
        if (entityForm) {
            entityForm.style.display = canInteract ? 'grid' : 'none';
        }
        if (entityFormTitle && entityFormCopy && !canInteract) {
            entityFormTitle.textContent = 'Vista de solo lectura';
            entityFormCopy.textContent = 'Tu rol actual no tiene permisos de edicion para esta entidad.';
        }
        if (entitySubmitBtn) {
            entitySubmitBtn.disabled = !canInteract;
        }
        if (entityCancelBtn) {
            entityCancelBtn.style.display = canInteract ? '' : 'none';
        }
    }

    function canCreate() {
        return Boolean(definition.canCreate && definition.canCreate(role));
    }

    function canEdit(record) {
        return Boolean(definition.canEdit && definition.canEdit(role, record));
    }

    function canDelete(record) {
        return Boolean(definition.canDelete && definition.canDelete(role, record));
    }

    function canAnyEdit() {
        return Boolean(definition.canEdit && definition.canEdit(role, null));
    }

    function canWrite(mode, record) {
        return mode === 'create' ? canCreate() : canEdit(record);
    }

    function getListEndpoint() {
        return definition.listEndpoint ? definition.listEndpoint(role) : null;
    }

    function getActionColumns() {
        const actions = [];
        if (canAnyEdit()) actions.push('edit');
        if (canDeleteForAnyRow()) actions.push('delete');
        return actions;
    }

    function canDeleteForAnyRow() {
        return Boolean(definition.canDelete && definition.canDelete(role, null));
    }

    function getRowId(row) {
        return row?.[definition.idField] ?? row?.id ?? row?.id_reserva ?? row?.id_pago ?? row?.id_usuario ?? row?.id_empleado ?? row?.id_sala ?? row?.id_horario ?? row?.id_actividad ?? row?.id_material ?? row?.id_incidencia ?? null;
    }

    function normalizeRows(data) {
        if (Array.isArray(data)) return data;
        if (data && typeof data === 'object') return [data];
        return [];
    }

    function formatValue(value) {
        if (value === null || value === undefined) return '';
        if (typeof value === 'number') {
            return Number.isInteger(value) ? String(value) : value.toFixed(2);
        }
        const stringValue = String(value);
        if (/^\d{4}-\d{2}-\d{2}T/.test(stringValue)) {
            return stringValue.replace('T', ' ').replace('Z', '');
        }
        return stringValue;
    }

    function formatMoney(value) {
        const number = Number(value);
        if (Number.isNaN(number)) return String(value);
        return `${number.toFixed(2)} €`;
    }

    function coerceValue(field, value) {
        if (field.type === 'number' || field.type === 'range' || field.numeric) {
            const number = Number(value);
            return Number.isNaN(number) ? value : number;
        }
        return String(value).trim();
    }

    function normalizeStatus(value) {
        const normalized = String(value).toLowerCase();
        if (['activo', 'activa', 'confirmada', 'completado', 'completada', 'cobrado', 'operativo'].includes(normalized)) {
            return 'activo';
        }
        if (['pendiente', 'revision', 'en espera', 'abierto', 'abierta'].includes(normalized)) {
            return 'pendiente';
        }
        return 'inactivo';
    }

    function escapeHtml(value) {
        return String(value)
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#39;');
    }

    function renderAccess(statusClass, titleText, copyText) {
        if (entityAccess) {
            entityAccess.className = `status ${statusClass}`;
            entityAccess.textContent = titleText;
        }
        if (entityModeTitle) entityModeTitle.textContent = titleText;
        if (entityModeCopy) entityModeCopy.textContent = copyText;
    }

    function isAdmin(userRole) {
        return String(userRole || '').toLowerCase() === 'admin';
    }

    function isMonitor(userRole) {
        return String(userRole || '').toLowerCase() === 'monitor';
    }

    function isStaff(userRole) {
        return isAdmin(userRole) || isMonitor(userRole);
    }

    function getDisplayLabel(entityName, userRole, entityDefinition) {
        if (entityName === 'usuarios' && String(userRole || '').toLowerCase() === 'cliente') {
            return 'Perfil';
        }
        if (entityName === 'reservas' && String(userRole || '').toLowerCase() === 'cliente') {
            return 'Mis reservas';
        }
        if (entityName === 'pagos' && String(userRole || '').toLowerCase() === 'cliente') {
            return 'Mis pagos';
        }
        return entityDefinition?.label || entityName;
    }

    function getEntityDefinitions() {
        return {
        usuarios: {
            label: 'Usuarios',
            description: 'Listado y edicion de perfiles de clientes.',
            idField: 'id_usuario',
            columns: [
                { key: 'id_usuario', label: 'ID', type: 'mono' },
                { key: 'nombre', label: 'Nombre' },
                { key: 'email', label: 'Email' },
                { key: 'telefono', label: 'Telefono' },
                { key: 'fecha_registro', label: 'Fecha', type: 'mono' },
                { key: 'estado', label: 'Estado', type: 'status' },
            ],
            emptyMessage: 'No hay usuarios cargados.',
            listEndpoint(userRole) {
                if (userRole === 'cliente') return '/usuarios/perfil';
                if (isAdmin(userRole)) return '/usuarios/';
                return null;
            },
            canCreate(userRole) {
                return isAdmin(userRole);
            },
            canEdit(userRole) {
                return userRole === 'cliente' || isAdmin(userRole);
            },
            canDelete(userRole) {
                return isAdmin(userRole);
            },
            getFields(userRole, mode) {
                if (mode === 'create') {
                    return [
                        { name: 'nombre', label: 'Nombre', type: 'text', required: true },
                        { name: 'email', label: 'Email', type: 'email', required: true },
                        { name: 'password', label: 'Contraseña', type: 'password', required: true },
                        { name: 'telefono', label: 'Telefono', type: 'text' },
                    ];
                }

                const fields = [
                    { name: 'nombre', label: 'Nombre', type: 'text', required: true },
                    { name: 'telefono', label: 'Telefono', type: 'text' },
                ];

                if (isStaff(userRole)) {
                    fields.push({ name: 'estado', label: 'Estado', type: 'select', options: [
                        { value: 'activo', label: 'Activo' },
                        { value: 'inactivo', label: 'Inactivo' },
                    ] });
                }

                return fields;
            },
            createEndpoint() {
                return '/auth/register';
            },
            updateEndpoint(record) {
                return `/usuarios/${getEntityId(record)}`;
            },
            deleteEndpoint(record) {
                return `/usuarios/${getEntityId(record)}`;
            },
        },
        empleados: {
            label: 'Empleados',
            description: 'Monitores y administradores del gimnasio.',
            idField: 'id_empleado',
            columns: [
                { key: 'id_empleado', label: 'ID', type: 'mono' },
                { key: 'nombre', label: 'Nombre' },
                { key: 'email', label: 'Email' },
                { key: 'rol', label: 'Rol' },
                { key: 'fecha_contratacion', label: 'Fecha', type: 'mono' },
            ],
            emptyMessage: 'No hay empleados cargados.',
            listEndpoint(userRole) {
                return isAdmin(userRole) ? '/empleados/' : null;
            },
            canCreate(userRole) {
                return isAdmin(userRole);
            },
            canEdit(userRole) {
                return isAdmin(userRole);
            },
            canDelete(userRole) {
                return isAdmin(userRole);
            },
            getFields(userRole, mode) {
                if (mode === 'create') {
                    return [
                        { name: 'nombre', label: 'Nombre', type: 'text', required: true },
                        { name: 'email', label: 'Email', type: 'email', required: true },
                        { name: 'password', label: 'Contraseña', type: 'password', required: true },
                        { name: 'rol', label: 'Rol', type: 'select', required: true, options: [
                            { value: 'monitor', label: 'Monitor' },
                            { value: 'admin', label: 'Admin' },
                        ] },
                    ];
                }
                return [
                    { name: 'nombre', label: 'Nombre', type: 'text', required: true },
                    { name: 'email', label: 'Email', type: 'email', required: true },
                    { name: 'rol', label: 'Rol', type: 'select', required: true, options: [
                        { value: 'monitor', label: 'Monitor' },
                        { value: 'admin', label: 'Admin' },
                    ] },
                ];
            },
            createEndpoint() {
                return '/auth/register-empleado';
            },
            updateEndpoint(record) {
                return `/empleados/${getEntityId(record)}`;
            },
            deleteEndpoint(record) {
                return `/empleados/${getEntityId(record)}`;
            },
        },
        salas: {
            label: 'Salas',
            description: 'Infraestructura del gimnasio.',
            idField: 'id_sala',
            columns: [
                { key: 'id_sala', label: 'ID', type: 'mono' },
                { key: 'nombre', label: 'Nombre' },
                { key: 'capacidad', label: 'Capacidad', type: 'mono' },
            ],
            emptyMessage: 'No hay salas cargadas.',
            listEndpoint() {
                return '/gym/salas';
            },
            canCreate(userRole) {
                return isAdmin(userRole);
            },
            canEdit(userRole) {
                return isAdmin(userRole);
            },
            canDelete(userRole) {
                return isAdmin(userRole);
            },
            getFields() {
                return [
                    { name: 'nombre', label: 'Nombre', type: 'text', required: true },
                    { name: 'capacidad', label: 'Capacidad', type: 'number', required: true },
                ];
            },
            createEndpoint() {
                return '/gym/salas';
            },
            updateEndpoint(record) {
                return `/gym/salas/${getEntityId(record)}`;
            },
            deleteEndpoint(record) {
                return `/gym/salas/${getEntityId(record)}`;
            },
        },
        horarios: {
            label: 'Horarios',
            description: 'Tramos horarios usados por las actividades.',
            idField: 'id_horario',
            columns: [
                { key: 'id_horario', label: 'ID', type: 'mono' },
                { key: 'dia_semana', label: 'Dia' },
                { key: 'hora_inicio', label: 'Inicio', type: 'mono' },
                { key: 'hora_fin', label: 'Fin', type: 'mono' },
            ],
            emptyMessage: 'No hay horarios cargados.',
            listEndpoint() {
                return '/gym/horarios';
            },
            canCreate(userRole) {
                return isAdmin(userRole);
            },
            canEdit(userRole) {
                return isAdmin(userRole);
            },
            canDelete(userRole) {
                return isAdmin(userRole);
            },
            getFields() {
                return [
                    { name: 'dia_semana', label: 'Dia de semana', type: 'text', required: true },
                    { name: 'hora_inicio', label: 'Hora inicio', type: 'time', required: true },
                    { name: 'hora_fin', label: 'Hora fin', type: 'time', required: true },
                ];
            },
            createEndpoint() {
                return '/gym/horarios';
            },
            updateEndpoint(record) {
                return `/gym/horarios/${getEntityId(record)}`;
            },
            deleteEndpoint(record) {
                return `/gym/horarios/${getEntityId(record)}`;
            },
        },
        actividades: {
            label: 'Actividades',
            description: 'Clases y sesiones del gimnasio.',
            idField: 'id_actividad',
            columns: [
                { key: 'id_actividad', label: 'ID', type: 'mono' },
                { key: 'nombre', label: 'Nombre' },
                { key: 'descripcion', label: 'Descripcion' },
                { key: 'sala', label: 'Sala' },
                { key: 'monitor', label: 'Monitor' },
                { key: 'horario', label: 'Horario' },
                { key: 'aforo_maximo', label: 'Capacidad/Aforo', type: 'mono' },
            ],
            emptyMessage: 'No hay actividades cargadas.',
            listEndpoint() {
                return '/gym/actividades';
            },
            canCreate(userRole) {
                return isAdmin(userRole);
            },
            canEdit(userRole) {
                return isAdmin(userRole);
            },
            canDelete(userRole) {
                return isAdmin(userRole);
            },
            getFields() {
                return [
                    { name: 'nombre', label: 'Nombre', type: 'text', required: true },
                    { name: 'descripcion', label: 'Descripcion', type: 'textarea' },
                    { name: 'monitor_id', label: 'ID monitor', type: 'number' },
                    { name: 'sala_id', label: 'ID sala', type: 'number' },
                    { name: 'horario_id', label: 'ID horario', type: 'number' },
                    { name: 'aforo_maximo', label: 'Aforo maximo', type: 'number' },
                ];
            },
            createEndpoint() {
                return '/gym/actividades';
            },
            updateEndpoint(record) {
                return `/gym/actividades/${getEntityId(record)}`;
            },
            deleteEndpoint(record) {
                return `/gym/actividades/${getEntityId(record)}`;
            },
        },
        reservas: {
            label: 'Reservas',
            description: 'Reservas de actividades por usuario.',
            idField: 'id_reserva',
            getColumns(userRole) {
                const base = [
                    { key: 'id_reserva', label: 'ID', type: 'mono' },
                ];
                if (isAdmin(userRole) || isMonitor(userRole)) {
                    base.push({ key: 'usuario', label: 'Usuario' });
                }
                base.push(
                    { key: 'actividad', label: 'Actividad' },
                    { key: 'fecha', label: 'Fecha', type: 'mono' },
                    { key: 'estado', label: 'Estado', type: 'status' }
                );
                return base;
            },
            emptyMessage: 'No hay reservas cargadas.',
            listEndpoint(userRole) {
                if (isAdmin(userRole)) return '/reservas/';
                if (userRole === 'cliente') return '/reservas/mis-reservas';
                return null;
            },
            canCreate(userRole) {
                return String(userRole || '').toLowerCase() === 'cliente';
            },
            canEdit(userRole) {
                return isAdmin(userRole);
            },
            canDelete(userRole) {
                return String(userRole || '').toLowerCase() === 'cliente';
            },
            getFields(userRole, mode) {
                if (mode === 'create') {
                    return [
                        { name: 'actividad_id', label: 'ID actividad', type: 'number', required: true },
                    ];
                }

                if (isStaff(userRole)) {
                    return [
                        { name: 'estado', label: 'Estado', type: 'select', options: [
                            { value: 'pendiente', label: 'Pendiente' },
                            { value: 'confirmada', label: 'Confirmada' },
                            { value: 'cancelada', label: 'Cancelada' },
                        ] },
                    ];
                }

                return [];
            },
            createEndpoint() {
                return '/reservas/';
            },
            updateEndpoint(record) {
                return `/reservas/${getEntityId(record)}`;
            },
            deleteEndpoint(record) {
                return `/reservas/${getEntityId(record)}`;
            },
        },
        pagos: {
            label: 'Pagos',
            description: 'Historial de pagos y cobros.',
            idField: 'id_pago',
            getColumns(userRole) {
                const base = [
                    { key: 'id_pago', label: 'ID', type: 'mono' },
                ];
                if (isAdmin(userRole) || isMonitor(userRole)) {
                    base.push({ key: 'usuario', label: 'Usuario' });
                }
                base.push(
                    { key: 'monto', label: 'Monto', type: 'money' },
                    { key: 'fecha', label: 'Fecha', type: 'mono' },
                    { key: 'metodo', label: 'Metodo' },
                    { key: 'estado', label: 'Estado', type: 'status' }
                );
                return base;
            },
            emptyMessage: 'No hay pagos cargados.',
            listEndpoint(userRole) {
                if (isAdmin(userRole)) return '/pagos/';
                if (userRole === 'cliente') return '/pagos/historial';
                return null;
            },
            canCreate(userRole) {
                return String(userRole || '').toLowerCase() === 'cliente';
            },
            canEdit(userRole) {
                return isAdmin(userRole);
            },
            canDelete() {
                return false;
            },
            getFields(userRole, mode) {
                if (mode === 'create') {
                    return [
                        { name: 'monto', label: 'Monto', type: 'number', required: true },
                        { name: 'metodo_pago', label: 'Metodo de pago', type: 'text' },
                    ];
                }

                if (isStaff(userRole)) {
                    return [
                        { name: 'monto', label: 'Monto', type: 'number' },
                        { name: 'metodo_pago', label: 'Metodo de pago', type: 'text' },
                        { name: 'estado', label: 'Estado', type: 'text' },
                    ];
                }

                return [];
            },
            createEndpoint() {
                return '/pagos/';
            },
            updateEndpoint(record) {
                return `/pagos/${getEntityId(record)}`;
            },
            deleteEndpoint(record) {
                return `/pagos/${getEntityId(record)}`;
            },
        },
        material: {
            label: 'Material',
            description: 'Inventario de equipos y accesorios.',
            idField: 'id_material',
            columns: [
                { key: 'id_material', label: 'ID', type: 'mono' },
                { key: 'nombre', label: 'Nombre' },
                { key: 'estado', label: 'Estado', type: 'status' },
                { key: 'sala', label: 'Sala' },
            ],
            emptyMessage: 'No hay material cargado.',
            listEndpoint() {
                return '/mantenimiento/materiales';
            },
            canCreate(userRole) {
                return isAdmin(userRole);
            },
            canEdit(userRole) {
                return isAdmin(userRole);
            },
            canDelete(userRole) {
                return isAdmin(userRole);
            },
            getFields() {
                return [
                    { name: 'nombre', label: 'Nombre', type: 'text', required: true },
                    { name: 'estado', label: 'Estado', type: 'text' },
                    { name: 'sala_id', label: 'ID sala', type: 'number' },
                ];
            },
            createEndpoint() {
                return '/mantenimiento/materiales';
            },
            updateEndpoint(record) {
                return `/mantenimiento/materiales/${getEntityId(record)}`;
            },
            deleteEndpoint(record) {
                return `/mantenimiento/materiales/${getEntityId(record)}`;
            },
        },
        incidencias: {
            label: 'Incidencias',
            description: 'Averias y notificaciones de mantenimiento.',
            idField: 'id_incidencia',
            columns: [
                { key: 'id_incidencia', label: 'ID', type: 'mono' },
                { key: 'descripcion', label: 'Descripcion' },
                { key: 'material', label: 'Material' },
                { key: 'estado', label: 'Estado', type: 'status' },
                { key: 'fecha', label: 'Fecha', type: 'mono' },
            ],
            emptyMessage: 'No hay incidencias cargadas.',
            listEndpoint(userRole) {
                return isAdmin(userRole) ? '/mantenimiento/incidencias' : null;
            },
            canCreate() {
                return true;
            },
            canEdit(userRole) {
                return isAdmin(userRole);
            },
            canDelete() {
                return false;
            },
            getFields(userRole, mode) {
                if (mode === 'create') {
                    const fields = [
                        { name: 'descripcion', label: 'Descripcion', type: 'textarea', required: true },
                        { name: 'material_id', label: 'ID material', type: 'number' },
                    ];
                    if (isStaff(userRole)) {
                        fields.push({ name: 'empleado_id', label: 'ID empleado', type: 'number' });
                    }
                    return fields;
                }

                if (isStaff(userRole)) {
                    return [
                        { name: 'descripcion', label: 'Descripcion', type: 'textarea', required: true },
                        { name: 'estado', label: 'Estado', type: 'text' },
                        { name: 'empleado_id', label: 'ID empleado', type: 'number' },
                    ];
                }

                return [];
            },
            createEndpoint() {
                return '/mantenimiento/incidencias';
            },
            updateEndpoint(record) {
                return `/mantenimiento/incidencias/${getEntityId(record)}`;
            },
            deleteEndpoint() {
                return null;
            },
        },
        };
    }

    function getEntityId(record) {
        return record?.[definition.idField] ?? record?.id ?? null;
    }

    loadEntity();
});
