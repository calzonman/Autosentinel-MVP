<script>
  import { onMount } from 'svelte';
  import Navbar from './lib/Navbar.svelte';
  import Dashboard from './lib/Dashboard.svelte';
  import MarketValidationModal from './lib/MarketValidationModal.svelte';
  import MarketDetailModal from './lib/MarketDetailModal.svelte';
  import SettingsModal from './lib/SettingsModal.svelte';

  let apiOnline = false;
  let isRunningSentinel = false;
  let stats = {};
  let vehicles = [];
  let selectedScoreFilter = '';
  let searchQuery = '';

  let isValidationModalOpen = false;
  let selectedVehicleForValidation = null;

  let isDetailModalOpen = false;
  let selectedVehicleForDetail = null;
  let selectedMarketKeyForDetail = 'chileautos';

  let isSettingsModalOpen = false;

  onMount(() => {
    fetchStats();
    fetchVehicles();
    const interval = setInterval(() => {
      fetchStats();
    }, 10000);
    return () => clearInterval(interval);
  });

  async function fetchStats() {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/stats');
      if (res.ok) {
        stats = await res.json();
        apiOnline = true;
      } else {
        apiOnline = false;
      }
    } catch (err) {
      apiOnline = false;
    }
  }

  async function fetchVehicles() {
    try {
      let url = `http://127.0.0.1:8000/api/vehicles?only_valid=true`;
      if (selectedScoreFilter) {
        url += `&score=${selectedScoreFilter}`;
      }
      if (searchQuery) {
        url += `&search=${encodeURIComponent(searchQuery)}`;
      }
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        vehicles = data.vehicles;
      }
    } catch (err) {
      console.error(err);
    }
  }

  async function handleRunSentinel() {
    isRunningSentinel = true;
    try {
      await fetch('http://127.0.0.1:8000/api/sentinel/run', { method: 'POST' });
      setTimeout(() => {
        isRunningSentinel = false;
        fetchVehicles();
        fetchStats();
      }, 6000);
    } catch (err) {
      isRunningSentinel = false;
    }
  }

  function handleFilterChange(event) {
    selectedScoreFilter = event.detail;
    fetchVehicles();
  }

  function handleSearchChange(event) {
    searchQuery = event.detail;
    fetchVehicles();
  }

  function handleOpenValidationModal(event) {
    selectedVehicleForValidation = event.detail;
    isValidationModalOpen = true;
  }

  function handleOpenMarketDetail(event) {
    selectedVehicleForDetail = event.detail.vehicle;
    selectedMarketKeyForDetail = event.detail.marketKey;
    isDetailModalOpen = true;
  }

  function handleVehicleUpdated() {
    fetchVehicles();
    fetchStats();
  }

  async function handleFacebookAuthTrigger() {
    try {
      await fetch('http://127.0.0.1:8000/api/auth/facebook', { method: 'POST' });
      alert('Se ha abierto una ventana del navegador para iniciar sesión en Facebook. Las cookies se guardarán en auth.json automáticamente.');
    } catch (err) {
      alert('Error al iniciar la sesión de Facebook.');
    }
  }
</script>

<div class="app-root">
  <Navbar 
    {stats} 
    {apiOnline} 
    {isRunningSentinel}
    on:runSentinel={handleRunSentinel}
    on:openFacebookAuth={handleFacebookAuthTrigger}
    on:openSettings={() => isSettingsModalOpen = true}
  />

  <main>
    <Dashboard 
      {vehicles} 
      {stats} 
      {selectedScoreFilter} 
      {searchQuery}
      on:filterChange={handleFilterChange}
      on:searchChange={handleSearchChange}
      on:openValidateModal={handleOpenValidationModal}
      on:openMarketDetail={handleOpenMarketDetail}
      on:refresh={() => { fetchVehicles(); fetchStats(); }}
    />
  </main>

  <MarketValidationModal 
    vehicle={selectedVehicleForValidation}
    isOpen={isValidationModalOpen}
    on:close={() => isValidationModalOpen = false}
    on:updated={handleVehicleUpdated}
  />

  <MarketDetailModal 
    vehicle={selectedVehicleForDetail}
    marketKey={selectedMarketKeyForDetail}
    isOpen={isDetailModalOpen}
    on:close={() => isDetailModalOpen = false}
    on:validate={(e) => handleOpenValidationModal({ detail: e.detail })}
  />

  <SettingsModal 
    isOpen={isSettingsModalOpen}
    on:close={() => isSettingsModalOpen = false}
    on:configSaved={() => { fetchVehicles(); fetchStats(); }}
  />
</div>

<style>
  .app-root {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  main {
    flex: 1;
  }
</style>
