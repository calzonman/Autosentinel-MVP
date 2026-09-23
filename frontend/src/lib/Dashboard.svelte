<script>
  import { createEventDispatcher } from 'svelte';
  export let vehicles = [];
  export let stats = {};
  export let selectedScoreFilter = '';
  export let searchQuery = '';

  const dispatch = createEventDispatcher();

  let spreadsheetIdInput = '';
  let showExportSheetPrompt = false;
  let isExporting = false;
  let exportStatusMessage = '';

  // Estado de pestaña activa por tarjeta de vehículo ('chileautos' o 'marketplace')
  let activeTabPerVehicle = {};

  function getActiveTab(vehicleId) {
    return activeTabPerVehicle[vehicleId] || 'chileautos';
  }

  function setActiveTab(vehicleId, tab) {
    activeTabPerVehicle = { ...activeTabPerVehicle, [vehicleId]: tab };
  }

  function setFilter(score) {
    dispatch('filterChange', score);
  }

  function triggerValidateMarket(vehicle) {
    dispatch('openValidateModal', vehicle);
  }

  function triggerOpenMarketDetail(vehicle, marketKey) {
    dispatch('openMarketDetail', { vehicle, marketKey });
  }

  function openMarketplaceUrl(url) {
    if (!url) return;
    let fullUrl = url.trim();
    if (!fullUrl.startsWith('http://') && !fullUrl.startsWith('https://')) {
      fullUrl = 'https://www.facebook.com' + (fullUrl.startsWith('/') ? '' : '/') + fullUrl;
    }
    window.open(fullUrl, '_blank', 'noopener,noreferrer');
  }

  async function handleExportToSheets() {
    if (!spreadsheetIdInput.trim()) {
      exportStatusMessage = 'Por favor ingresa el ID de tu Google Sheet.';
      return;
    }

    isExporting = true;
    exportStatusMessage = '';

    try {
      const res = await fetch('http://127.0.0.1:8000/api/export-sheets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          spreadsheet_id: spreadsheetIdInput.trim(),
          vehicle_ids: []
        })
      });
      const data = await res.json();
      if (data.success) {
        exportStatusMessage = `✅ ${data.message}`;
        setTimeout(() => {
          showExportSheetPrompt = false;
          exportStatusMessage = '';
          dispatch('refresh');
        }, 2500);
      } else {
        exportStatusMessage = `⚠️ ${data.message}`;
      }
    } catch (err) {
      exportStatusMessage = '⚠️ Error al conectar con la API de exportación.';
    } finally {
      isExporting = false;
    }
  }

  /**
   * Elimina un vehículo individual de la base de datos y solicita un refresco global
   * @param {number} vehicleId - ID del vehículo a eliminar
   */
  async function handleDeleteVehicle(vehicleId) {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/vehicles/${vehicleId}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        dispatch('refresh');
      } else {
        console.error('[Dashboard Error] No se pudo eliminar el vehículo:', vehicleId);
      }
    } catch (err) {
      console.error('[Dashboard Error] Error de conexión al eliminar vehículo:', err);
    }
  }
</script>

<div class="dashboard-wrapper">
  <!-- Tarjetas de Métricas Principales -->
  <div class="metrics-grid">
    <div class="metric-card glass-card">
      <div class="metric-icon">🚗</div>
      <div>
        <div class="metric-title">Total Detectados</div>
        <div class="metric-value">{stats?.total_vehicles || 0}</div>
      </div>
    </div>

    <div class="metric-card glass-card verde" role="button" tabindex="0" on:click={() => setFilter('VERDE')} on:keydown={(e) => e.key === 'Enter' && setFilter('VERDE')}>
      <div class="metric-icon">🟢</div>
      <div>
        <div class="metric-title">Oportunidad Verde (&ge;&nbsp;30% Margen)</div>
        <div class="metric-value verde-text">{stats?.score_verde || 0}</div>
      </div>
    </div>

    <div class="metric-card glass-card amarillo" role="button" tabindex="0" on:click={() => setFilter('AMARILLO')} on:keydown={(e) => e.key === 'Enter' && setFilter('AMARILLO')}>
      <div class="metric-icon">🟡</div>
      <div>
        <div class="metric-title">Rentabilidad Ajustada (15-30%)</div>
        <div class="metric-value amarillo-text">{stats?.score_amarillo || 0}</div>
      </div>
    </div>

    <div class="metric-card glass-card rojo" role="button" tabindex="0" on:click={() => setFilter('ROJO')} on:keydown={(e) => e.key === 'Enter' && setFilter('ROJO')}>
      <div class="metric-icon">🔴</div>
      <div>
        <div class="metric-title">Margen Bajo (&lt;&nbsp;15%)</div>
        <div class="metric-value rojo-text">{stats?.score_rojo || 0}</div>
      </div>
    </div>
  </div>

  <!-- Barra de Búsqueda, Filtros y Acciones -->
  <div class="controls-bar glass-card">
    <div class="search-input-wrapper">
      <span class="search-icon">🔍</span>
      <input 
        type="text" 
        placeholder="Buscar por marca, modelo o título..." 
        bind:value={searchQuery}
        on:input={() => dispatch('searchChange', searchQuery)}
      />
    </div>

    <div class="filter-tabs">
      <button class="tab-btn" class:active={selectedScoreFilter === ''} on:click={() => setFilter('')}>
        Todos
      </button>
      <button class="tab-btn verde" class:active={selectedScoreFilter === 'VERDE'} on:click={() => setFilter('VERDE')}>
        🟢 Verdes
      </button>
      <button class="tab-btn amarillo" class:active={selectedScoreFilter === 'AMARILLO'} on:click={() => setFilter('AMARILLO')}>
        🟡 Amarillos
      </button>
      <button class="tab-btn rojo" class:active={selectedScoreFilter === 'ROJO'} on:click={() => setFilter('ROJO')}>
        🔴 Rojos
      </button>
    </div>

    <button class="btn btn-success" on:click={() => showExportSheetPrompt = true}>
      📊 Exportar a Google Sheets
    </button>
  </div>

  <!-- Grilla de Vehículos Detectados -->
  {#if vehicles.length === 0}
    <div class="empty-state glass-card">
      <div class="empty-icon">🚘</div>
      <h3>No se encontraron vehículos</h3>
      <p>Haz clic en "Escanear Marketplace" para iniciar la búsqueda pasiva del Centinela.</p>
    </div>
  {:else}
    <div class="vehicles-grid">
      {#each vehicles as vehicle (vehicle.id)}
        {@const currentTab = activeTabPerVehicle[vehicle.id] || 'chileautos'}
        {@const isCA = currentTab === 'chileautos'}
        {@const currentPrice = isCA ? (vehicle.estimated_market_price_chileautos || vehicle.estimated_market_price) : vehicle.estimated_market_price_mp}
        {@const currentMargin = isCA ? (vehicle.margin_chileautos || vehicle.calculated_margin) : vehicle.margin_mp}
        {@const currentScore = isCA ? (vehicle.score_chileautos || vehicle.score) : (vehicle.score_mp || 'PENDIENTE')}
        {@const currentTransfer = isCA ? (vehicle.transfer_tax_chileautos || vehicle.transfer_tax) : (vehicle.transfer_tax_mp || vehicle.transfer_tax)}

        <div class="vehicle-card glass-card">
          <div class="card-image-wrapper">
            <!-- Botón de Borrado de Tarjeta (Icono Basurero con Red Glow en Hover) -->
            <button 
              type="button" 
              class="card-delete-btn" 
              title="Borrar esta tarjeta"
              on:click|stopPropagation={() => handleDeleteVehicle(vehicle.id)}
            >
              🗑️
            </button>

            {#if vehicle.image_url}
              <img src={vehicle.image_url} alt={vehicle.title} loading="lazy" />
            {:else}
              <div class="placeholder-img">🚘 Sin foto</div>
            {/if}
            <span class="badge-score {currentScore}">
              {currentScore}
            </span>
          </div>

          <div class="card-content">
            <div class="card-header">
              <h3 class="vehicle-title" title={vehicle.title}>{vehicle.title}</h3>
              <span class="location-tag">📍 {vehicle.location || 'Valparaíso / RM'}</span>
            </div>

            <!-- Pestañas de Selección de Mercado dentro de la Tarjeta -->
            <div class="card-market-tabs">
              <button 
                type="button"
                class="inner-tab-btn" 
                class:active={currentTab === 'chileautos'} 
                on:click|stopPropagation={() => setActiveTab(vehicle.id, 'chileautos')}
              >
                🇨🇱 Chileautos
              </button>
              <button 
                type="button"
                class="inner-tab-btn" 
                class:active={currentTab === 'marketplace'} 
                on:click|stopPropagation={() => setActiveTab(vehicle.id, 'marketplace')}
              >
                🛒 Marketplace
              </button>
            </div>

            <div class="price-row">
              <div class="price-box">
                <span class="price-label">Precio Publicado</span>
                <span class="price-val">${vehicle.price?.toLocaleString('es-CL')}</span>
              </div>
              
              <!-- Mediana Clickeable para abrir Modal de Desglose -->
              <div 
                class="price-box clickable" 
                role="button"
                tabindex="0"
                on:click|stopPropagation={() => triggerOpenMarketDetail(vehicle, currentTab)}
                on:keydown={(e) => e.key === 'Enter' && triggerOpenMarketDetail(vehicle, currentTab)}
                title="Haz clic para ver desglose de muestra (Promedio, Mín, Máx)"
              >
                <span class="price-label">Mediana {isCA ? 'Chileautos' : 'Marketplace'} 🔍</span>
                <span class="price-val market">
                  {currentPrice ? `$${currentPrice.toLocaleString('es-CL')}` : 'Pendiente ⏳'}
                </span>
              </div>
            </div>

            <div class="financial-breakdown">
              <div class="fin-item">
                <span>Transf. (1.5%):</span>
                <strong>${currentTransfer?.toLocaleString('es-CL')}</strong>
              </div>
              <div class="fin-item">
                <span>Colchón Mecánico:</span>
                <strong>${vehicle.mechanical_cushion?.toLocaleString('es-CL')}</strong>
              </div>
              <div class="fin-item highlight">
                <span>Margen Estimado:</span>
                <strong class={currentMargin >= 0 ? 'pos' : 'neg'}>
                  ${currentMargin?.toLocaleString('es-CL')}
                </strong>
              </div>
            </div>

            <div class="card-actions">
              <!-- Botón de Ver en Marketplace Fix -->
              <button 
                class="btn btn-secondary btn-sm" 
                on:click|stopPropagation={() => openMarketplaceUrl(vehicle.url)}
              >
                🔗 Ver en Marketplace
              </button>

              <button 
                class="btn btn-primary btn-sm" 
                on:click|stopPropagation={() => triggerValidateMarket(vehicle)}
              >
                ⚡ Validar Mercado
              </button>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<!-- Modal para Exportación a Google Sheets -->
{#if showExportSheetPrompt}
  <div class="modal-backdrop" role="button" tabindex="0" on:click|self={() => showExportSheetPrompt = false} on:keydown={(e) => e.key === 'Escape' && (showExportSheetPrompt = false)}>
    <div class="export-modal glass-card">
      <h3>📊 Exportar Oportunidades a Google Sheets</h3>
      <p class="sub">Ingresa el ID de la Hoja de Cálculo donde deseas enviar los vehículos aprobados.</p>

      {#if exportStatusMessage}
        <div class="alert">{exportStatusMessage}</div>
      {/if}

      <div class="field-group">
        <label for="spreadsheetId">ID de Google Sheet (Ej: 1BxiMVs0XR83EA...)</label>
        <input 
          id="spreadsheetId" 
          type="text" 
          bind:value={spreadsheetIdInput} 
          placeholder="Ingresa Spreadsheet ID" 
        />
      </div>

      <div class="modal-actions">
        <button class="btn btn-secondary" on:click={() => showExportSheetPrompt = false}>Cancelar</button>
        <button class="btn btn-success" on:click={handleExportToSheets} disabled={isExporting}>
          {isExporting ? 'Exportando...' : 'Confirmar Exportación'}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .dashboard-wrapper {
    max-width: 1400px;
    margin: 0 auto;
    padding: 24px;
  }

  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
  }

  .metric-card {
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    cursor: pointer;
  }

  .metric-icon {
    font-size: 32px;
  }

  .metric-title {
    font-size: 12px;
    color: var(--text-muted);
    font-weight: 600;
  }

  .metric-value {
    font-size: 26px;
    font-weight: 800;
    margin-top: 2px;
  }

  .verde-text { color: var(--score-verde); }
  .amarillo-text { color: var(--score-amarillo); }
  .rojo-text { color: var(--score-rojo); }

  .controls-bar {
    padding: 16px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 24px;
    flex-wrap: wrap;
  }

  .search-input-wrapper {
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid var(--border-color);
    padding: 8px 16px;
    border-radius: var(--radius-md);
    flex: 1;
    min-width: 260px;
  }

  .search-input-wrapper input {
    background: none;
    border: none;
    color: white;
    font-size: 14px;
    width: 100%;
    outline: none;
  }

  .filter-tabs {
    display: flex;
    gap: 6px;
    background: rgba(0, 0, 0, 0.2);
    padding: 4px;
    border-radius: var(--radius-md);
  }

  .tab-btn {
    background: none;
    border: none;
    color: var(--text-muted);
    padding: 6px 14px;
    border-radius: var(--radius-sm);
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .tab-btn.active {
    background: rgba(255, 255, 255, 0.12);
    color: white;
  }

  .vehicles-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 20px;
  }

  .vehicle-card {
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .card-image-wrapper {
    position: relative;
    height: 180px;
    background: rgba(0, 0, 0, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .card-image-wrapper img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .placeholder-img {
    color: var(--text-dim);
    font-size: 14px;
  }

  .badge-score {
    position: absolute;
    top: 12px;
    right: 12px;
  }

  .card-delete-btn {
    position: absolute;
    top: 12px;
    left: 12px;
    background: rgba(15, 23, 42, 0.75);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 50%;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    cursor: pointer;
    z-index: 5;
    transition: all 0.2s ease;
    outline: none;
  }

  .card-delete-btn:hover {
    background: rgba(239, 68, 68, 0.25);
    border-color: #ef4444;
    box-shadow: 0 0 14px rgba(239, 68, 68, 0.85);
    transform: scale(1.12);
  }

  .card-content {
    padding: 18px;
    display: flex;
    flex-direction: column;
    flex: 1;
    gap: 12px;
  }

  .vehicle-title {
    font-size: 16px;
    font-weight: 700;
    line-height: 1.3;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .location-tag {
    font-size: 11px;
    color: var(--text-muted);
  }

  .card-market-tabs {
    display: flex;
    gap: 4px;
    background: rgba(0, 0, 0, 0.3);
    padding: 3px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-color);
  }

  .inner-tab-btn {
    flex: 1;
    background: transparent;
    border: 1px solid transparent;
    color: var(--text-muted);
    font-size: 11px;
    font-weight: 700;
    padding: 6px 8px;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: all var(--transition-fast);
    user-select: none;
  }

  .inner-tab-btn:hover {
    color: white;
    background: rgba(255, 255, 255, 0.08);
  }

  .inner-tab-btn.active {
    background: rgba(59, 130, 246, 0.25);
    color: #60a5fa;
    border-color: rgba(96, 165, 250, 0.4);
    box-shadow: 0 0 10px rgba(59, 130, 246, 0.2);
  }

  .price-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    background: rgba(0, 0, 0, 0.2);
    padding: 10px;
    border-radius: var(--radius-md);
  }

  .price-box {
    display: flex;
    flex-direction: column;
  }

  .price-box.clickable {
    cursor: pointer;
    border: 1px dashed rgba(59, 130, 246, 0.3);
    padding: 4px 6px;
    border-radius: var(--radius-sm);
    transition: all var(--transition-fast);
  }

  .price-box.clickable:hover {
    background: rgba(59, 130, 246, 0.2);
    border-color: var(--primary);
    transform: scale(1.02);
  }

  .price-label {
    font-size: 10px;
    color: var(--text-muted);
    text-transform: uppercase;
  }

  .price-val {
    font-size: 15px;
    font-weight: 800;
  }

  .price-val.market {
    color: var(--primary);
  }

  .financial-breakdown {
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 12px;
    border-top: 1px solid var(--border-color);
    padding-top: 10px;
  }

  .fin-item {
    display: flex;
    justify-content: space-between;
    color: var(--text-muted);
  }

  .fin-item.highlight {
    color: white;
    font-size: 13px;
    margin-top: 4px;
  }

  .pos { color: var(--score-verde); }
  .neg { color: var(--score-rojo); }

  .card-actions {
    display: flex;
    gap: 8px;
    margin-top: auto;
    padding-top: 10px;
  }

  .btn-sm {
    padding: 8px 12px;
    font-size: 12px;
    flex: 1;
    justify-content: center;
  }

  .empty-state {
    text-align: center;
    padding: 60px 20px;
  }

  .empty-icon {
    font-size: 48px;
    margin-bottom: 12px;
  }

  .export-modal {
    width: 100%;
    max-width: 480px;
    padding: 24px;
  }

  .export-modal .sub {
    font-size: 13px;
    color: var(--text-muted);
    margin-bottom: 16px;
  }

  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 16px;
  }
</style>
