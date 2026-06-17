# MYSGYM — Backend API

Sistema de gestión integral para gimnasios desarrollado con **Python Flask**, **SQLAlchemy** y **MySQL**.

## Estructura del Proyecto

El proyecto sigue un patrón modular utilizando Blueprints para facilitar la escalabilidad:

```text
Backend_MYSGYM/
├── app/                    # Lógica principal de la aplicación
│   ├── routes/             # Blueprints (Auth, Gym, Usuarios, etc.)
│   ├── models.py           # Modelos de SQLAlchemy
│   ├── utils.py            # Decoradores y utilidades de seguridad
│   └── __init__.py         # Factory de la aplicación
├── database/               # Volumen de persistencia de MySQL (Docker)
├── docs/                   # Documentación detallada (Épicas, Diagramas, E/R)
├── migrations/             # Migraciones de la base de datos
├── scripts/                # Scripts de utilidad (Carga de datos/Seed)
├── tests/                  # Pruebas unitarias y de integración
├── database_schema.sql     # Script SQL completo de la DB
├── docker-compose.yml      # Orquestación de contenedores
├── run.py                  # Punto de entrada de la aplicación
└── requirements.txt        # Dependencias del proyecto
```

## Tecnologías utilizadas

*   **Framework:** Flask
*   **Base de Datos:** MySQL 8.0 (Dockerizado)
*   **ORM:** SQLAlchemy + Flask-Migrate
*   **Seguridad:** Flask-JWT-Extended (Roles: Cliente, Monitor, Admin)

## Requisitos previos

Antes de instalar el proyecto, asegúrate de tener:

- **Python 3.12+**
- **Docker**
- **Docker Compose**
- **Git**

## Instalación paso a paso

Sigue estos pasos para configurar el proyecto en un ordenador nuevo desde cero:

### 1. Clonar el repositorio
Abre una terminal y descarga el código:
```bash
git clone <URL_DEL_REPO>
cd Backend_MYSGYM
```

### 2. Levantar la Base de Datos (local)
Si trabajas en tu equipo, puedes usar MySQL con Docker como hasta ahora:
```bash
docker-compose up -d
```
*La base de datos estará disponible en `localhost:3307`.*

En Render, el backend usa una base gestionada de PostgreSQL y recibe su conexión desde `DATABASE_URL`.

### 3. Configurar Variables de Entorno
Crea un archivo llamado `.env` en la raíz del proyecto con el siguiente contenido base:
```env
DB_HOST=localhost
DB_PORT=3307
DB_USER=root
DB_PASSWORD=root_password
DB_NAME=gimnasio
JWT_SECRET_KEY=super-secret-key
```

Si despliegas en Render, no necesitas definir `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` ni `DB_NAME` si `DATABASE_URL` ya está presente.

### 4. Crear y activar el entorno virtual
**En Windows:**
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

**En macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 5. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 6. Cargar datos de prueba (Opcional)
Para insertar datos iniciales (salas, empleados, actividades) en la base de datos:
```bash
python seed_db.py
```

### 7. Ejecutar el backend
```bash
python run.py
```
El servidor estará disponible en `http://localhost:8000`.

---

## Scripts de Utilidad

- **[seed_db.py](seed_db.py)**: Script principal para poblar la base de datos con información didáctica inicial.
- **[database_schema.sql](database_schema.sql)**: Esquema completo de la base de datos (se ejecuta automáticamente en el primer `docker-compose up`).

## Tests

El proyecto incluye pruebas automatizadas con `pytest` para validar el estado de la base de datos y el flujo de integración.

### Qué cubren

*   La prueba principal de integración en [tests/test_db.py](tests/test_db.py) usa una base SQLite temporal, crea las tablas desde los modelos y verifica tablas, columnas y claves foráneas importantes.
*   La configuración de [pytest.ini](pytest.ini) ignora `database/` durante la recolección, evitando errores por archivos internos de MySQL.

### Cómo ejecutarlos

```bash
.venv/bin/python -m pytest -q
```

Para generar un reporte HTML detallado:

```bash
.venv/bin/python -m pytest -q --html=reporte.html
```

Para medir cobertura de código:

```bash
.venv/bin/python -m pytest -q --cov=app --cov-report=html --cov-report=term
```

Para análisis estático de código:

```bash
.venv/bin/python -m pylint app/ --output-format=parseable
.venv/bin/python -m pylint app/ --disable=missing-docstring
```

### Generación de reportes

El progreso de cada prueba se guarda automáticamente en `test_progress.log` con fecha y hora (hook configurado en [tests/conftest.py](tests/conftest.py)). 

Los reportes HTML se generan en:
- `reporte.html` — Detalles de ejecución de pruebas
- `htmlcov/` — Cobertura de código por línea y módulo

Pylint evalúa la calidad del código en `pylint_report.txt` con puntuación y recomendaciones.

---

*Desarrollado para el proyecto final de MYSGYM.*
