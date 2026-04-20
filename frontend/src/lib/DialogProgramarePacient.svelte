<script>
  import { createEventDispatcher, onMount } from 'svelte';
  export let slot;
  export let data;

  const dispatch = createEventDispatcher();

  let nume = '';
  let cnp = '';
  let telefon = '';
  let tip_programare = 'Consultație de rutină';
  let isLoading = false;
  let isFetchingData = true;

  $: cnp = cnp.replace(/[^0-9]/g, '').slice(0, 13);
  $: telefon = telefon.replace(/[^0-9]/g, '').slice(0, 10);

  onMount(async () => {
    const p_id = localStorage.getItem('pacient_id');
    if (p_id && p_id !== 'null') {
      try {
        const res = await fetch(`http://127.0.0.1:8000/pacienti/${p_id}?t=${Date.now()}`);
        if (res.ok) {
          const datePacient = await res.json();
          nume = datePacient.nume || '';
          telefon = (datePacient.phone && datePacient.phone !== '-') ? datePacient.phone : '';
          cnp = (datePacient.cnp && !datePacient.cnp.startsWith('T-')) ? datePacient.cnp : '';
        }
      } catch (e) { console.error("Eroare detalii:", e); }
    }
    isFetchingData = false;
  });

  async function rezervaProgramarea() {
    if (nume.trim().length < 3) { alert("Te rog să introduci un nume valid."); return; }
    if (cnp.length > 0 && cnp.length !== 13) { alert("CNP-ul trebuie să aibă 13 cifre!"); return; }
    if (telefon.length > 0 && telefon.length !== 10) { alert("Numărul de telefon trebuie să aibă 10 cifre!"); return; }

    isLoading = true;
    try {
      const p_id = localStorage.getItem('pacient_id');
      const res = await fetch('http://127.0.0.1:8000/programari/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pacienti_id: parseInt(p_id),
          slot_id: slot.id || slot.slot_id, 
          type: tip_programare
        })
      });

      const dataRes = await res.json();
      if (!res.ok) throw new Error(dataRes.detail || "Eroare la salvarea programării.");

      try {
        await fetch(`http://127.0.0.1:8000/pacienti/${p_id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ nume: nume, cnp: cnp, phone: telefon })
        });
      } catch (e) { console.error(e); }

      dispatch('success');
    } catch (err) {
      alert(err.message);
    } finally {
      isLoading = false;
    }
  }
</script>

<div class="modal-overlay" on:click|self={() => dispatch('close')}>
  <div class="modal-content animate-pop">
    <button class="btn-close-modal" on:click={() => dispatch('close')} aria-label="Închide">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
    </button>
    
    <div class="modal-header">
      <div class="modal-icon">📅</div>
      <div>
        <h3 class="modal-title">Finalizare Programare</h3>
        <p class="modal-meta">{data} &bull; Ora {slot.start_time || slot.ora}</p>
      </div>
    </div>

    {#if isFetchingData}
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Se pregătește formularul...</p>
      </div>
    {:else}
      <div class="form-body">
        <div class="input-block">
          <label>Nume complet pacient</label>
          <input type="text" bind:value={nume} placeholder="Ex: Popescu Ion" autocomplete="new-password" />
        </div>

        <div class="input-row">
          <div class="input-block">
            <label>CNP</label>
            <input type="text" bind:value={cnp} placeholder="13 cifre" autocomplete="new-password" />
          </div>
          <div class="input-block">
            <label>Telefon Contact</label>
            <input type="text" bind:value={telefon} placeholder="07XX XXX XXX" autocomplete="new-password" />
          </div>
        </div>

        <div class="input-block">
          <label>Motivul vizitei medicale</label>
          <div class="select-wrapper">
            <select bind:value={tip_programare}>
              <option>Consultație inițială</option>
              <option>Consultație de rutină</option>
              <option>Control / Interpretare analize</option>
              <option>Tratament / Intervenție</option>
              <option>Urgență medicală</option>
            </select>
            <div class="select-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-cancel" on:click={() => dispatch('close')} disabled={isLoading}>Anulează</button>
        <button class="btn-confirm" on:click={rezervaProgramarea} disabled={isLoading}>
          {isLoading ? 'Se procesează...' : 'Confirmă Programarea'}
        </button>
      </div>
    {/if}
  </div>
</div>

<style>
  .modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 9999; padding: 1rem; }
  .modal-content { background: #ffffff; width: 100%; max-width: 480px; border-radius: 20px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); position: relative; overflow: hidden; display: flex; flex-direction: column; font-family: 'Inter', sans-serif; }
  
  .btn-close-modal { position: absolute; top: 1.25rem; right: 1.25rem; width: 32px; height: 32px; border-radius: 50%; background: #f1f5f9; border: none; color: #64748b; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s; z-index: 10; }
  .btn-close-modal:hover { background: #e2e8f0; color: #0f172a; }

  .modal-header { padding: 2rem 2rem 1.5rem; display: flex; align-items: center; gap: 1rem; border-bottom: 1px solid #f1f5f9; background: #fcfcfd;}
  .modal-icon { width: 48px; height: 48px; background: #f0fdfa; color: #0d9488; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; flex-shrink: 0;}
  .modal-title { margin: 0; font-size: 1.25rem; font-weight: 700; color: #0f172a; letter-spacing: -0.02em; }
  .modal-meta { margin: 0.25rem 0 0 0; font-size: 0.875rem; font-weight: 600; color: #0d9488; }

  .form-body { padding: 1.5rem 2rem; display: flex; flex-direction: column; gap: 1.25rem; }
  .input-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
  .input-block { display: flex; flex-direction: column; gap: 0.5rem; }
  .input-block label { font-size: 0.8125rem; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; }
  
  input, select { width: 100%; box-sizing: border-box; padding: 0.875rem 1rem; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 0.9375rem; color: #0f172a; background: #f8fafc; transition: all 0.2s; outline: none; font-family: inherit; }
  input:hover, select:hover { border-color: #cbd5e1; }
  input:focus, select:focus { border-color: #0d9488; background: white; box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.1); }
  
  .select-wrapper { position: relative; }
  select { appearance: none; padding-right: 2.5rem; cursor: pointer; }
  .select-icon { position: absolute; right: 1rem; top: 50%; transform: translateY(-50%); color: #64748b; pointer-events: none; display: flex; }

  .modal-footer { padding: 1.25rem 2rem; background: #f8fafc; border-top: 1px solid #f1f5f9; display: flex; justify-content: flex-end; gap: 0.75rem; }
  button { font-family: inherit; font-size: 0.9375rem; font-weight: 600; padding: 0.625rem 1.25rem; border-radius: 8px; cursor: pointer; transition: all 0.2s; }
  .btn-cancel { background: white; border: 1px solid #e2e8f0; color: #475569; }
  .btn-cancel:hover:not(:disabled) { background: #f1f5f9; color: #0f172a; }
  .btn-confirm { background: #0d9488; border: 1px solid #0d9488; color: white; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
  .btn-confirm:hover:not(:disabled) { background: #0f766e; border-color: #0f766e; }
  button:disabled { opacity: 0.6; cursor: not-allowed; }

  .loading-state { padding: 3rem; display: flex; flex-direction: column; align-items: center; gap: 1rem; color: #64748b; font-size: 0.9375rem; }
  .spinner { width: 24px; height: 24px; border: 3px solid #e2e8f0; border-top-color: #0d9488; border-radius: 50%; animation: spin 0.8s linear infinite; }

  @keyframes popIn { from { opacity: 0; transform: scale(0.95) translateY(10px); } to { opacity: 1; transform: scale(1) translateY(0); } }
  @keyframes spin { to { transform: rotate(360deg); } }
  .animate-pop { animation: popIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
</style>