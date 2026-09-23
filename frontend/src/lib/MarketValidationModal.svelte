<script>
  import { createEventDispatcher } from 'svelte';
  export let vehicle = null;
  export let isOpen = false;

  const dispatch = createEventDispatcher();

  let brand = '';
  let model = '';
  let year = '';
  let isAnalyzing = false;
  let chileautosStats = null;
  let marketplaceStats = null;
  let errorMessage = '';

  $: if (vehicle) {
    const titleParts = vehicle.title.trim().split(/\s+/);
    if (/^\d{4}$/.test(titleParts[0])) {
      year = vehicle.year || titleParts[0];
      brand = vehicle.brand || titleParts[1] || '';
      model = vehicle.model || titleParts.slice(2).join(' ') || '';
    } else {
      brand = vehicle.brand || titleParts[0] || '';
      model = vehicle.model || titleParts.slice(1).join(' ') || '';
      year = vehicle.year || '';
    }
    chileautosStats = null;
    marketplaceStats = null;
    errorMessage = '';
  }

  function closeModal() {
    dispatch('close');
  }

  async function runValidation() {
    if (!brand || !model) {
      errorMessage = 'Debes ingresar al menos la marca y el modelo.';
      return;
    }

    isAnalyzing = true;
    errorMessage = '';
    chileautosStats = null;
    marketplaceStats = null;

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/vehicles/${vehicle.id}/validate-market`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          brand: brand.trim(),
          model: model.trim(),
          year: year ? parseInt(year) : null
        })
      });

      const data = await response.json();
      if (response.ok) {
        chileautosStats = data.chileautos_stats;
        marketplaceStats = data.marketplace_stats;
        dispatch('updated', data.vehicle);
      } else {
        errorMessage = data.detail || 'Error al validar mercado.';
      }
    } catch (err) {
      errorMessage = 'Error de conexión con el backend local.';
    } finally {
      isAnalyzing = false;
    }
  }
</script>

{#if isOpen && vehicle}
  <div class="modal-backdrop" role="button" tabindex="0" on:click|self={closeModal} on:keydown={(e) => e.key === 'Escape' && closeModal()}>
    <div class="modal-card glass-card">
      <div class="modal-header">
        <div>
          <span class="badge-tag">Validación Dual de Mercado</span>
          <h2 class="modal-title">Validación Chileautos & Marketplace</h2>
          <p class="modal-sub">{vehicle.title}</p>
        </div>
        <button class="close-btn" on:click={closeModal}>&times;</button>
      </div>

      <div class="modal-body">
        <div class="form-row">
          <div class="field-group">
            <label for="brand">Marca</label>
            <input id="brand" type="text" bind:value={brand} placeholder="Ej: Suzuki, Toyota" />
          </div>
          <div class="field-group">
            <label for="model">Modelo</label>
            <input id="model" type="text" bind:value={model} placeholder="Ej: Swift, Yaris" />
          </div>
          <div class="field-group">
            <label for="year">Año</label>
            <input id="year" type="number" bind:value={year} placeholder="Ej: 2018" />
          </div>
        </div>

        {#if errorMessage}
          <div class="alert alert-error">⚠️ {errorMessage}</div>
        {/if}

        <div class="action-bar">
          <button class="btn btn-primary btn-block" on:click={runValidation} disabled={isAnalyzing}>
            {#if isAnalyzing}
              <span class="spinner"></span> Escaneando Chileautos y Facebook Marketplace...
            {:else}
              ⚡ Validar Mercado Automáticamente
            {/if}
          </button>
        </div>

        {#if chileautosStats || marketplaceStats}
          <div class="dual-results-grid">
            <!-- Columna Chileautos -->
            <div class="market-result-card glass-card">
              <div class="market-card-title">🇨🇱 Chileautos</div>
              {#if chileautosStats && chileautosStats.success}
                <div class="metric-group">
                  <span class="metric-lbl">Mediana de Mercado</span>
                  <span class="metric-val highlight">${chileautosStats.median_price?.toLocaleString('es-CL')}</span>
                </div>
                <div class="metric-sub-row">
                  <span>Muestras: <strong>{chileautosStats.sample_count}</strong></span>
                  <span>Mín: <strong>${chileautosStats.min_price?.toLocaleString('es-CL')}</strong></span>
                </div>
              {:else}
                <div class="no-data">{chileautosStats?.message || 'Sin datos de Chileautos'}</div>
              {/if}
            </div>

            <!-- Columna Marketplace -->
            <div class="market-result-card glass-card">
              <div class="market-card-title">🛒 Marketplace</div>
              {#if marketplaceStats && marketplaceStats.success}
                <div class="metric-group">
                  <span class="metric-lbl">Mediana de Mercado</span>
                  <span class="metric-val highlight mp">${marketplaceStats.median_price?.toLocaleString('es-CL')}</span>
                </div>
                <div class="metric-sub-row">
                  <span>Muestras: <strong>{marketplaceStats.sample_count}</strong></span>
                  <span>Mín: <strong>${marketplaceStats.min_price?.toLocaleString('es-CL')}</strong></span>
                </div>
              {:else}
                <div class="no-data">{marketplaceStats?.message || 'Sin datos de Marketplace'}</div>
              {/if}
            </div>
          </div>
        {/if}
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" on:click={closeModal}>Cerrar</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .modal-card {
    width: 100%;
    max-width: 620px;
    padding: 24px;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 16px;
    margin-bottom: 20px;
  }

  .badge-tag {
    font-size: 10px;
    font-weight: 800;
    text-transform: uppercase;
    color: var(--primary);
    background: rgba(59, 130, 246, 0.15);
    padding: 2px 8px;
    border-radius: 10px;
    border: 1px solid var(--primary-glow);
  }

  .modal-title {
    font-size: 20px;
    font-weight: 800;
    margin-top: 4px;
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

  .close-btn:hover {
    color: white;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr 100px;
    gap: 12px;
    margin-bottom: 16px;
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

  .field-group input:focus {
    border-color: var(--primary);
    box-shadow: 0 0 10px var(--primary-glow);
  }

  .btn-block {
    width: 100%;
    justify-content: center;
    padding: 12px;
  }

  .alert {
    padding: 10px 14px;
    border-radius: var(--radius-md);
    font-size: 13px;
    margin-bottom: 16px;
  }

  .alert-error {
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #fca5a5;
  }

  .dual-results-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-top: 20px;
  }

  .market-result-card {
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .market-card-title {
    font-size: 13px;
    font-weight: 700;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 6px;
  }

  .metric-group {
    display: flex;
    flex-direction: column;
  }

  .metric-lbl {
    font-size: 10px;
    color: var(--text-muted);
    text-transform: uppercase;
  }

  .metric-val.highlight {
    font-size: 18px;
    font-weight: 800;
    color: var(--score-verde);
  }

  .metric-val.mp {
    color: #3b82f6;
  }

  .metric-sub-row {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: var(--text-muted);
  }

  .no-data {
    font-size: 12px;
    color: var(--text-dim);
    padding: 10px 0;
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid var(--border-color);
  }

  .spinner {
    width: 14px;
    height: 14px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    display: inline-block;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
