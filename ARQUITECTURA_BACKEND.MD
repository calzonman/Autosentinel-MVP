# Arquitectura del Backend - Documentación Técnica y de Negocio

Este documento contiene la especificación detallada de la arquitectura del servidor backend del software de **Detección, Evaluación Financiera y Arbitraje Automotriz (AutoSentinel MVP)**.

---

## 📂 Árbol de Directorios del Backend (`backend/`)

```text
backend/
├── calculator/
│   └── financial.py            # Motor de cálculo financiero y semáforo de rentabilidad
├── export/
│   └── google_sheets.py        # Módulo de exportación remota a Google Sheets API
├── filters/
│   └── cleaner.py              # Motor de filtrado de riesgo comercial, legal y precios engañosos
├── scrapers/
│   ├── auth_helper.py          # Helper de autenticación y captura de cookies de Facebook (auth.json)
│   ├── chileautos_micro.py     # Micro-scraper de validación de mercado en Chileautos
│   ├── marketplace_micro.py   # Micro-scraper de validación de mercado en Facebook Marketplace (filtro estricto)
│   └── marketplace_sentinel.py # Engine Centinela para escaneo masivo de publicaciones en Marketplace
├── auth.json                   # Archivo JSON de persistencia de sesión y cookies de Facebook
├── automotive_mvp.db           # Base de datos SQLite del sistema
├── chileautos_sample.html      # Muestra local HTML de prueba de Chileautos
├── clear_db.py                 # Script utilitario de limpieza completa de base de datos
├── database.py                 # Configuración de SQLAlchemy e inicialización con auto-migración SQLite
├── main.py                     # Servidor FastAPI principal, scheduler y endpoints de la API REST
├── models.py                   # Modelos ORM (Vehicle, SentinelConfig, FilterKeyword)
├── requirements.txt            # Especificación de dependencias Python del proyecto
├── seed_data.py                # Script de poblamiento de datos demostrativos iniciales
├── test_chileautos.py          # Script de prueba e inspección de Chileautos
└── test_exact_chileautos.py    # Script de prueba con coincidencia exacta para Chileautos
```

---

## 🏛️ Documentación de Directorios (Backend)

### 📁 `backend/`
- **Función Técnica Exacta**: Directorio raíz que aloja el servidor backend en Python, los modelos de datos de SQLAlchemy, el motor de scraping con Playwright, los algoritmos financieros, los filtros de riesgo y las pruebas de integración.
- **Modelo de Negocio / Contexto General**: Constituye el núcleo operativo del negocio. Ejecuta la búsqueda pasiva y activa de oportunidades automotrices en Chile, evalúa costos ocultos (transferencia 1.5%, colchón mecánico), compara contra medianas de mercado en tiempo real y expone las oportunidades filtradas a la interfaz de usuario.
- **Dependencias**:
  - **Depende de**: Python 3.13, Playwright Chromium, FastAPI, SQLAlchemy, SQLite, Google Sheets API (`gspread`).
  - **Utilizado por**: Frontend Svelte (`frontend/`), que consume sus endpoints REST HTTP en `http://127.0.0.1:8000`.

---

### 📁 `backend/calculator/`
- **Función Técnica Exacta**: Módulo aislado para la lógica matemática y algoritmos de evaluación de viabilidad económica.
- **Modelo de Negocio / Contexto General**: Aplica las reglas financieras de arbitraje (Impuesto de Transferencia del 1.5%, Colchón Mecánico configurable y margen de ganancia en $ CLP), clasificando la oportunidad en semáforo comercial (Verde $\ge 30\%$, Amarillo $15-30\%$, Rojo $<15\%$).
- **Dependencias**:
  - **Depende de**: Biblioteca estándar de Python.
  - **Utilizado por**: `backend/main.py`, `backend/scrapers/marketplace_sentinel.py`, `backend/seed_data.py`.

---

### 📁 `backend/export/`
- **Función Técnica Exacta**: Módulo de integración externa para el envío persistente de datos a servicios de hojas de cálculo mediante API.
- **Modelo de Negocio / Contexto General**: Permite la exportación del listado de vehículos aprobados a Google Sheets para su posterior revisión por equipos de venta, inversionistas o administradores fuera de la plataforma.
- **Dependencias**:
  - **Depende de**: `gspread`, `sqlalchemy.orm`, `backend/database.py`, `backend/models.py`, `service_account.json`.
  - **Utilizado por**: Endpoint `POST /api/export-sheets` en `backend/main.py`.

---

### 📁 `backend/filters/`
- **Función Técnica Exacta**: Módulo de filtrado sintáctico mediante expresiones regulares y validación de rangos numéricos.
- **Modelo de Negocio / Contexto General**: Actúa como filtro de calidad ("trash filter"). Descarta publicaciones con precios anzuelo/engañosos ($1, $123, $999.999) y vehículos con alto riesgo legal o técnico (prenda, embargo, sin padrón, chocado, desarme, motor malo).
- **Dependencias**:
  - **Depende de**: Módulo `re` de Python.
  - **Utilizado por**: `backend/scrapers/marketplace_sentinel.py`.

---

### 📁 `backend/scrapers/`
- **Función Técnica Exacta**: Módulo de automatización de navegadores web utilizando Playwright (sincrónico y asincrónico) para la extracción automatizada de datos de Facebook Marketplace y Chileautos.
- **Modelo de Negocio / Contexto General**: Provee la materia prima del sistema: extrae avisos en vivo, captura precios publicados, imágenes, ubicaciones y realiza las búsquedas de mercado para calcular medianas de comparación.
- **Dependencias**:
  - **Depende de**: `playwright`, `numpy`, `sqlalchemy`, `backend/scrapers/auth_helper.py`, `backend/auth.json`.
  - **Utilizado por**: `backend/main.py`.

---

## 📄 Documentación Detallada de Archivos (Backend)

### 1. `backend/database.py`
- **Función Técnica Exacta**: Configura la conexión SQLAlchemy ORM a la base de datos SQLite (`automotive_mvp.db`). Define `engine`, `SessionLocal`, `Base`, el generador de sesiones `get_db()` y la función `init_db()` que incluye un mecanismo de **migración automática de esquema** ejecutando sentencias `PRAGMA table_info` y `ALTER TABLE` si se añaden nuevas columnas.
- **Modelo de Negocio / Contexto General**: Garantiza la persistencia relacional de la información de vehículos, configuraciones y palabras clave, manteniendo la compatibilidad de datos cuando la aplicación evoluciona sin destruir la información histórica.
- **Dependencias**:
  - **Depende de**: `sqlalchemy`, `sqlite3`, `os`.
  - **Utilizado por**: `backend/main.py`, `backend/models.py`, `backend/export/google_sheets.py`, `backend/scrapers/marketplace_sentinel.py`, `backend/clear_db.py`, `backend/seed_data.py`.

---

### 2. `backend/models.py`
- **Función Técnica Exacta**: Define las clases de modelos relacionales de SQLAlchemy:
  - `Vehicle`: Almacena información técnica del auto, precio publicado, imágenes, URL, scores independientes para Chileautos (`score_chileautos`, `estimated_market_price_chileautos`, `transfer_tax_chileautos`, `margin_chileautos`, `samples_count_chileautos`, `min_price_chileautos`, `max_price_chileautos`, `avg_price_chileautos`) y para Facebook Marketplace (`score_mp`, `estimated_market_price_mp`, etc.).
  - `SentinelConfig`: Almacena parámetros globales de escaneo (presupuestos mín/máx, colchón mecánico por defecto, porcentaje de transferencia, ubicaciones e intervalo de ejecución).
  - `FilterKeyword`: Almacena palabras clave personalizadas de descarte (prenda, embargo, choque, etc.).
- **Modelo de Negocio / Contexto General**: Estructura la representación de datos del negocio para permitir la evaluación dual de mercado (Chileautos vs Marketplace), la segmentación de vehículos por nivel de rentabilidad y el control dinámico del robot centinela.
- **Dependencias**:
  - **Depende de**: `sqlalchemy`, `backend/database.py`.
  - **Utilizado por**: `backend/main.py`, `backend/scrapers/marketplace_sentinel.py`, `backend/export/google_sheets.py`, `backend/clear_db.py`, `backend/seed_data.py`.

---

### 3. `backend/main.py`
- **Función Técnica Exacta**: Punto de entrada de la aplicación FastAPI. Define el middleware CORS, inicializa la base de datos, administra el programador en segundo plano `AsyncIOScheduler` (para escaneos automáticos cada $N$ horas) y expone los siguientes endpoints HTTP REST:
  - `GET /api/health`
  - `GET /api/stats`
  - `GET /api/vehicles` y `GET /api/vehicles/{id}`
  - `DELETE /api/vehicles/{id}` (elimina un vehículo específico por ID) y `DELETE /api/vehicles` (purga completa de la base de datos de vehículos recopilados)
  - `POST /api/vehicles/{id}/validate-market` (ejecuta micro-scrapers de Chileautos y Marketplace en paralelo/hilos dedicados)
  - `POST /api/vehicles/{id}/recalculate`
  - `POST /api/sentinel/run`
  - `GET /api/config` y `PUT /api/config` (fija `search_query='autos'` y `locations='Valparaíso, Región Metropolitana'`, reprograma dinámicamente la frecuencia del `scheduler` y ejecuta un **recálculo masivo automático** de los impuestos de transferencia, márgenes en $ CLP y Scores de todos los vehículos almacenados)
  - `POST /api/auth/facebook` y `GET /api/auth/facebook/status`
  - `POST /api/auth/google-sheets/credentials` y `POST /api/export-sheets`
- **Modelo de Negocio / Contexto General**: Orquesta todas las funcionalidades del software, conectando la interfaz de usuario con los scrapers, el motor de cálculo financiero, la base de datos y la exportación de resultados.
- **Dependencias**:
  - **Depende de**: `fastapi`, `uvicorn`, `apscheduler`, `sqlalchemy.orm`, `backend/database.py`, `backend/models.py`, `backend/calculator/financial.py`, `backend/scrapers/chileautos_micro.py`, `backend/scrapers/marketplace_micro.py`, `backend/scrapers/marketplace_sentinel.py`, `backend/scrapers/auth_helper.py`, `backend/export/google_sheets.py`.
  - **Utilizado por**: Frontend Svelte (`frontend/src/App.svelte`, `Dashboard.svelte`, `MarketValidationModal.svelte`, `SettingsModal.svelte`).

---

### 4. `backend/calculator/financial.py`
- **Función Técnica Exacta**: Contiene la función `calculate_financial_score(published_price, estimated_market_price, mechanical_cushion, transfer_tax_percent)`. Calcula el costo total de adquisición (precio publicado + impuesto transferencia 1.5% + colchón mecánico), determina el margen neto ($ CLP), calcula el % de margen sobre costo total y asigna el Score de Semáforo:
  - **VERDE**: Margen $\% \ge 30\%$
  - **AMARILLO**: $15\% \le$ Margen $\% < 30\%$
  - **ROJO**: Margen $\% < 15\%$
- **Modelo de Negocio / Contexto General**: Implementa la lógica de discriminación económica que permite detectar oportunidades reales de compra para revender con margen asegurado en el mercado chileno.
- **Dependencias**:
  - **Depende de**: Ninguna biblioteca externa.
  - **Utilizado por**: `backend/main.py`, `backend/scrapers/marketplace_sentinel.py`, `backend/seed_data.py`.

---

### 5. `backend/filters/cleaner.py`
- **Función Técnica Exacta**: Provee las funciones `validate_price`, `validate_text` e `is_valid_listing`. Utiliza expresiones regulares para identificar patrones de palabras de riesgo (`DEFAULT_RISK_KEYWORDS`) e identifica precios engañosos (`DUMMY_PRICES`).
- **Modelo de Negocio / Contexto General**: Evita que el sistema almacene o evalúe publicaciones que sean estafas, precios anzuelo o vehículos con problemas legales/mecánicos graves que impidan una reventa comercial limpia.
- **Dependencias**:
  - **Depende de**: Módulo nativo `re`.
  - **Utilizado por**: `backend/scrapers/marketplace_sentinel.py`.

---

### 6. `backend/scrapers/auth_helper.py`
- **Función Técnica Exacta**: Expone las funciones `login_and_save_session()` e `is_session_saved()`. Abre una ventana de navegador Chromium visible (`headless=False`) mediante Playwright para que el usuario inicie sesión manualmente en Facebook. Al detectar cookies clave (`c_user`, `xs`), captura el `storage_state` y lo guarda en `backend/auth.json`.
- **Modelo de Negocio / Contexto General**: Permite sortear las restricciones de acceso a Facebook Marketplace mediante la reutilización segura de la sesión real del usuario, evitando bloqueos por uso de bots sin sesión.
- **Dependencias**:
  - **Depende de**: `playwright.async_api`, `os`, `sys`, `asyncio`, `time`.
  - **Utilizado por**: Endpoint `POST /api/auth/facebook` en `backend/main.py`, `backend/scrapers/marketplace_sentinel.py`, `backend/scrapers/marketplace_micro.py`.

---

### 7. `backend/scrapers/marketplace_sentinel.py`
- **Función Técnica Exacta**: Implementa `run_marketplace_sentinel_sync()` y su wrapper asíncrono `run_marketplace_sentinel()`. Incluye el helper `extract_clean_title()` para ignorar insignias de estado de Facebook (`"Recién publicado"`, `"Nuevo"`, `"Patrocinado"`), extrae títulos reales, precios, imágenes e hipervínculos, aplica `is_valid_listing()` y registra nuevos vehículos en la base de datos con su score inicial.
- **Modelo de Negocio / Contexto General**: Es el robot rastreador pasivo principal que busca oportunidades de autos publicados recientemente en la zona central de Chile (Valparaíso / Región Metropolitana).
- **Dependencias**:
  - **Depende de**: `playwright.sync_api`, `sqlalchemy.orm`, `backend/database.py`, `backend/models.py`, `backend/filters/cleaner.py`, `backend/calculator/financial.py`, `backend/scrapers/auth_helper.py`.
  - **Utilizado por**: `backend/main.py` (ejecutado bajo demanda o mediante la tarea programada `AsyncIOScheduler`).

---

### 8. `backend/scrapers/chileautos_micro.py`
- **Función Técnica Exacta**: Implementa `get_chileautos_market_median_sync()` y `get_chileautos_market_median()`. Construye la URL de búsqueda exacta con codificación `%20` (ej: `q=CarAll.keyword%28chevrolet%20spark%202019%29.`), abre un navegador Chromium, espera la estabilización contra DataDome, analiza tarjetas `a[href*='/vehiculos/detalles/']`, extrae precios reales y calcula la mediana, mínimo, máximo, promedio y conteo de muestra utilizando `numpy`.
- **Modelo de Negocio / Contexto General**: Provee la referencia de precio del mercado formal chileno (Chileautos) para comparar el precio de compra contra el valor real de mercado.
- **Dependencias**:
  - **Depende de**: `playwright.sync_api`, `numpy`, `re`, `urllib.parse`, `asyncio`.
  - **Utilizado por**: Endpoint `POST /api/vehicles/{id}/validate-market` en `backend/main.py`.

---

### 9. `backend/scrapers/marketplace_micro.py`
- **Función Técnica Exacta**: Implementa `get_marketplace_market_median_sync()` y `get_marketplace_market_median()`. Emplea `extract_clean_title()` para omitir etiquetas de estado, abre un navegador visible en Facebook Marketplace, realiza búsquedas por término y aplica un **Filtro Estricto por Nombre** exigiendo que el título de la publicación contenga todas las palabras clave del vehículo analizado (ej: `chevrolet`, `spark`, `2016`). Extrae precios y calcula la mediana, mínimo, máximo, promedio y conteo de muestra usando `numpy`.
- **Modelo de Negocio / Contexto General**: Provee la referencia de precio del mercado informal/C2C (Facebook Marketplace) con filtro anti-ruido para obtener una comparación exacta de mercado independiente de Chileautos.
- **Dependencias**:
  - **Depende de**: `playwright.sync_api`, `numpy`, `re`, `urllib.parse`, `asyncio`, `backend/scrapers/auth_helper.py`.
  - **Utilizado por**: Endpoint `POST /api/vehicles/{id}/validate-market` en `backend/main.py`.

---

### 10. `backend/export/google_sheets.py`
- **Función Técnica Exacta**: Implementa `export_vehicles_to_google_sheets(spreadsheet_id, vehicle_ids)`. Lee las credenciales de la Service Account de Google (`service_account.json`), conecta a Google Sheets con `gspread`, verifica o inserta encabezados, inyecta las filas con los detalles financieros del vehículo y marca los registros en la base de datos como `exported_to_sheets = True`.
- **Modelo de Negocio / Contexto General**: Facilita la salida de datos del sistema hacia flujos de trabajo externos o planillas compartidas con el equipo de trabajo.
- **Dependencias**:
  - **Depende de**: `gspread`, `sqlalchemy.orm`, `backend/database.py`, `backend/models.py`, `service_account.json`.
  - **Utilizado por**: Endpoint `POST /api/export-sheets` en `backend/main.py`.

---

### 11. `backend/clear_db.py`
- **Función Técnica Exacta**: Script ejecutable de mantenimiento que elimina todos los registros de la tabla `vehicles` y resetea las fechas de ejecución en `sentinel_config`.
- **Modelo de Negocio / Contexto General**: Permite vaciar la base de datos para realizar pruebas limpias, demostraciones o reiniciar el rastreo desde cero.
- **Dependencias**:
  - **Depende de**: `backend/database.py`, `backend/models.py`.
  - **Utilizado por**: Ejecución manual por el desarrollador/administrador desde terminal.

---

### 12. `backend/seed_data.py`
- **Función Técnica Exacta**: Script ejecutable que inicializa la base de datos, asegura la existencia de `SentinelConfig`, inserta las palabras clave por defecto (`FilterKeyword`) e inserta vehículos de prueba demostrativos con cálculo financiero inicial.
- **Modelo de Negocio / Contexto General**: Provee datos iniciales para la presentación o pruebas inmediatas de la interfaz gráfica sin requerir un escaneo previo.
- **Dependencias**:
  - **Depende de**: `backend/database.py`, `backend/models.py`, `backend/calculator/financial.py`.
  - **Utilizado por**: Ejecución manual por el desarrollador/administrador desde terminal.

---

### 13. `backend/test_chileautos.py` & `backend/test_exact_chileautos.py`
- **Función Técnica Exacta**: Scripts de prueba independientes para validar la extracción de Selectores CSS, comportamientos de scroll y regex de precios directamente en Chileautos.
- **Modelo de Negocio / Contexto General**: Herramientas de diagnóstico técnico para verificar la estabilidad de los scrapers frente a cambios en la estructura web de Chileautos.
- **Dependencias**:
  - **Depende de**: `playwright.sync_api`, `numpy`, `re`, `urllib.parse`.
  - **Utilizado por**: Pruebas manuales de desarrollo.

---

### 14. `backend/requirements.txt`
- **Función Técnica Exacta**: Archivo de texto plano con la lista de librerías y versiones de Python necesarias para el entorno virtual (`fastapi`, `uvicorn`, `playwright`, `sqlalchemy`, `apscheduler`, `gspread`, `pandas`, `numpy`, `pydantic`, `httpx`, `python-multipart`).
- **Modelo de Negocio / Contexto General**: Garantiza la reproducibilidad e instalación del proyecto en cualquier entorno de despliegue o máquina de desarrollo.
- **Dependencias**:
  - **Depende de**: Gestor de paquetes `pip`.
  - **Utilizado por**: Entorno virtual de Python (`venv`).

---

### 15. `backend/auth.json`
- **Función Técnica Exacta**: Archivo JSON generado automáticamente por Playwright que contiene la sesión guardada, cookies de autenticación (`c_user`, `xs`), tokens local storage y contexto de Facebook.
- **Modelo de Negocio / Contexto General**: Almacena las credenciales activas para permitir que los scrapers naveguen en Facebook Marketplace autenticados como usuario real.
- **Dependencias**:
  - **Depende de**: Generado por `backend/scrapers/auth_helper.py`.
  - **Utilizado por**: `backend/scrapers/marketplace_sentinel.py`, `backend/scrapers/marketplace_micro.py`, `backend/main.py`.

---

### 16. `backend/automotive_mvp.db`
- **Función Técnica Exacta**: Base de datos SQLite relacional del sistema que almacena las tablas `vehicles`, `sentinel_config` y `filter_keywords`.
- **Modelo de Negocio / Contexto General**: Almacenamiento local liviano y persistente de todas las oportunidades detectadas y configuraciones de la plataforma.
- **Dependencias**:
  - **Depende de**: Administrada por `backend/database.py` y `backend/models.py`.
  - **Utilizado por**: Todo el backend.

---

### 17. `backend/chileautos_sample.html`
- **Función Técnica Exacta**: Archivo HTML estático guardado localmente de la estructura del DOM de Chileautos.
- **Modelo de Negocio / Contexto General**: Utilizado para realizar pruebas offline de parsing de tarjetas de vehículos.
- **Dependencias**:
  - **Depende de**: Ninguna.
  - **Utilizado por**: Inspección manual durante desarrollo.

---

## 📊 Tabla Resumen de Dependencias Mapeadas (Backend)

| Módulo / Archivo | Archivos de los que Depende | Archivos que Dependen de Él |
| :--- | :--- | :--- |
| `database.py` | `automotive_mvp.db` | `models.py`, `main.py`, `google_sheets.py`, `marketplace_sentinel.py`, `clear_db.py`, `seed_data.py` |
| `models.py` | `database.py` | `main.py`, `google_sheets.py`, `marketplace_sentinel.py`, `clear_db.py`, `seed_data.py` |
| `main.py` | `database.py`, `models.py`, `financial.py`, `chileautos_micro.py`, `marketplace_micro.py`, `marketplace_sentinel.py`, `auth_helper.py`, `google_sheets.py` | `Frontend Svelte` (Endpoints REST HTTP) |
| `calculator/financial.py` | Ninguna | `main.py`, `marketplace_sentinel.py`, `seed_data.py` |
| `filters/cleaner.py` | Ninguna | `marketplace_sentinel.py` |
| `scrapers/auth_helper.py` | `auth.json` | `main.py`, `marketplace_sentinel.py`, `marketplace_micro.py` |
| `scrapers/marketplace_sentinel.py` | `database.py`, `models.py`, `cleaner.py`, `financial.py`, `auth_helper.py`, `auth.json` | `main.py` |
| `scrapers/chileautos_micro.py` | Ninguna interna | `main.py` |
| `scrapers/marketplace_micro.py` | `auth_helper.py`, `auth.json` | `main.py` |
| `export/google_sheets.py` | `database.py`, `models.py`, `service_account.json` | `main.py` |
| `clear_db.py` | `database.py`, `models.py` | Ejecución manual |
| `seed_data.py` | `database.py`, `models.py`, `financial.py` | Ejecución manual |
