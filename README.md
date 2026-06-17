MYSGYM — Plataforma Integral para Gestión de Gimnasios
Proyecto colaborativo reciclado, modernizado y desplegado en la nube con Render
MYSGYM nació como un proyecto colaborativo académico.
Esta versión es una refactorización completa, donde se unificó backend + frontend en un solo servicio Flask, se migró MySQL → PostgreSQL y se adaptó toda la arquitectura para funcionar en Render Cloud.
El resultado es una plataforma ligera, escalable y lista para producción.
---
Descripción General
MYSGYM es un sistema de gestión para gimnasios que incluye:
• API REST modular con Flask
• Autenticación JWT
• Gestión de usuarios, empleados, reservas, pagos, salas, materiales y actividades
• Frontend integrado con Jinja2 + HTML + CSS + JavaScript
• Base de datos PostgreSQL gestionada por Render
• Despliegue mediante Docker + render.yaml
---
Estructura del Proyecto
```
MYSGYM/
├── app/
│   ├── __init__.py              # Factory principal (API + Frontend)
│   ├── models.py                # Modelos SQLAlchemy
│   ├── utils.py                 # Utilidades
│   ├── routes/                  # Blueprints API + Frontend
│   │   ├── auth.py
│   │   ├── usuarios.py
│   │   ├── empleados.py
│   │   ├── gym.py
│   │   ├── reservas.py
│   │   ├── pagos.py
│   │   ├── mantenimiento.py
│   │   └── frontend_routes.py
│   ├── templates/               # HTML (Jinja2)
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── entity.html
│   │   └── register.html
│   └── static/                  # CSS + JS
│       ├── css/
│       └── js/
├── run.py                       # Punto de entrada
├── Dockerfile                   # Imagen para Render
├── requirements.txt             # Dependencias
├── render.yaml                  # Infraestructura Render
└── tests/                       # Pruebas unitarias y funcionales
```
Tecnologías Utilizadas
Backend
• Python 3.12+
• Flask
• SQLAlchemy
• Flask-Migrate
• Flask-JWT-Extended
• Flask-CORS
Frontend
• HTML + Jinja2
• CSS
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