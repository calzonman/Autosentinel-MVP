# 🚗 AutoSentinel MVP - Sistema de Análisis, Detección de Oportunidades Automotrices y Arbitraje Financiero

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Svelte](https://img.shields.io/badge/Svelte-5.0+-FF3E00?style=for-the-badge&logo=svelte&logoColor=white)](https://svelte.dev/)
[![Vite](https://img.shields.io/badge/Vite-8.0+-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Playwright](https://img.shields.io/badge/Playwright-Automated-45BA4B?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

Plataforma integral de software para la **búsqueda automatizada, evaluación financiera, filtrado de riesgo comercial y comparación dual de mercado (Facebook Marketplace vs Chileautos)** de vehículos usables en Chile.

Diseñada para inversionistas y revendedores automotrices, esta herramienta automatiza la detección de oportunidades con márgenes de ganancia reales calculados en tiempo real.

---

## 📌 Índice
- [Características Principales](#-características-principales)
- [Arquitectura del Proyecto](#-arquitectura-del-proyecto)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Requisitos Previos](#-requisitos-previos)
- [Guía de Instalación y Configuración](#-guía-de-instalación-y-configuración)
- [Seguridad y Credenciales](#-seguridad-y-credenciales)
- [Documentación Detallada](#-documentación-detallada)

---

## 🔥 Características Principales

1. **🤖 Centinela de Scraping Automatizado (Facebook Marketplace):**
   - Rastreos continuos en segundo plano usando Playwright (Chromium Headless).
   - Persistencia de sesión y cookies activas de Facebook para evitar bloqueos.
   - Programador de ejecuciones dinámicas (APScheduler) configurable por horas.

2. **🛡️ Motor de Filtrado de Riesgo Comercial ("Trash Filter"):**
   - Descarte automático de precios engañosos/anzuelo ($1, $123, $999.999).
   - Filtro sintáctico de vehículos con alto riesgo legal o técnico (prenda, embargo, sin padrón, chocado, desarme, motor malo).

3. **📊 Validador Dual de Mercado (Chileautos vs Marketplace):**
   - Micro-scrapers en tiempo real que consultan medianas de precio, mínimos, máximos y muestras estadísticas tanto en Chileautos como en Facebook Marketplace para un vehículo seleccionado.

4. **💰 Calculadora Financiera y Semáforo de Rentabilidad:**
   - Descuento automático de Impuesto de Transferencia (1.5% del valor real).
   - Colchón mecánico de mantenimiento/reparación personalizable.
   - Clasificación en Semáforo:
     - 🟢 **VERDE:** Margen estimado $\ge 30\%$
     - 🟡 **AMARILLO:** Margen estimado entre $15\%$ y $30\%$
     - 🔴 **ROJO:** Margen estimado $< 15\%$

5. **🎨 Interfaz Dashboard Svelte 5 (Glassmorphism UI):**
   - Panel reactivo de oportunidades con métricas globales, búsqueda en vivo, filtros por semáforo, modales de validación estadística y modal de configuraciones generales.

6. **📊 Exportación Remota a Google Sheets:**
   - Integración nativa mediante Google Service Account para exportar vehículos aprobados a hojas de cálculo compartidas.

---

## 📂 Arquitectura del Proyecto

```text
app pancho/
├── backend/                  # Servidor REST FastAPI, Scrapers Playwright y Base de Datos
│   ├── calculator/           # Motor de cálculo financiero y semáforo
│   ├── export/               # Integración remota con Google Sheets API
│   ├── filters/              # Motor de filtrado de descarte y riesgo
│   ├── scrapers/             # Scrapers (Centinela Marketplace, Micro Chileautos, Auth)
│   ├── auth.json.example     # Plantilla de ejemplo para credenciales de Facebook
│   ├── service_account.json.example # Plantilla de ejemplo para Google Service Account
│   ├── database.py           # Conexión SQLAlchemy y migración SQLite
│   ├── main.py               # Servidor FastAPI principal y endpoints REST
│   ├── models.py             # Modelos ORM (Vehicle, SentinelConfig, FilterKeyword)
│   └── requirements.txt      # Dependencias Python
│
├── frontend/                 # Aplicación Cliente SPA en Svelte 5 + Vite
│   ├── public/               # Recursos estáticos y favicons
│   ├── src/
│   │   ├── assets/           # Imágenes e isotipos
│   │   ├── lib/              # Componentes Svelte (Dashboard, Navbar, Modales)
│   │   ├── app.css           # Design System Glassmorphism global
│   │   ├── App.svelte        # Orquestador principal de estado UI
│   │   └── main.js           # Punto de entrada JavaScript
│   ├── package.json          # Dependencias Node.js (Svelte 5, Vite 8)
│   └── vite.config.js        # Configuración de empaquetado Vite
│
├── .gitignore                # Reglas de exclusión de archivos sensibles y builds
├── ARQUITECTURA_BACKEND.MD   # Documentación técnica completa del Backend
├── ARQUITECTURA_FRONTEND.MD  # Documentación técnica completa del Frontend
└── README.md                 # Este archivo
```

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **Lenguaje:** Python 3.13+
- **Framework Web:** FastAPI + Uvicorn
- **Scraping & Automatización:** Playwright (Python async/sync)
- **Base de Datos & ORM:** SQLite + SQLAlchemy (con auto-migración de esquemas)
- **Tareas Programadas:** APScheduler (AsyncIOScheduler)
- **Exportación:** Google Sheets API (`gspread`)

### Frontend
- **Framework UI:** Svelte 5 (con Runes y reactividad avanzada)
- **Empaquetador & Dev Server:** Vite 8
- **Estilos & Diseño:** CSS3 Nativo con variables HSL, Glassmorphism y Flexbox/Grid

---

## 📋 Requisitos Previos

Asegúrate de contar con los siguientes elementos instalados antes de iniciar:

1. **Python 3.13+** (con `pip` habilitado).
2. **Node.js 18+** y `npm`.
3. **Google Chrome / Chromium** (Playwright lo instalará automáticamente).

---

## 🚀 Guía de Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/tu-repositorio.git
cd "app pancho"
```

---

### 2. Configurar el Backend (`backend/`)

1. Navega a la carpeta del backend:
   ```bash
   cd backend
   ```
2. Crea e inicializa un entorno virtual de Python:
   ```bash
   python -m venv venv
   # En Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # En Linux/macOS:
   source venv/bin/activate
   ```
3. Instala las dependencias de Python:
   ```bash
   pip install -r requirements.txt
   ```
4. Instala los navegadores necesarios para Playwright:
   ```bash
   playwright install chromium
   ```
5. Poblar la base de datos con datos de demostración iniciales (opcional):
   ```bash
   python seed_data.py
   ```
6. Iniciar el servidor FastAPI:
   ```bash
   python main.py
   # O alternativamente:
   uvicorn main:app --reload --port 8000
   ```
   El backend estará disponible en `http://127.0.0.1:8000`.

---

### 3. Configurar el Frontend (`frontend/`)

1. Abre una nueva terminal y navega a la carpeta frontend:
   ```bash
   cd frontend
   ```
2. Instala las dependencias de Node.js:
   ```bash
   npm install
   ```
3. Inicia el servidor de desarrollo de Vite:
   ```bash
   npm run dev
   ```
4. Abre tu navegador e ingresa a `http://localhost:5173`.

---

## 🔒 Seguridad y Credenciales

Este proyecto maneja autenticación local para scraping en Facebook Marketplace y exportación remota a Google Sheets.

> [!CAUTION]
> **NUNCA subas archivos de credenciales reales a GitHub.** El archivo `.gitignore` raíz ya está configurado para excluir automáticamente archivos sensibles.

- **Autenticación en Facebook:** El backend abrirá una ventana interactiva de navegador cuando presiones "Capturar Sesión Facebook" en los ajustes para generar `backend/auth.json`. Puedes guiarte en [auth.json.example](file:///c:/Users/nicov/OneDrive/Escritorio/app%20pancho/backend/auth.json.example).
- **Google Sheets API:** Para exportar a Google Sheets, sube tu archivo `service_account.json` desde la pestaña de configuración de la app. Puedes guiarte en [service_account.json.example](file:///c:/Users/nicov/OneDrive/Escritorio/app%20pancho/backend/service_account.json.example).

---

## 📖 Documentación Detallada

Para comprender la arquitectura completa, modelos de datos, endpoints REST y componentes en profundidad, consulta los siguientes manuales:

- 📘 [Documentación del Backend (backend/README.md)](file:///c:/Users/nicov/OneDrive/Escritorio/app%20pancho/backend/README.md)
- 📙 [Documentación del Frontend (frontend/README.md)](file:///c:/Users/nicov/OneDrive/Escritorio/app%20pancho/frontend/README.md)
- 📗 [Especificación Técnica de Arquitectura Backend](file:///c:/Users/nicov/OneDrive/Escritorio/app%20pancho/ARQUITECTURA_BACKEND.MD)
- 📕 [Especificación Técnica de Arquitectura Frontend](file:///c:/Users/nicov/OneDrive/Escritorio/app%20pancho/ARQUITECTURA_FRONTEND.MD)

---

## 📄 Licencia

Este proyecto es software privado desarrollado para uso de evaluación y arbitraje automotriz. Todos los derechos reservados.
