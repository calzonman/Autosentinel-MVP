<script>
  /**
   * Componente Modal de Configuración Global del Sistema (SettingsModal.svelte)
   * 
   * Permite gestionar los parámetros del robot centinela, la calculadora financiera,
   * la sesión autenticada de Facebook Marketplace y las credenciales de Google Sheets.
   * 
   * @property {boolean} isOpen - Estado de visibilidad de la ventana modal.
   */
  import { createEventDispatcher, onMount } from 'svelte';
  export let isOpen = false;

  const dispatch = createEventDispatcher();

  // Valores Fijos del Proyecto (Objetivo del Software: Autos recién publicados en Valparaíso y Santiago)
  const FIXED_SEARCH_QUERY = 'autos';
  const FIXED_LOCATIONS = 'Valparaíso, Región Metropolitana';

  let searchQuery = FIXED_SEARCH_QUERY;
  let minBudget = 500000;
  let maxBudget = 20000000;
  let locations = FIXED_LOCATIONS;
  let intervalHours = 3;
  let mechanicalCushionDefault = 500000;
  let transferTaxPercent = 1.5;

  let message = '';
  let errorMsg = '';
  let isLoading = false;
  let authStatus = { session_saved: false };

  // Cargar la configuración desde el backend cada vez que se abre la ventana modal
  $: if (isOpen) {
    fetchConfig();
    fetchAuthStatus();
  }

  /**
   * Obtiene la configuración activa desde la API REST del backend
   */
  async function fetchConfig() {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/config');
      if (res.ok) {
        const data = await res.json();
        const cfg = data.config;
        // Garantizar que los campos fijos se mantengan constantes
        searchQuery = FIXED_SEARCH_QUERY;
        locations = FIXED_LOCATIONS;
        minBudget = cfg.min_budget;
        maxBudget = cfg.max_budget;
        intervalHours = cfg.interval_hours;
        mechanicalCushionDefault = cfg.mechanical_cushion_default;
        transferTaxPercent = cfg.transfer_tax_percent;
      }
    } catch (err) {
      console.error('[SettingsModal Error] No se pudo obtener la configuración:', err);
    }
  }

  /**
   * Consulta el estado de autenticación de Facebook guardado en auth.json
   */
  async function fetchAuthStatus() {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/auth/facebook/status');
      if (res.ok) {
        authStatus = await res.json();
      }
    } catch (err) {
      console.error('[SettingsModal Error] No se pudo obtener estado de autenticación:', err);
    }
  }

  /**
   * Guarda los cambios de configuración en el backend e inicia el recálculo dinámico masivo
   */
  async function saveConfig() {
    isLoading = true;
    message = '';
    errorMsg = '';

    try {
      // Enviar la configuración con los valores fijos obligatorios de búsqueda y región
      const res = await fetch('http://127.0.0.1:8000/api/config', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          search_query: FIXED_SEARCH_QUERY,
          min_budget: parseInt(minBudget),
          max_budget: parseInt(maxBudget),
          locations: FIXED_LOCATIONS,
          interval_hours: parseInt(intervalHours),
          mechanical_cushion_default: parseInt(mechanicalCushionDefault),
          transfer_tax_percent: parseFloat(transferTaxPercent),
          is_active: true
        })
      });

      if (res.ok) {
        message = 'Configuración guardada y parámetros aplicados exitosamente.';
        dispatch('configSaved');
        setTimeout(() => message = '', 3500);
      } else {
        errorMsg = 'Error al guardar la configuración en el servidor.';
      }
    } catch (err) {
      errorMsg = 'Error de conexión con el backend local.';
    } finally {
      isLoading = false;
    }
  }

  /**
   * Dispara el helper de inicio de sesión de Facebook para renovar auth.json
   */
  async function triggerFacebookAuth() {
    message = 'Abriendo ventana de inicio de sesión en Facebook...';
    try {
      await fetch('http://127.0.0.1:8000/api/auth/facebook', { method: 'POST' });
      setTimeout(fetchAuthStatus, 5000);
    } catch (err) {
      errorMsg = 'Error al iniciar captura de sesión de Facebook.';
    }
  }

  /**
   * Maneja la subida del archivo service_account.json para Google Sheets
   * @param {Event} e - Evento de cambio del input de tipo archivo
   */
  async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://127.0.0.1:8000/api/auth/google-sheets/credentials', {
        method: 'POST',
        body: formData
      });
      if (res.ok) {
        message = 'Archivo service_account.json cargado correctamente.';
      } else {
        errorMsg = 'Error al cargar credenciales de Google Sheets.';
      }
    } catch (err) {
      errorMsg = 'Error de subida de archivo.';
    }
  }

  let showDeleteConfirmPrompt = false;
  let isDeletingAll = false;

  /**
   * Borra la totalidad de los datos recopilados en la base de datos tras confirmar
   */
  async function handleClearAllData() {
    isDeletingAll = true;
    errorMsg = '';
    message = '';
    try {
      const res = await fetch('http://127.0.0.1:8000/api/vehicles', {
        method: 'DELETE'
      });
      if (res.ok) {
        message = 'Toda la información recopilada ha sido borrada exitosamente.';
        showDeleteConfirmPrompt = false;
        dispatch('configSaved');
      } else {
        errorMsg = 'Error al intentar limpiar la base de datos.';
      }
    } catch (err) {
      errorMsg = 'Error de conexión con el backend al intentar borrar los datos.';
    } finally {
      isDeletingAll = false;
    }
  }

  function closeModal() {
    dispatch('close');
  }
</script>

{#if isOpen}
  <div class="modal-backdrop" role="button" tabindex="0" on:click|self={closeModal} on:keydown={(e) => e.key === 'Escape' && closeModal()}>
    <div class="modal-card glass-card">
      <div class="modal-header">
        <div>
          <h2 class="modal-title">⚙️ Configuración del Sistema</h2>
          <p class="modal-sub">Parámetros del Centinela, Calculadora Financiera & Integraciones</p>
        </div>
        <button class="close-btn" on:click={closeModal}>&times;</button>
      </div>

      <div class="modal-body">
        {#if message}
          <div class="alert alert-success">✅ {message}</div>
        {/if}
        {#if errorMsg}
          <div class="alert alert-error">⚠️ {errorMsg}</div>
        {/if}

        <div class="settings-section">
          <!-- Encabezado con Ícono de Información Tooltip para eliminar ruido visual de campos fijos -->
          <div class="section-title-wrapper">
            <h3>🔍 Parámetros del Centinela Marketplace</h3>
            <div class="info-tooltip-container">
              <span class="info-icon" role="button" tabindex="0">ℹ️</span>
              <div class="tooltip-box">
                El software está configurado por defecto para rastrear únicamente la categoría Autos en las regiones Metropolitana y de Valparaíso.
              </div>
            </div>
          </div>

          <div class="grid-2">
            <div class="field-group">
              <label for="minBudget">Presupuesto Mínimo ($)</label>
              <input id="minBudget" type="number" bind:value={minBudget} />
            </div>
            <div class="field-group">
              <label for="maxBudget">Presupuesto Máximo ($)</label>
              <input id="maxBudget" type="number" bind:value={maxBudget} />
            </div>
            <div class="field-group full-width">
              <label for="intervalHours">Frecuencia de Scraping (Horas)</label>
              <input id="intervalHours" type="number" bind:value={intervalHours} />
            </div>
          </div>
        </div>

        <div class="settings-section">
          <h3>💰 Calculadora Financiera & Semáforo</h3>
          <div class="grid-2">
            <div class="field-group">
              <label for="mechanicalCushionDefault">Colchón Mecánico ($)</label>
              <input id="mechanicalCushionDefault" type="number" bind:value={mechanicalCushionDefault} />
            </div>
            <div class="field-group">
              <label for="transferTaxPercent">Impuesto Transferencia (%)</label>
              <input id="transferTaxPercent" type="number" step="0.1" bind:value={transferTaxPercent} />
            </div>
          </div>
        </div>

        <div class="settings-section">
          <h3>🔑 Autenticación & Credenciales</h3>
          <div class="auth-box glass-card">
            <div>
              <strong>Estado de Sesión Facebook:</strong>
              <span class="status-badge" class:active={authStatus.session_saved}>
                {authStatus.session_saved ? 'Guardada (auth.json)' : 'No configurada'}
              </span>
            </div>
            <button class="btn btn-secondary" on:click={triggerFacebookAuth}>
              🌐 Capturar Sesión Facebook
            </button>
          </div>

          <div class="credentials-box glass-card">
            <label for="googleCreds">Subir service_account.json (Google Sheets)</label>
            <input id="googleCreds" type="file" accept=".json" on:change={handleFileUpload} />
          </div>
        </div>

        <div class="settings-section">
          <h3 class="danger-title">🗑️ Mantenimiento & Purga de Datos</h3>
          <div class="danger-box glass-card">
            <div>
              <strong>Limpieza de Base de Datos:</strong>
              <p class="danger-sub">Borra todas las publicaciones para liberar almacenamiento y mantener la fluidez del sistema.</p>
            </div>
            <button class="btn btn-danger" on:click={() => showDeleteConfirmPrompt = true}>
              🗑️ Borrar todos los datos
            </button>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" on:click={closeModal}>Cancelar</button>
        <button class="btn btn-primary" on:click={saveConfig} disabled={isLoading}>
          {isLoading ? 'Guardando...' : 'Guardar Cambios'}
        </button>
      </div>
    </div>
  </div>
{/if}

{#if showDeleteConfirmPrompt}
  <div class="confirm-backdrop" role="button" tabindex="0" on:click|self={() => showDeleteConfirmPrompt = false} on:keydown={(e) => e.key === 'Escape' && (showDeleteConfirmPrompt = false)}>
    <div class="confirm-box glass-card">
      <div class="confirm-icon">⚠️</div>
      <h3 class="confirm-title">¿Confirmar Eliminación Masiva?</h3>
      <p class="confirm-text">estas a punto de borrar toda la informacion recopilada por los scrappers</p>
      <div class="confirm-actions">
        <button class="btn btn-secondary" on:click={() => showDeleteConfirmPrompt = false}>Cancelar</button>
        <button class="btn btn-danger" on:click={handleClearAllData} disabled={isDeletingAll}>
          {isDeletingAll ? 'Borrando...' : 'Aceptar'}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .modal-card {
    width: 100%;
    max-width: 650px;
    padding: 24px;
    max-height: 90vh;
    overflow-y: auto;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 16px;
    margin-bottom: 20px;
  }

  .modal-title {
    font-size: 20px;
    font-weight: 800;
  }

  .modal-sub {
    font-size: 13px;
    color: var(--text-muted);
  }

  .close-btn {
    background: none;
    border: none;
    font-size: 24px;
    color: var(--text-muted);
    cursor: pointer;
  }

  .settings-section {
    margin-bottom: 20px;
  }

  .settings-section h3 {
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 12px;
    color: var(--primary);
  }

  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }

  .field-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .field-group label {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-muted);
  }

  .field-group input {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid var(--border-color);
    color: white;
    padding: 10px 12px;
    border-radius: var(--radius-md);
    font-size: 14px;
    outline: none;
  }

  .section-title-wrapper {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
  }

  .settings-section .section-title-wrapper h3 {
    margin-bottom: 0;
  }

  .info-tooltip-container {
    position: relative;
    display: inline-flex;
    align-items: center;
  }

  .info-icon {
    font-size: 14px;
    cursor: pointer;
    opacity: 0.8;
    transition: opacity var(--transition-fast, 0.2s ease);
  }

  .info-icon:hover {
    opacity: 1;
  }

  .tooltip-box {
    visibility: hidden;
    opacity: 0;
    width: 260px;
    background: rgba(15, 23, 42, 0.95);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
    color: var(--text-main, #f8fafc);
    font-size: 11px;
    line-height: 1.4;
    padding: 8px 12px;
    border-radius: var(--radius-md, 8px);
    position: absolute;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    transition: opacity 0.2s ease, visibility 0.2s ease;
    z-index: 10;
    pointer-events: none;
  }

  .info-tooltip-container:hover .tooltip-box {
    visibility: visible;
    opacity: 1;
  }

  .field-group.full-width {
    grid-column: span 2;
  }

  .field-group input:focus {
    border-color: var(--primary);
  }

  .auth-box, .credentials-box {
    padding: 14px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 13px;
  }

  .credentials-box {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .status-badge {
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 700;
    background: rgba(239, 68, 68, 0.2);
    color: var(--score-rojo);
    margin-left: 6px;
  }

  .status-badge.active {
    background: rgba(16, 185, 129, 0.2);
    color: var(--score-verde);
  }

  .alert {
    padding: 10px 14px;
    border-radius: var(--radius-md);
    font-size: 13px;
    margin-bottom: 16px;
  }

  .alert-success {
    background: rgba(16, 185, 129, 0.15);
    color: #a7f3d0;
  }

  .alert-error {
    background: rgba(239, 68, 68, 0.15);
    color: #fca5a5;
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid var(--border-color);
  }

  .danger-title {
    color: #f87171 !important;
  }

  .danger-box {
    padding: 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 13px;
    border: 1px solid rgba(239, 68, 68, 0.3);
    background: rgba(239, 68, 68, 0.06);
    border-radius: var(--radius-md, 8px);
  }

  .danger-sub {
    font-size: 11px;
    color: var(--text-muted);
    margin-top: 2px;
  }

  .btn-danger {
    background: rgba(239, 68, 68, 0.2);
    color: #fca5a5;
    border: 1px solid rgba(239, 68, 68, 0.4);
    padding: 8px 14px;
    border-radius: var(--radius-md, 8px);
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .btn-danger:hover {
    background: rgba(239, 68, 68, 0.45);
    color: white;
    box-shadow: 0 0 14px rgba(239, 68, 68, 0.7);
  }

  .confirm-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.75);
    backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .confirm-box {
    max-width: 420px;
    width: 90%;
    padding: 26px;
    text-align: center;
    border: 1px solid rgba(239, 68, 68, 0.5);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
  }

  .confirm-icon {
    font-size: 38px;
    margin-bottom: 8px;
  }

  .confirm-title {
    font-size: 17px;
    font-weight: 800;
    margin-bottom: 10px;
    color: #fca5a5;
  }

  .confirm-text {
    font-size: 13px;
    color: var(--text-muted);
    margin-bottom: 22px;
    line-height: 1.45;
  }

  .confirm-actions {
    display: flex;
    justify-content: center;
    gap: 12px;
  }
</style>
