<script>
  import { createProgramare, getPacienti, getListaAsteptare } from './api.js';
  import { createEventDispatcher, onMount } from 'svelte';

  export let slot;
  export let data;

  const dispatch = createEventDispatcher();

  let listaPacienti = [];
  let pacientiCareAsteaptaDataAsta = []; 

  let idPacientSelectat = "";
  let tipProgramare = 'consultatie';
  
  let seIncarcaDate = true;
  let seSalveaza = false;
  let mesajEroare = null;

  onMount(async () => {
    try {
      const [pacientiRes, asteptareRes] = await Promise.all([
        getPacienti().catch(() => []),
        getListaAsteptare().catch(() => [])
      ]);
      
      listaPacienti = pacientiRes;
      const cautariPentruAzi = asteptareRes.filter(item => item.data_preferata === data);
      
      pacientiCareAsteaptaDataAsta = cautariPentruAzi.map(entry => {
        const p = listaPacienti.find(pac => pac.id === entry.pacienti_id);
        return p ? p.nume : `Pacient #${entry.pacienti_id}`;
      });
    } catch (err) {
      mesajEroare = "Nu am putut incarca lista de pacienti.";
    } finally {
      seIncarcaDate = false;
    }
  });

  async function handleSubmit() {
    if (!idPacientSelectat) { mesajEroare = "Te rog selecteaza un pacient din lista!"; return; }
    seSalveaza = true; mesajEroare = null;
    try {
      const dateDeTrimis = { pacienti_id: parseInt(idPacientSelectat), slot_id: slot.id, type: tipProgramare };
      await createProgramare(dateDeTrimis);
      dispatch('success');
    } catch (err) {
      mesajEroare = "Eroare la salvare: " + err.message;
    } finally {
      seSalveaza = false;
    }
  }

  function close() { dispatch('close'); }
</script>

<div class="overlay" on:click|self={close}>
  <div class="dialog">
    <button class="close-btn" on:click={close}>✕</button>
    
    <h2>Programare Noua</h2>
    
    <div class="info-slot"><span>📅 {data}</span><span>⏰ {slot.ora}</span></div>

    {#if pacientiCareAsteaptaDataAsta.length > 0}
      <div class="alerta-asteptare">
        <div class="alerta-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
        </div>
        <div class="alerta-text">
          <strong>Sfat pentru medic:</strong>
          Urmatorii pacienti de pe lista de asteptare prefera aceasta data:
          <ul>
            {#each pacientiCareAsteaptaDataAsta as nume}
              <li>{nume}</li>
            {/each}
          </ul>
        </div>
      </div>
    {/if}

    {#if mesajEroare}<div class="alerta-eroare">{mesajEroare}</div>{/if}

    <div class="form">
      <div class="field">
        <label>Selecteaza Pacientul</label>
        {#if seIncarcaDate}
          <div class="loading-input">Se incarca pacientii...</div>
        {:else}
          <select bind:value={idPacientSelectat} disabled={seSalveaza}>
            <option value="">-- Alege un pacient --</option>
            {#each listaPacienti as p}<option value={p.id}>{p.nume} (CNP: {p.cnp})</option>{/each}
          </select>
        {/if}
      </div>

      <div class="field">
        <label>Tip Serviciu</label>
        <select bind:value={tipProgramare} disabled={seSalveaza}>
          <option value="consultatie">Consultatie</option><option value="control">Control</option><option value="analize">Analize</option><option value="urgenta">Urgenta</option>
        </select>
      </div>

      <div class="actions">
        <button class="btn-secondary" on:click={close}>Anuleaza</button>
        <button class="btn-primary" on:click={handleSubmit} disabled={seSalveaza || seIncarcaDate}>
          {seSalveaza ? 'Se salveaza...' : 'Finalizeaza Programarea'}
        </button>
      </div>
    </div>
  </div>
</div>

<style>
  .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(4px); display: flex; justify-content: center; align-items: center; z-index: 2000; }
  .dialog { background: white; width: 420px; padding: 28px; border-radius: 16px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); position: relative; }
  .close-btn { position: absolute; top: 18px; right: 18px; background: none; border: none; font-size: 20px; color: #94a3b8; cursor: pointer; }
  h2 { margin: 0 0 20px 0; font-size: 22px; color: #1e293b; }
  .info-slot { display: flex; gap: 15px; background: #f1f5f9; padding: 12px; border-radius: 10px; margin-bottom: 20px; font-weight: 600; color: #475569; }
  .alerta-asteptare { display: flex; gap: 12px; background: #fffbeb; border: 1px solid #fde68a; padding: 14px; border-radius: 10px; margin-bottom: 20px; color: #92400e; }
  .alerta-icon { color: #d97706; margin-top: 2px; }
  .alerta-text { font-size: 13px; line-height: 1.4; }
  .alerta-text strong { color: #b45309; display: block; margin-bottom: 4px; }
  .alerta-text ul { margin: 6px 0 0 0; padding-left: 18px; color: #b45309; font-weight: 600;}
  .alerta-text li { margin-bottom: 2px; }
  .form { display: flex; flex-direction: column; gap: 18px; }
  .field { display: flex; flex-direction: column; gap: 6px; }
  label { font-size: 13px; font-weight: 600; color: #64748b; }
  select, .loading-input { padding: 11px; border: 1px solid #e2e8f0; border-radius: 8px; background: #fff; outline: none; font-size: 14px; }
  select:focus { border-color: #0d9488; box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.1); }
  .loading-input { color: #94a3b8; font-style: italic; background: #f8fafc; }
  .alerta-eroare { background: #fef2f2; color: #dc2626; padding: 12px; border-radius: 8px; font-size: 13px; margin-bottom: 15px; border: 1px solid #fee2e2; }
  .actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 10px; }
  .btn-primary { background: #0d9488; color: white; border: none; padding: 11px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: 0.2s; }
  .btn-primary:hover:not(:disabled) { background: #0f766e; }
  .btn-secondary { background: #fff; color: #64748b; border: 1px solid #e2e8f0; padding: 11px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; }
  button:disabled { opacity: 0.6; cursor: not-allowed; }
</style>