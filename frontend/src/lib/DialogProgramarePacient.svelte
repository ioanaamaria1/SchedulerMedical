<script>
  import { createEventDispatcher, onMount } from 'svelte';
  export let slot;
  export let data;

  const dispatch = createEventDispatcher();

  // Datele pe care le completeaza pacientul
  let nume = '';
  let cnp = '';
  let telefon = '';
  let tip_programare = 'Consultație de rutină';
  let isLoading = false;

  async function rezervaProgramarea() {
    isLoading = true;
    try {
      // Luăm ID-ul pacientului salvat la login
      const p_id = localStorage.getItem('pacient_id');
      if (!p_id || p_id === 'null') {
        throw new Error("Eroare de sesiune. Te rog să te reloghezi.");
      }

      // 1. Facem programarea în backend
      const res = await fetch('http://127.0.0.1:8000/programari', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pacienti_id: parseInt(p_id),
          slot_id: slot.id || slot.slot_id, 
          type: tip_programare
        })
      });

      if (!res.ok) throw new Error("A apărut o eroare la salvarea programării.");

      // 2. Trimitem datele noi (Nume, CNP, Tel) în backend pentru a inlocui numele provizoriu
      try {
        await fetch(`http://127.0.0.1:8000/api/pacienti/${p_id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ nume: nume, cnp: cnp, phone: telefon })
        });
      } catch (e) { 
        console.error("Eroare la actualizarea numelui: ", e); 
      }

      // Trimitem semnal catre App.svelte ca am terminat
      dispatch('success');
    } catch (err) {
      alert(err.message);
    } finally {
      isLoading = false;
    }
  }
</script>

<div class="modal-backdrop">
  <div class="modal">
    <button class="btn-close" on:click={() => dispatch('close')}>&times;</button>
    
    <h3>Rezervare Programare</h3>
    <p class="subtitle">Data: <strong>{data}</strong> &bull; Ora: <strong>{slot.start_time || slot.ora || '--:--'}</strong></p>

    <div class="form-container">
      <div class="input-group">
        <label>Nume complet</label>
        <input type="text" bind:value={nume} placeholder="Ex: Popescu Ion" />
      </div>

      <div class="row">
        <div class="input-group">
          <label>CNP</label>
          <input type="text" bind:value={cnp} placeholder="Pentru fișa medicală" />
        </div>
        <div class="input-group">
          <label>Telefon</label>
          <input type="text" bind:value={telefon} placeholder="07XX XXX XXX" />
        </div>
      </div>

      <div class="input-group">
        <label>Motivul vizitei</label>
        <select bind:value={tip_programare}>
          <option>Consultație inițială</option>
          <option>Consultație de rutină</option>
          <option>Control / Interpretare analize</option>
          <option>Tratament / Intervenție</option>
          <option>Urgență</option>
        </select>
      </div>
    </div>

    <button class="btn-submit" on:click={rezervaProgramarea} disabled={isLoading}>
      {isLoading ? 'Se procesează...' : 'Confirmă Programarea'}
    </button>
  </div>
</div>

<style>
  .modal-backdrop {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px);
    display: flex; align-items: center; justify-content: center; z-index: 1000;
  }
  .modal {
    background: white; width: 100%; max-width: 450px; padding: 32px;
    border-radius: 20px; position: relative; box-shadow: 0 20px 40px rgba(0,0,0,0.1);
  }
  .btn-close {
    position: absolute; top: 16px; right: 16px; background: #f1f5f9; border: none;
    width: 32px; height: 32px; border-radius: 50%; font-size: 18px; cursor: pointer; color: #64748b;
  }
  .btn-close:hover { background: #e2e8f0; color: #0f172a; }
  h3 { margin: 0 0 8px 0; color: #0f172a; font-size: 22px; }
  .subtitle { color: #0d9488; font-weight: 600; margin-bottom: 24px; font-size: 15px; }
  
  .form-container { display: flex; flex-direction: column; gap: 16px; margin-bottom: 24px; }
  .row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .input-group { display: flex; flex-direction: column; gap: 6px; }
  .input-group label { font-size: 13px; font-weight: 600; color: #475569; }
  input, select {
    padding: 12px; border: 1px solid #cbd5e1; border-radius: 10px; font-size: 14px;
    outline: none; transition: 0.2s; background: #f8fafc;
  }
  input:focus, select:focus { border-color: #0d9488; background: white; }
  
  .btn-submit {
    width: 100%; padding: 14px; background: #0d9488; color: white; border: none;
    border-radius: 12px; font-size: 15px; font-weight: 700; cursor: pointer; transition: 0.2s;
  }
  .btn-submit:hover:not(:disabled) { background: #0f766e; transform: translateY(-1px); }
  .btn-submit:disabled { opacity: 0.7; cursor: not-allowed; }
</style>