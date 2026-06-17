// Configuración del frontend: URL base de la API.
// El frontend Flask sirve las páginas y el backend separado responde a las rutas REST.
const runtimeConfig = window.MYSGYM_CONFIG || {};
const isLocalHost = ['localhost', '127.0.0.1'].includes(window.location.hostname);
const defaultApiBaseUrl = isLocalHost
	? `http://${window.location.hostname}:8000`
	: 'https://backend-mysgym.onrender.com';
const API_BASE_URL = runtimeConfig.API_BASE_URL || defaultApiBaseUrl;

// Modo de desarrollo: si está activado, las llamadas a la API se simulan
// en el frontend con datos en memoria para poder hacer ensayos sin backend.
// Cambia a `false` para usar el backend real.
const USE_MOCK_API = runtimeConfig.USE_MOCK_API === true;
