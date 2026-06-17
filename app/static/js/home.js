document.addEventListener('DOMContentLoaded', async () => {
    const schema = window.MYSGYM_SCHEMA || {};
    const sections = window.MYSGYM_SECTIONS || [];
    const state = {};

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

    function setText(id, value) {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    }

    function renderPayments(payments) {
        const tbody = document.getElementById('latest-payments-body');
        if (!tbody) return;

        const latest = [...payments]
            .sort((a, b) => String(b.fecha_pago || '').localeCompare(String(a.fecha_pago || '')))
            .slice(0, 5);

        if (!latest.length) {
            tbody.innerHTML = '<tr><td colspan="4">No hay pagos registrados</td></tr>';
            return;
        }

        tbody.innerHTML = '';
        latest.forEach((payment) => {
            const tr = document.createElement('tr');
            appendCell(tr, payment.id_pago);
            appendCell(tr, payment.usuario_id);
            appendCell(tr, `${payment.monto ?? 0}€`);
            appendCell(tr, payment.metodo);
            tbody.appendChild(tr);
        });
    }

    function renderDistribution(totalRecords) {
        const list = document.getElementById('distribution-list');
        if (!list) return;

        list.innerHTML = '';
        sections.forEach((section) => {
            const count = (state[section.key] || []).length;
            const width = totalRecords ? (count / totalRecords) * 100 : 0;
            const row = document.createElement('div');
            row.className = 'bar-row';
            row.innerHTML = `
                <span class="bar-name"></span>
                <div class="bar-track"><div class="bar-fill"></div></div>
                <span class="bar-val"></span>
            `;
            row.querySelector('.bar-name').textContent = section.title;
            row.querySelector('.bar-fill').style.width = `${width}%`;
            row.querySelector('.bar-val').textContent = count;
            list.appendChild(row);
        });
    }

    function appendCell(row, value) {
        const cell = document.createElement('td');
        cell.textContent = value ?? '';
        row.appendChild(cell);
    }

    try {
        await Promise.all(sections.map(async (section) => {
            const card = document.querySelector(`[data-entity-card="${section.key}"]`);
            const countEl = card && card.querySelector('[data-count]');
            try {
                const rows = normalizeList(await ApiService.get(section.key));
                state[section.key] = rows;

                if (countEl) countEl.textContent = `${rows.length} registros`;
            } catch (err) {
                if (err.message === 'Unauthorized') throw err;
                state[section.key] = [];
                if (countEl) countEl.textContent = 'Error';
            }
        }));

        const totalRecords = sections.reduce((total, section) => total + (state[section.key] || []).length, 0);
        const activeUsers = (state.usuarios || []).filter((row) => statusClass(row.estado) === 'activo').length;
        const openIssues = (state.incidencias || []).filter((row) => statusClass(row.estado) === 'inactivo').length;
        const totalRevenue = (state.pagos || []).reduce((total, row) => total + Number.parseFloat(row.monto || 0), 0);
        const linkedEntities = Object.values(schema).filter((config) => {
            return (config.fields || []).some((field) => field.endsWith('_id'));
        }).length;

        setText('kpi-total-records', totalRecords);
        setText('kpi-active-users', activeUsers);
        setText('kpi-open-issues', openIssues);
        setText('kpi-total-revenue', Number.isFinite(totalRevenue) ? totalRevenue.toFixed(0) : '0');
        setText('kpi-linked-entities', linkedEntities);
        renderPayments(state.pagos || []);
        renderDistribution(totalRecords);
    } catch (err) {
        const tbody = document.getElementById('latest-payments-body');
        if (tbody) tbody.innerHTML = `<tr><td colspan="4">${err.message || 'Error al cargar datos'}</td></tr>`;
        const list = document.getElementById('distribution-list');
        if (list) list.textContent = err.message || 'Error al cargar datos';
    }
});
