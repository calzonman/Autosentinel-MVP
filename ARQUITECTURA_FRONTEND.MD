# Arquitectura del Frontend - Documentación Técnica y de Negocio

Este documento contiene la especificación detallada de la arquitectura de la interfaz de usuario (Frontend) del software de **Detección, Evaluación Financiera y Arbitraje Automotriz (AutoSentinel MVP)**.

---

## 📂 Árbol de Directorios del Frontend (`frontend/`)

```text
frontend/
├── public/
│   ├── favicon.svg             # Isotipo vectorizado para la pestaña del navegador
│   └── icons.svg               # Sprites vectoriales de íconos del sistema
├── src/
│   ├── assets/
│   │   ├── hero.png            # Imagen ilustrativa para componentes o vistas vacías
│   │   ├── svelte.svg          # Isotipo de Svelte
│   │   └── vite.svg            # Isotipo de Vite
│   ├── lib/
│   │   ├── Counter.svelte      # Componente de prueba/ejemplo básico de Svelte Runes
│   │   ├── Dashboard.svelte    # Panel principal con tarjetas de vehículos, pestañas de mercado dual y filtros
│   │   ├── MarketDetailModal.svelte # Modal desplegable para análisis de muestra estadística (Mín, Máx, Mediana, Promedio)
│   │   ├── MarketValidationModal.svelte # Modal de ejecución y monitoreo de la validación dual de mercado
│   │   ├── Navbar.svelte       # Barra de navegación superior con estado de sesión, servidor y disparador del Centinela
│   │   └── SettingsModal.svelte # Modal de configuración de parámetros del Centinela, Calculadora y Credenciales
│   ├── app.css                 # Sistema de diseño global (Design System, Tokens HSL, Glassmorphism, CSS Variables)
│   ├── App.svelte              # Componente raíz orquestador de estado global y vistas modales
│   └── main.js                 # Punto de entrada de JavaScript e inicialización de la app Svelte
├── dist/                       # Build final de producción generado por Vite
├── index.html                  # Plantilla HTML5 semántica y contenedor root `#app`
├── jsconfig.json               # Configuración de resolución de rutas e IntelliSense en VS Code
├── package.json                # Especificación de dependencias (Svelte 5, Vite) y scripts de build
├── svelte.config.js            # Configuración del compilador de Svelte
└── vite.config.js              # Configuración de empaquetado y servidor de desarrollo Vite
```

---

## 🏛️ Documentación de Directorios (Frontend)

### 📁 `frontend/`
- **Función Técnica Exacta**: Directorio raíz de la aplicación cliente construida en Svelte 5 y empaquetada con Vite 8. Aloja los componentes web, estilos CSS globales, plantillas y archivos de configuración de compilación.
- **Modelo de Negocio / Contexto General**: Constituye la interfaz de usuario interactiva ("Single Page Application" o SPA) con estética Glassmorphism avanzada. Permite a los inversionistas o compradores de autos visualizar oportunidades filtradas en tiempo real, comparar mercados (Chileautos vs Marketplace), disparar validaciones automáticas y exportar reportes a Google Sheets.
- **Dependencias**:
  - **Depende de**: Node.js, `svelte`, `@sveltejs/vite-plugin-svelte`, `vite`.
  - **Utilizado por**: Navegadores web que se conectan a `http://localhost:5173`. Consume la API REST del backend en `http://127.0.0.1:8000`.

---

### 📁 `frontend/public/`
- **Función Técnica Exacta**: Directorio de recursos estáticos servidos directamente en la raíz por Vite sin procesamiento del compilador.
- **Modelo de Negocio / Contexto General**: Almacena los elementos de branding visual (favicons e íconos SVG) que identifican la marca AutoSentinel en el navegador del usuario.
- **Dependencias**:
  - **Depende de**: Formato estándar SVG.
  - **Utilizado por**: `frontend/index.html`.

---

### 📁 `frontend/src/`
- **Función Técnica Exacta**: Directorio de código fuente primario. Contiene el punto de entrada `main.js`, el componente raíz `App.svelte`, los estilos universales `app.css` y las carpetas de utilidades y componentes `lib/` y `assets/`.
- **Modelo de Negocio / Contexto General**: Contiene toda la lógica de presentación visual, gestión de estado reactivo local, comunicación vía `fetch` HTTP con el backend FastAPI e interacciones del usuario.
- **Dependencias**:
  - **Depende de**: Componentes internos en `lib/` y estilos en `app.css`.
  - **Utilizado por**: Compilador Vite durante `npm run dev` y `npm run build`.

---

### 📁 `frontend/src/assets/`
- **Función Técnica Exacta**: Directorio de recursos gráficos vectoriales y mapas de bits procesados y optimizados por el pipeline de Vite durante la compilación.
- **Modelo de Negocio / Contexto General**: Provee imágenes de soporte visual para la interfaz de usuario.
- **Dependencias**:
  - **Depende de**: Formatos PNG/SVG.
  - **Utilizado por**: Componentes Svelte en `src/`.

---

### 📁 `frontend/src/lib/`
- **Función Técnica Exacta**: Biblioteca de componentes Svelte reutilizables e independientes (`Navbar.svelte`, `Dashboard.svelte`, `MarketValidationModal.svelte`, `MarketDetailModal.svelte`, `SettingsModal.svelte`).
- **Modelo de Negocio / Contexto General**: Subdivide la aplicación en módulos funcionales especializados (Barra Superior, Dashboard de Tarjetas, Modales de Validación, Detalles Estadísticos y Configuración).
- **Dependencias**:
  - **Depende de**: Svelte framework (`createEventDispatcher`, bindings reactivos).
  - **Utilizado por**: `frontend/src/App.svelte`.

---

### 📁 `frontend/dist/`
- **Función Técnica Exacta**: Directorio generado automáticamente por `npm run build` que contiene los archivos HTML, CSS y JS minificados y empaquetados para producción.
- **Modelo de Negocio / Contexto General**: Representa el entregable optimizado listo para ser desplegado en servidores web como Nginx, Vercel o GitHub Pages.
- **Dependencias**:
  - **Depende de**: Proceso de compilación `vite build`.
  - **Utilizado por**: Servidores web de producción.

---

## 📄 Documentación Detallada de Archivos (Frontend)

### 1. `frontend/package.json`
- **Función Técnica Exacta**: Manifiesto del proyecto Node.js. Define el nombre (`frontend`), versión, tipo de módulo ES (`"type": "module"`), scripts de ejecución (`dev`, `build`, `preview`) y dependencias dev (`svelte@^5.56.10`, `vite@^8.2.2`, `@sveltejs/vite-plugin-svelte@^7.3.0`).
- **Modelo de Negocio / Contexto General**: Garantiza la correcta versión de las librerías de interfaz gráfica y automatiza los comandos de compilación y ejecución del software.
- **Dependencias**:
  - **Depende de**: Administrador de paquetes `npm`.
  - **Utilizado por**: CLI de Vite y Node.js.

---

### 2. `frontend/vite.config.js`
- **Función Técnica Exacta**: Archivo de configuración del empaquetador Vite. Importa el plugin oficial `@sveltejs/vite-plugin-svelte` e integra el soporte para compilar archivos `.svelte` en módulos JavaScript ultrarápidos con Hot Module Replacement (HMR).
- **Modelo de Negocio / Contexto General**: Permite un desarrollo fluido en tiempo real y genera compilados de alta velocidad para el usuario final.
- **Dependencias**:
  - **Depende de**: `vite`, `@sveltejs/vite-plugin-svelte`.
  - **Utilizado por**: Servidor de desarrollo Vite y script de compilación.

---

### 3. `frontend/svelte.config.js`
- **Función Técnica Exacta**: Archivo de configuración del compilador Svelte. Integra el adaptador `vitePreprocess` para procesar estilos CSS y scripts dentro de los bloques `<style>` y `<script>` de los componentes.
- **Modelo de Negocio / Contexto General**: Asegura la correcta compilación de los componentes de la interfaz.
- **Dependencias**:
  - **Depende de**: `@sveltejs/vite-plugin-svelte`.
  - **Utilizado por**: Plugin de Svelte en Vite.

---

### 4. `frontend/jsconfig.json`
- **Función Técnica Exacta**: Archivo de configuración de JavaScript para el IDE (VS Code). Define el nivel de sintaxis objetivo (`ES2022`), la resolución de módulos Node y alias de rutas para autocompletado y tipado.
- **Modelo de Negocio / Contexto General**: Mejora la productividad del desarrollo y evita errores de importación en el código.
- **Dependencias**:
  - **Depende de**: VS Code / Servicio de lenguaje JavaScript.
  - **Utilizado por**: Editor de código.

---

### 5. `frontend/index.html`
- **Función Técnica Exacta**: Documento HTML5 primario de la Single Page Application (SPA). Define las etiquetas meta viewport, el título de la página ("AutoSentinel - MVP"), importa las fuentes de Google Fonts (*Plus Jakarta Sans*), incluye el `favicon.svg` y monta el script `/src/main.js` dentro del contenedor `<div id="app"></div>`.
- **Modelo de Negocio / Contexto General**: Estructura la experiencia inicial del usuario en el navegador y asegura la carga de la tipografía moderna del sistema de diseño.
- **Dependencias**:
  - **Depende de**: `public/favicon.svg`, Google Fonts CDN, `src/main.js`.
  - **Utilizado por**: Navegador web del usuario.

---

### 6. `frontend/src/main.js`
- **Función Técnica Exacta**: Punto de entrada ejecutable de JavaScript. Importa los estilos globales `app.css`, importa el componente principal `App.svelte` y utiliza la función `mount(App, { target: document.getElementById('app') })` de Svelte 5 para inicializar la aplicación.
- **Modelo de Negocio / Contexto General**: Arranca la ejecución de la interfaz gráfica en el navegador.
- **Dependencias**:
  - **Depende de**: `svelte` (`mount`), `src/app.css`, `src/App.svelte`.
  - **Utilizado por**: `index.html`.

---

### 7. `frontend/src/app.css`
- **Función Técnica Exacta**: Sistema de diseño CSS global. Define variables universales CSS (`:root`), paletas tailoring en HSL, tokens de colores de semáforo (`--score-verde`, `--score-amarillo`, `--score-rojo`), utilidades Glassmorphic (`.glass-card`), barras de desplazamiento personalizadas, estilos de botones (`.btn-primary`, `.btn-secondary`, `.btn-success`), insignias de score (`.badge-score`) y capas backdrop modales (`.modal-backdrop`).
- **Modelo de Negocio / Contexto General**: Provee una estética premium, moderna y vibrante (Glassmorphism con efectos traslúcidos y resplandores) que resalta las oportunidades de negocio en Verde/Amarillo/Rojo y otorga una apariencia profesional y de alto impacto visual.
- **Dependencias**:
  - **Depende de**: Ninguna externa (CSS Vanilla puro).
  - **Utilizado por**: `src/main.js` y todos los componentes Svelte (`App.svelte`, `Navbar.svelte`, `Dashboard.svelte`, Modales).

---

### 8. `frontend/src/App.svelte`
- **Función Técnica Exacta**: Componente raíz orquestador de estado de la SPA. Administra el ciclo de vida con `onMount`, polling periódico cada 10 segundos hacia `GET /api/stats`, carga de listado de vehículos `GET /api/vehicles`, filtros por score/búsqueda, control de modales (`isValidationModalOpen`, `isDetailModalOpen`, `isSettingsModalOpen`), invocación del robot centinela `POST /api/sentinel/run` e inicio de sesión de Facebook.
- **Modelo de Negocio / Contexto General**: Actúa como el cerebro de la interfaz de usuario, manteniendo sincronizada la pantalla con el estado real del servidor backend y coordinando los flujos de navegación entre modales y el panel principal.
- **Dependencias**:
  - **Depende de**: `src/lib/Navbar.svelte`, `src/lib/Dashboard.svelte`, `src/lib/MarketValidationModal.svelte`, `src/lib/MarketDetailModal.svelte`, `src/lib/SettingsModal.svelte`.
  - **Utilizado por**: `src/main.js`.

---

### 9. `frontend/src/lib/Navbar.svelte`
- **Función Técnica Exacta**: Barra de navegación superior fija (`position: sticky`). Muestra el estado del backend (`Backend Activo` / `Conectando...`), el indicador visual de sesión de Facebook (`🔒 Sesión FB Guardada` / `🔓 Sin Sesión FB`), botón de renovación de sesión, acceso a la modal de configuración y el botón disparador del centinela (`🔍 Escanear Marketplace`) con indicador de carga (*spinner*).
- **Modelo de Negocio / Contexto General**: Permite al usuario monitorear de un vistazo la salud del sistema, verificar la validez de sus credenciales de Facebook e iniciar rastreos activos de mercado con un solo clic.
- **Dependencias**:
  - **Depende de**: Svelte `createEventDispatcher`.
  - **Utilizado por**: `src/App.svelte`.

---

### 10. `frontend/src/lib/Dashboard.svelte`
- **Función Técnica Exacta**: Componente principal de panel de control. Presenta 4 tarjetas superiores de métricas (Total, Verdes, Amarillos, Rojos), barra de búsqueda en tiempo real, pestañas de filtrado rápido, modal de exportación a Google Sheets y la grilla adaptativa de vehículos (`.vehicles-grid`).
  - **Tarjetas de Vehículo**: Cada tarjeta cuenta con **2 pestañas internas directas** (`🇨🇱 Chileautos` y `🛒 Marketplace`) y un **botón flotante de borrado individual (`🗑️ card-delete-btn`)** en la esquina superior izquierda que brilla con resplandor rojo (*red glow*) al pasar el cursor y ejecuta `DELETE /api/vehicles/{id}`.
  - **Acciones**: Elimina la tarjeta individual del auto, abre la URL en Marketplace con `openMarketplaceUrl(vehicle.url)` (`window.open`), abre la validación con `triggerValidateMarket(vehicle)` y abre la modal de desglose estadístico al hacer clic en la casilla de la Mediana de Mercado.
- **Modelo de Negocio / Contexto General**: Es la vista de negocio principal donde el usuario evalúa los autos detectados, revisa costos duros (Impuesto 1.5%, Colchón), descarta tarjetas no deseadas individualmente y compara las medianas y márgenes en CLP de los dos mercados independientes (Chileautos vs Marketplace).
- **Dependencias**:
  - **Depende de**: Svelte `createEventDispatcher`.
  - **Utilizado por**: `src/App.svelte`.

---

### 11. `frontend/src/lib/MarketValidationModal.svelte`
- **Función Técnica Exacta**: Componente modal de validación de mercado automátizada. Permite editar/confirmar marca, modelo y año del vehículo y ejecuta `POST /api/vehicles/{id}/validate-market`. Muestra el estado de carga animado (*Escaneando Chileautos y Facebook Marketplace...*) y presenta los resultados estadísticos obtenidos en ambos mercados lado a lado en 2 columnas (`.dual-results-grid`).
- **Modelo de Negocio / Contexto General**: Permite al usuario solicitar la verificación en tiempo real del precio de un vehículo específico contra las publicaciones activas en Chileautos y Facebook Marketplace.
- **Dependencias**:
  - **Depende de**: Svelte `createEventDispatcher`.
  - **Utilizado por**: `src/App.svelte`.

---

### 12. `frontend/src/lib/MarketDetailModal.svelte`
- **Función Técnica Exacta**: Componente modal desplegable para el análisis detallado de muestras. Muestra las 5 métricas estadísticas fundamentales extraídas de la muestra de mercado del vehículo:
  1. 📑 **Muestra Rescatada** (cantidad de publicaciones analizadas).
  2. 🧮 **Promedio de la Muestra**.
  3. 📉 **Precio Más Bajo (Mínimo)**.
  4. 📈 **Precio Más Alto (Máximo)**.
  5. ⚖️ **Mediana Calculada** (destacada en Verde).
- **Modelo de Negocio / Contexto General**: Otorga al usuario transparencia matemática absoluta sobre cómo se calculó la mediana de mercado, permitiéndole verificar el rango de precios en el que se mueve la competencia antes de realizar una oferta de compra.
- **Dependencias**:
  - **Depende de**: Svelte `createEventDispatcher`.
  - **Utilizado por**: `src/App.svelte` (disparado desde `Dashboard.svelte`).

---

### 13. `frontend/src/lib/SettingsModal.svelte`
- **Función Técnica Exacta**: Componente modal de configuración global. Incluye un encabezado con un ícono de información `ℹ️` y tooltip que explica los parámetros fijados del negocio. Permite consultar (`GET /api/config`) y actualizar (`PUT /api/config`) los presupuestos mín/máx, frecuencia de scraping, colchón e impuestos. Además, incluye la sección de **"Mantenimiento & Purga de Datos"** con el botón **"Borrar todos los datos"**, el cual despliega un cuadro de diálogo de confirmación (*"estas a punto de borrar toda la informacion recopilada por los scrappers"*) con opciones de *"Aceptar"* y *"Cancelar"* para ejecutar la eliminación masiva (`DELETE /api/vehicles`).
- **Modelo de Negocio / Contexto General**: Permite al usuario ajustar sus parámetros financieros y limpiar de forma periódica la base de datos para evitar acumulación excesiva de publicaciones obsoletas y mantener la máxima fluidez en el software.
- **Dependencias**:
  - **Depende de**: Svelte `createEventDispatcher`, `onMount`.
  - **Utilizado por**: `src/App.svelte`.

---

### 14. `frontend/src/lib/Counter.svelte`
- **Función Técnica Exacta**: Componente de ejemplo básico que demuestra la sintaxis de runes de Svelte 5 (`let count = $state(0)`).
- **Modelo de Negocio / Contexto General**: Componente utilitario/demostrativo de pruebas sintácticas de Svelte.
- **Dependencias**:
  - **Depende de**: Svelte 5.
  - **Utilizado por**: No integrado en el flujo principal (componente standalone).

---

### 15. `frontend/public/favicon.svg` & `public/icons.svg`
- **Función Técnica Exacta**: Archivos de gráficos vectoriales (SVG) que definen el icono oficial de la aplicación para navegadores e íconos del sistema.
- **Modelo de Negocio / Contexto General**: Mantener la consistencia visual y de marca en la pestaña del navegador web.
- **Dependencias**: Ninguna.
- **Utilizado por**: `index.html`.

---

### 16. `frontend/src/assets/hero.png`, `svelte.svg`, `vite.svg`
- **Función Técnica Exacta**: Recursos gráficos de apoyo estático.
- **Modelo de Negocio / Contexto General**: Elementos de soporte visual para branding y desarrollo.
- **Dependencias**: Ninguna.
- **Utilizado por**: Vite / Componentes.

---

## 📊 Tabla Resumen de Dependencias Inter-Componentes (Frontend)

| Componente / Archivo | Archivos de los que Depende | Componentes que Dependen de Él |
| :--- | :--- | :--- |
| `main.js` | `index.html`, `app.css`, `App.svelte` | `index.html` (Punto de entrada) |
| `app.css` | Ninguno (CSS puro) | `main.js`, `App.svelte`, todos los componentes `.svelte` |
| `App.svelte` | `Navbar.svelte`, `Dashboard.svelte`, `MarketValidationModal.svelte`, `MarketDetailModal.svelte`, `SettingsModal.svelte` | `main.js` |
| `Navbar.svelte` | `app.css` | `App.svelte` |
| `Dashboard.svelte` | `app.css` | `App.svelte` (dispara `openValidateModal`, `openMarketDetail`, `filterChange`) |
| `MarketValidationModal.svelte` | `app.css` | `App.svelte` |
| `MarketDetailModal.svelte` | `app.css` | `App.svelte` (disparado desde `Dashboard.svelte`) |
| `SettingsModal.svelte` | `app.css` | `App.svelte` |
| `Counter.svelte` | Svelte 5 | Ninguno (Componente de prueba) |
| `vite.config.js` | `package.json` | Servidor Vite / Pipeline de build |
| `svelte.config.js` | `package.json` | Compilador Svelte |
