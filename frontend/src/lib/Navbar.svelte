<script>
  import { createEventDispatcher } from 'svelte';
  export let stats = {};
  export let apiOnline = true;
  export let isRunningSentinel = false;

  const dispatch = createEventDispatcher();

  function triggerRunSentinel() {
    dispatch('runSentinel');
  }

  function triggerFacebookAuth() {
    dispatch('openFacebookAuth');
  }

  function triggerOpenSettings() {
    dispatch('openSettings');
  }
</script>

<header class="navbar">
  <div class="nav-container">
    <div class="brand">
      <div class="logo-icon">🚗</div>
      <div>
        <h1 class="brand-title">AutoSentinel MVP</h1>
        <p class="brand-sub">Detección & Análisis de Rentabilidad Automotriz</p>
      </div>
    </div>

    <div class="nav-status">
      <div class="status-indicator" class:online={apiOnline}>
        <span class="dot"></span>
        <span class="status-text">{apiOnline ? 'Backend Activo' : 'Conectando...'}</span>
      </div>

      <div class="auth-pill" class:authenticated={stats?.session_saved}>
        <span class="auth-icon">{stats?.session_saved ? '🔒' : '🔓'}</span>
        <span class="auth-text">{stats?.session_saved ? 'Sesión FB Guardada' : 'Sin Sesión FB'}</span>
        <button class="btn-xs" on:click={triggerFacebookAuth}>
          {stats?.session_saved ? 'Renovar' : 'Iniciar Sesión'}
        </button>
      </div>
    </div>

    <div class="nav-actions">
      <button class="btn btn-secondary" on:click={triggerOpenSettings}>
        ⚙️ Configuración
      </button>

      <button 
        class="btn btn-primary" 
        on:click={triggerRunSentinel} 
        disabled={isRunningSentinel || !apiOnline}
      >
        {#if isRunningSentinel}
          <span class="spinner"></span> Escaneando...
        {:else}
          🔍 Escanear Marketplace
        {/if}
      </button>
    </div>
  </div>
</header>

<style>
  .navbar {
    background: rgba(11, 15, 25, 0.85);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border-color);
    position: sticky;
    top: 0;
    z-index: 100;
    padding: 12px 24px;
  }

  .nav-container {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .logo-icon {
    font-size: 28px;
    background: rgba(59, 130, 246, 0.15);
    padding: 8px 12px;
    border-radius: var(--radius-md);
    border: 1px solid var(--primary-glow);
  }

  .brand-title {
    font-size: 18px;
    font-weight: 800;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, #fff, #9ca3af);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .brand-sub {
    font-size: 11px;
    color: var(--text-muted);
  }

  .nav-status {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .status-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: var(--text-muted);
  }

  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--score-rojo);
  }

  .status-indicator.online .dot {
    background: var(--score-verde);
    box-shadow: 0 0 8px var(--score-verde);
  }

  .auth-pill {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--border-color);
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
  }

  .auth-pill.authenticated {
    border-color: rgba(16, 185, 129, 0.3);
    background: rgba(16, 185, 129, 0.1);
  }

  .btn-xs {
    background: rgba(255, 255, 255, 0.15);
    border: none;
    color: white;
    font-size: 10px;
    padding: 3px 8px;
    border-radius: 12px;
    cursor: pointer;
    font-weight: 600;
  }

  .btn-xs:hover {
    background: var(--primary);
  }

  .nav-actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .spinner {
    width: 14px;
    height: 14px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
