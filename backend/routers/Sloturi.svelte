<script>
  import { createEventDispatcher, onMount } from 'svelte'
  import { getSloturiZi } from './api.js'

  export let data = null

  const dispatch = createEventDispatcher()

  let sloturi = []
  let loading = false
  let eroare = null
  let slotSelectat = null

  $: if (data) incarcaSloturi(data)

  async function incarcaSloturi(d) {
    loading = true
    eroare = null
    slotSelectat = null
    sloturi = []
    try {
      sloturi = await getSloturiZi(d)
    } catch (e) {
      eroare = e.message
    } finally {
      loading = false
    }
  }

  function selectSlot(slot) {
    if (slot.ocupat) return
    slotSelectat = slot
    dispatch('select', slot)
  }

  function formatData(iso) {
    if (!iso) return ''
    const [an, l, z] = iso.split('-')
    const luni = ['ian', 'feb', 'mar', 'apr', 'mai', 'iun', 'iul', 'aug', 'sep', 'oct', 'noi', 'dec']
    return `${parseInt(z)} ${luni[parseInt(l) - 1]} ${an}`
  }
</script>

<div class="sloturi-container">
  {#if !data}
    <div class="placeholder">
      <span class="icon">📅</span>
      <p>Selectează o zi din calendar pentru a vedea sloturile disponibile.</p>
    </div>
  {:else if loading}
    <div class="loading">
      <div class="spinner"></div>
      <p>Se încarcă sloturile...</p>
    </div>
  {:else if eroare}
    <div class="eroare">
      <span>⚠️ {eroare}</span>
      <button on:click={() => incarcaSloturi(data)}>Reîncearcă</button>
    </div>
  {:else}
    <div class="header-sloturi">
      <h3>{formatData(data)}</h3>
      <span class="count">
        {sloturi.filter(s => !s.ocupat).length} sloturi libere
      </span>
    </div>

    {#if sloturi.length === 0}
      <div class="placeholder">
        <span class="icon">🚫</span>
        <p>Nu există sloturi pentru această zi.</p>
      </div>
    {:else}
      <div class="grid">
        {#each sloturi as slot}
          <button
            class="slot"
            class:liber={!slot.ocupat}
            class:ocupat={slot.ocupat}
            class:selectat={slotSelectat?.id === slot.id}
            disabled={slot.ocupat}
            on:click={() => selectSlot(slot)}
            title={slot.ocupat ? 'Slot ocupat' : `Durată: ${slot.durata} min`}
          >
            <span class="ora">{slot.ora}</span>
            <span class="durata">{slot.durata} min</span>
            {#if slot.ocupat}
              <span class="status-badge ocupat-badge">Ocupat</span>
            {:else if slotSelectat?.id === slot.id}
              <span class="status-badge selectat-badge">✓</span>
            {/if}
          </button>
        {/each}
      </div>
    {/if}
  {/if}
</div>

<style>
  .sloturi-container {
    background: var(--bg-card);
    border: 0.5px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    min-height: 200px;
  }

  .header-sloturi {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 16px;
  }

  h3 {
    font-size: 15px;
    font-weight: 500;
    margin: 0;
    color: var(--text-primary);
    text-transform: capitalize;
  }

  .count {
    font-size: 12px;
    color: var(--text-muted);
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
    gap: 8px;
  }

  .slot {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 10px 6px;
    border-radius: 8px;
    border: 0.5px solid var(--border);
    background: var(--bg-card);
    cursor: pointer;
    gap: 2px;
    transition: all 0.12s;
  }

  .slot.liber:hover:not(.selectat) {
    border-color: var(--accent);
    background: var(--accent-light);
  }

  .slot.selectat {
    background: var(--accent);
    border-color: var(--accent);
  }

  .slot.selectat .ora,
  .slot.selectat .durata {
    color: white;
  }

  .slot.ocupat {
    opacity: 0.45;
    cursor: not-allowed;
    background: var(--bg-hover);
  }

  .ora {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
  }

  .durata {
    font-size: 11px;
    color: var(--text-muted);
  }

  .status-badge {
    position: absolute;
    top: 4px;
    right: 4px;
    font-size: 9px;
    padding: 1px 4px;
    border-radius: 4px;
  }

  .ocupat-badge {
    background: #fee2e2;
    color: #ef4444;
  }

  .selectat-badge {
    background: rgba(255,255,255,0.3);
    color: white;
    font-size: 11px;
  }

  .placeholder, .loading, .eroare {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 40px 20px;
    color: var(--text-muted);
    text-align: center;
  }

  .icon { font-size: 28px; }

  .placeholder p, .loading p {
    font-size: 13px;
    margin: 0;
    max-width: 220px;
  }

  .spinner {
    width: 24px;
    height: 24px;
    border: 2px solid var(--border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  .eroare {
    color: #ef4444;
  }

  .eroare button {
    font-size: 12px;
    padding: 4px 12px;
    border: 0.5px solid #ef4444;
    border-radius: 6px;
    background: none;
    color: #ef4444;
    cursor: pointer;
  }
</style>
