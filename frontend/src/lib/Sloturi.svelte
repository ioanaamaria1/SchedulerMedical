<script>
  import { getSloturiZi } from './api.js';
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();
  
  export let data; 
  
  let sloturi = [];
  let seIncarca = false;

  $: if (data) {
    incarcaSloturi(data);
  }

  async function incarcaSloturi(dataSelectata) {
    seIncarca = true;
    try {
      sloturi = await getSloturiZi(dataSelectata);
    } catch (e) {
      console.error("Eroare la incarcare sloturi:", e);
    } finally {
      seIncarca = false;
    }
  }

  function selecteazaSlot(slot) {
    if (slot.ocupat) return;
    dispatch('select', slot);
  }
</script>

<div class="panel-sloturi">
  <div class="panel-header">Intervale Orare - {data || 'Selecteaza o zi'}</div>
  
  {#if seIncarca}
    <p class="msg">Se incarca...</p>
  {:else if sloturi.length === 0}
    <p class="msg">Nu sunt sloturi generate.</p>
  {:else}
    <div class="grid-sloturi">
      {#each sloturi as s}
        <button 
          class="slot-btn" 
          class:ocupat={s.ocupat} 
          disabled={s.ocupat}
          on:click={() => selecteazaSlot(s)}
        >
          {s.ora}
        </button>
      {/each}
    </div>
  {/if}
</div>

<style>
  .panel-sloturi {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px;
    margin-top: 16px;
  }
  .panel-header { font-weight: 600; margin-bottom: 12px; font-size: 14px; }
  .grid-sloturi {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
  }
  .slot-btn {
    padding: 8px;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    background: #f8fafc;
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
  }
  .slot-btn:hover:not(:disabled) { background: #0ea5e9; color: white; border-color: #0ea5e9; }
  .slot-btn.ocupat {
    background: #fee2e2;
    color: #ef4444;
    cursor: not-allowed;
    border-color: #fecaca;
  }
  .msg { font-size: 13px; color: #64748b; text-align: center; }
</style>