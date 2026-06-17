MYSGYM — Plataforma Integral para Gestión de Gimnasios
Proyecto colaborativo reciclado, modernizado y adaptado para despliegue en la nube con Render
MYSGYM es un sistema completo de gestión para gimnasios, desarrollado originalmente como un proyecto colaborativo académico.
Esta versión ha sido refactorizada, optimizada y unificada para funcionar como una aplicación full-stack Flask desplegable en la nube mediante Render, utilizando PostgreSQL gestionado y un único servicio web que sirve:
• API REST (Flask + SQLAlchemy + JWT)
• Frontend HTML/CSS/JS (Jinja + Static Assets)
• Base de datos PostgreSQL (Render Managed DB)
---
Características Principales
Backend API REST
• Framework: Flask
• ORM: SQLAlchemy
• Migraciones: Flask-Migrate
• Seguridad: JWT (Flask-JWT-Extended)
• Modularización con Blueprints
• Roles: Cliente, Monitor, Administrador
Frontend Integrado
• Plantillas Jinja2
• Estilos CSS personalizados
• JavaScript modular (fetch API, CRUD dinámico)
• Dashboard, login, gestión de entidades, etc.
Base de Datos
• PostgreSQL 18 (Render Managed)
• Modelos normalizados
• Seed automático opcional
Despliegue en la nube
• Un solo servicio Render (backend + frontend)
• Dockerfile optimizado
• render.yaml para infraestructura como código
---
Estructura del Proyecto (Versión Unificada)
MYSGYM/
├── app/
│   ├── __init__.py            # Factory principal (API + Frontend)
│   ├── models.py              # Modelos SQLAlchemy
│   ├── utils.py               # Utilidades y helpers
│   ├── routes/                # Blueprints API + Frontend
│   │   ├── auth.py
│   │   ├── usuarios.py
│   │   ├── gym.py
│   │   ├── reservas.py
│   │   ├── pagos.py
│   │   ├── mantenimiento.py
│   │   ├── empleados.py
│   │   └── frontend_routes.py # Rutas HTML
│   ├── templates/             # HTML (Jinja)
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── entity.html
│   │   └── register.html
│   └── static/                # CSS + JS
│       ├── css/
│       └── js/
├── run.py                     # Punto de entrada
├── Dockerfile                 # Imagen para Render
├── requirements.txt           # Dependencias
├── render.yaml                # Infraestructura Render
└── tests/                     # Pruebas unitarias y funcionales
Tecnologías Utilizadas
Backend
• Python 3.12+
• Flask
• SQLAlchemy
• Flask-Migrate
• Flask-JWT-Extended
• Flask-CORS
Frontend
• HTML5 + Jinja2
• CSS3
• JavaScript modular (fetch API)
Infraestructura
• Docker
• Render Web Service
• Render PostgreSQL
---
Instalación Local (Modo Desarrollo)
1. Clonar el repositorio
git clone https://github.com/MirelSIG/MYSGYM.git
cd MYSGYM
2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate
3. Instalar dependencias
pip install -r requirements.txt
4. Configurar variables de entorno
Crear .env:
DATABASE_URL=postgresql+psycopg://usuario:password@localhost:5432/mysgym
JWT_SECRET_KEY=super-secret-key
5. Ejecutar migraciones
flask db upgrade
6. Ejecutar servidor
python run.py
Finalmente, App disponible en: http://localhost:10000

☁️ Despliegue en Render
Render utiliza:
• Dockerfile para construir la imagen
• render.yaml para definir el servicio web
• DATABASE_URL para conectarse a PostgreSQL gestionado
Pasos:
1. Subir el repo a GitHub
2. Crear un Web Service en Render
3. Seleccionar el repo
4. Render detectará el Dockerfile automáticamente
5. Añadir variable de entorno: 
DATABASE_URL=postgresql+psycopg://...
6. Desplegar y esperar a que Render construya y ejecute la app

🧪 Pruebas
El proyecto incluye pruebas con pytest.
Ejecutar pruebas: pytest -q
Con reporte HTML:
pytest --html=reporte.html
Con cobertura:
pytest --cov=app --cov-report=html
Origen del Proyecto
Este proyecto nació como un trabajo colaborativo académico, desarrollado originalmente con:
• Flask
• MySQL
• Docker Compose
• Frontend separado
La versión actual es un reciclaje profesional, donde se:
• Unificó backend + frontend en un solo servicio Flask
• Migró MySQL → PostgreSQL
• Eliminó dependencias innecesarias
• Simplificó la arquitectura
• Adaptó todo para Render Cloud
• Modernizó rutas, seguridad y estructura
El resultado es una plataforma más ligera, escalable y lista para producción.
---
👤 Autoría y Créditos
Proyecto original: equipo colaborativo MYSGYM (https://github.com/MirelSIG/MYSGYM, https://github.com/yeremijesus9, https://github.com/GermanIllan, https://github.com/troyanojoi-sour)
Refactorización, unificación y despliegue cloud: Mirel Volcán (https://github.com/MirelSIG/MYSGYM)