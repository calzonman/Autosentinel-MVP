<script>
  import { createEventDispatcher } from 'svelte';
  export let vehicle = null;
  export let marketKey = 'chileautos'; // 'chileautos' o 'marketplace'
  export let isOpen = false;

  const dispatch = createEventDispatcher();

  function closeModal() {
    dispatch('close');
  }

  function triggerValidate() {
    dispatch('validate', vehicle);
    closeModal();
  }

  $: isCA = marketKey === 'chileautos';
  $: marketName = isCA ? 'Chileautos' : 'Facebook Marketplace';
  $: marketFlag = isCA ? '🇨🇱' : '🛒';

  $: medianPrice = vehicle ? (isCA ? (vehicle.estimated_market_price_chileautos || vehicle.estimated_market_price) : vehicle.estimated_market_price_mp) : 0;
  $: samplesCount = vehicle ? (isCA ? vehicle.samples_count_chileautos : vehicle.samples_count_mp) : 0;
  $: minPrice = vehicle ? (isCA ? vehicle.min_price_chileautos : vehicle.min_price_mp) : 0;
  $: maxPrice = vehicle ? (isCA ? vehicle.max_price_chileautos : vehicle.max_price_mp) : 0;
  $: avgPrice = vehicle ? (isCA ? vehicle.avg_price_chileautos : vehicle.avg_price_mp) : 0;

  $: hasData = medianPrice > 0;
</script>

{#if isOpen && vehicle}
  <div class="modal-backdrop" role="button" tabindex="0" on:click|self={closeModal} on:keydown={(e) => e.key === 'Escape' && closeModal()}>
    <div class="modal-card glass-card">
      <div class="modal-header">
        <div>
          <span class="badge-tag">{marketFlag} Mercado {marketName}</span>
          <h2 class="modal-title">Desglose de Muestra Estadística</h2>
          <p class="modal-sub">{vehicle.title}</p>
        </div>
        <button class="close-btn" on:click={closeModal}>&times;</button>
      </div>

      <div class="modal-body">
        {#if hasData}
          <div class="stats-summary-card">
            <div class="summary-header">
              <span class="header-icon">📊</span>
              <div>
                <h4>Resultados del Análisis de Muestra</h4>
                <p>Estadísticas extraídas de publicaciones activas en {marketName}</p>
              </div>
            </div>

            <div class="stats-grid">
              <!-- 1. Muestra -->
              <div class="stat-box">
                <span class="stat-icon">📑</span>
                <span class="stat-label">Muestra Rescatada</span>
                <span class="stat-value">{samplesCount > 0 ? `${samplesCount} autos` : 'N/A'}</span>
              </div>

              <!-- 2. Promedio -->
              <div class="stat-box">
                <span class="stat-icon">🧮</span>
                <span class="stat-label">Promedio de Muestra</span>
                <span class="stat-value">{avgPrice > 0 ? `$${avgPrice.toLocaleString('es-CL')}` : 'N/A'}</span>
              </div>

              <!-- 3. Precio Mínimo -->
              <div class="stat-box">
                <span class="stat-icon">📉</span>
                <span class="stat-label">Precio Más Bajo (Mín)</span>
                <span class="stat-value min">{minPrice > 0 ? `$${minPrice.toLocaleString('es-CL')}` : 'N/A'}</span>
              </div>

              <!-- 4. Precio Máximo -->
              <div class="stat-box">
                <span class="stat-icon">📈</span>
                <span class="stat-label">Precio Más Alto (Máx)</span>
                <span class="stat-value max">{maxPrice > 0 ? `$${maxPrice.toLocaleString('es-CL')}` : 'N/A'}</span>
              </div>

              <!-- 5. Mediana Destacada -->
              <div class="stat-box highlight">
                <span class="stat-icon">⚖️</span>
                <span class="stat-label">Mediana Calculada</span>
                <span class="stat-value median">${medianPrice.toLocaleString('es-CL')}</span>
              </div>
            </div>
          </div>
        {:else}
          <div class="no-data-card glass-card">
            <div class="no-data-icon">⏳</div>
            <h3>Mercado {marketName} no validado aún</h3>
            <p>Haz clic a continuación para ejecutar la validación automática de mercado.</p>
            <button class="btn btn-primary" on:click={triggerValidate}>
              ⚡ Validar Mercado Ahora
            </button>
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
    max-width: 560px;
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

  .stats-summary-card {
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 16px;
  }

  .summary-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 12px;
  }

  .header-icon {
    font-size: 24px;
  }

  .summary-header h4 {
    font-size: 14px;
    font-weight: 700;
  }

  .summary-header p {
    font-size: 12px;
    color: var(--text-muted);
  }

  .stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }

  .stat-box {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--border-color);
    padding: 12px;
    border-radius: var(--radius-md);
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .stat-box.highlight {
    grid-column: span 2;
    background: rgba(59, 130, 246, 0.12);
    border-color: rgba(59, 130, 246, 0.35);
  }

  .stat-icon {
    font-size: 16px;
  }

  .stat-label {
    font-size: 11px;
    color: var(--text-muted);
    font-weight: 600;
  }

  .stat-value {
    font-size: 16px;
    font-weight: 800;
    color: white;
  }

  .stat-value.min {
    color: #60a5fa;
  }

  .stat-value.max {
    color: #f59e0b;
  }

  .stat-value.median {
    font-size: 22px;
    color: var(--score-verde);
  }

  .no-data-card {
    text-align: center;
    padding: 40px 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }

  .no-data-icon {
    font-size: 40px;
  }

  .no-data-card p {
    font-size: 13px;
    color: var(--text-muted);
    margin-bottom: 10px;
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid var(--border-color);
  }
</style>
