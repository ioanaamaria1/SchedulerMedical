<script>
  import { onMount } from 'svelte';
  import { getListaAsteptare, addToListaAsteptare, deleteFromListaAsteptare, getPacienti } from './api.js';
  import AdaugaPacient from './AdaugaPacient.svelte'; 

  let listaAsteptare = [];
  let listaPacienti = [];
  let seIncarca = true;
  
  let arataFormular = false;
  let seSalveaza = false;
  let arataDialogPacientNou = false; 

  let formPacientId = '';
  let formTip = 'Consultatie';
  let formDataPreferata = '';

  onMount(async () => {
    seIncarca = true;
    try {
      const [asteptareRes, pacientiRes] = await Promise.all([
        getListaAsteptare().catch(() => []),
        getPacienti().catch(() => [])
      ]);
      listaAsteptare = asteptareRes;
      listaPacienti = pacientiRes;
    } catch (err) {
      console.error(err);
    } finally {
      seIncarca = false;
    }
  });

  async function incarcaListaAsteptare() {
    try {
      listaAsteptare = await getListaAsteptare();
    } catch (e) {}
  }

  async function salveaza() {
    if (!formPacientId) { alert("Te rog selecteaza un pacient!"); return; }
    seSalveaza = true;
    try {
      await addToListaAsteptare({ pacienti_id: parseInt(formPacientId), type: formTip, data_preferata: formDataPreferata || null });
      formPacientId = ''; formTip = 'Consultatie'; formDataPreferata = ''; arataFormular = false;
      await incarcaListaAsteptare();
    } catch (err) {
      alert("Eroare la salvare: " + err.message);
    } finally {
      seSalveaza = false;
    }
  }

  async function sterge(id) {
    if (confirm("Elimini acest pacient din lista de asteptare?")) {
      try {
        await deleteFromListaAsteptare(id);
        listaAsteptare = listaAsteptare.filter(item => item.id !== id);
      } catch (err) {}
    }
  }

  function getNumePacient(id) {
    const p = listaPacienti.find(pac => pac.id === id);
    return p ? p.nume : `Pacient #${id}`;
  }
</script>

<div class="card-asteptare">
  <div class="card-header">
    <div class="header-titlu">
      <h3>Lista de asteptare</h3>
      <span class="intrari">{listaAsteptare.length} intrari</span>
    </div>
    <div class="actiuni-dreapta">
      <button class="btn-pacient-nou" on:click={() => arataDialogPacientNou = true} title="Inregistreaza un pacient nou">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="17" y1="11" x2="23" y2="11"/>
        </svg>
      </button>
      <button class="btn-adauga-sus" on:click={() => arataFormular = true}>+ Adauga</button>
    </div>
  </div>

  <div class="card-body">
    {#if seIncarca}
      <div class="stare-goala">Se incarca...</div>
    {:else if listaAsteptare.length === 0}
      <div class="stare-goala"><span class="icon-clepsidra">⏳</span><p>Lista este goala</p></div>
    {:else}
      <div class="lista-items">
        {#each listaAsteptare as item}
          <div class="item-asteptare">
            <div class="item-info">
              <div class="item-nume">{getNumePacient(item.pacienti_id)}</div>
              <div class="item-detalii">{item.type || item.tip}</div>
              {#if item.data_preferata}
                <div class="item-data-pref">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
                  </svg>
                  Data preferata: <strong>{item.data_preferata}</strong>
                </div>
              {/if}
            </div>
            <button class="btn-sterge-item" on:click={() => sterge(item.id)}>✕</button>
          </div>
        {/each}
      </div>
    {/if}
  </div>

  {#if arataFormular}
    <div class="card-footer-form">
      <div class="form-header"><h4>Adauga in lista</h4><button class="btn-inchide" on:click={() => arataFormular = false}>✕</button></div>
      <div class="form-group"><label>Pacient</label><select bind:value={formPacientId} disabled={seSalveaza}><option value="">— Selecteaza pacient —</option>{#each listaPacienti as p}<option value={p.id}>{p.nume}</option>{/each}</select></div>
      <div class="form-group"><label>Tip consultatie</label><select bind:value={formTip} disabled={seSalveaza}><option value="Consultatie">Consultatie</option><option value="Control">Control</option><option value="Analize">Analize</option><option value="Urgenta">Urgenta</option></select></div>
      <div class="form-group"><label>Data preferata (optional)</label><input type="date" bind:value={formDataPreferata} disabled={seSalveaza} /></div>
      <button class="btn-salveaza-plin" on:click={salveaza} disabled={seSalveaza}>{seSalveaza ? 'Se proceseaza...' : 'Salveaza'}</button>
    </div>
  {/if}
</div>

<AdaugaPacient bind:esteVizibil={arataDialogPacientNou} />

<style>
  .card-asteptare { background: white; border: 1px solid #e2e8f0; border-radius: 8px; width: 100%; max-width: 400px; display: flex; flex-direction: column; overflow: hidden; }
  .card-header { display: flex; justify-content: space-between; align-items: center; padding: 16px; border-bottom: 1px solid #e2e8f0; }
  .header-titlu h3 { margin: 0; font-size: 15px; font-weight: 600; color: #0f172a; }
  .intrari { font-size: 12px; color: #94a3b8; }
  .actiuni-dreapta { display: flex; gap: 8px; align-items: center; }
  .btn-pacient-nou { background: white; color: #0d9488; border: 1px solid #0d9488; padding: 5px 8px; border-radius: 6px; cursor: pointer; display: flex; align-items: center; transition: 0.2s; }
  .btn-pacient-nou:hover { background: #f0fdfa; }
  .btn-adauga-sus { background: #0d9488; color: white; border: none; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 500; cursor: pointer; transition: 0.2s; }
  .btn-adauga-sus:hover { background: #0f766e; }
  .card-body { padding: 20px; min-height: 150px; display: flex; flex-direction: column; }
  .stare-goala { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: #cbd5e1; font-size: 13px; margin-top: 20px; }
  .icon-clepsidra { font-size: 32px; margin-bottom: 8px; opacity: 0.5; }
  .lista-items { display: flex; flex-direction: column; gap: 8px; }
  .item-asteptare { display: flex; justify-content: space-between; align-items: flex-start; padding: 10px; background: #f8fafc; border: 1px solid #f1f5f9; border-radius: 6px; }
  .item-info { display: flex; flex-direction: column; }
  .item-nume { font-size: 13px; font-weight: 600; color: #334155; }
  .item-detalii { font-size: 11px; color: #64748b; margin-top: 2px; }
  .item-data-pref { display: flex; align-items: center; gap: 4px; font-size: 11px; color: #0369a1; background: #e0f2fe; padding: 4px 8px; border-radius: 6px; margin-top: 6px; width: fit-content; border: 1px solid #bae6fd; }
  .item-data-pref strong { font-weight: 700; }
  .btn-sterge-item { background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 14px; padding: 4px; }
  .btn-sterge-item:hover { color: #ef4444; }
  .card-footer-form { background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 16px; }
  .form-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
  .form-header h4 { margin: 0; font-size: 13px; font-weight: 600; color: #0f172a; }
  .btn-inchide { background: none; border: none; font-size: 14px; color: #94a3b8; cursor: pointer; }
  .btn-inchide:hover { color: #334155; }
  .form-group { display: flex; flex-direction: column; margin-bottom: 12px; }
  .form-group label { font-size: 11px; color: #475569; margin-bottom: 4px; }
  .form-group select, .form-group input { padding: 8px 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 13px; color: #334155; background: white; outline: none; }
  .form-group select:focus, .form-group input:focus { border-color: #0d9488; }
  .btn-salveaza-plin { width: 100%; background: #0d9488; color: white; border: none; padding: 10px; border-radius: 6px; font-weight: 600; font-size: 13px; cursor: pointer; margin-top: 8px; transition: 0.2s; }
  .btn-salveaza-plin:hover:not(:disabled) { background: #0f766e; }
  .btn-salveaza-plin:disabled { opacity: 0.6; cursor: not-allowed; }
</style>