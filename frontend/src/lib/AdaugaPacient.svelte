<script>
  import { createPacient } from './api.js';

  export let esteVizibil = false;

  let pacient = {
    cnp: '',
    nume: '',
    telefon: '',
    email: ''
  };

  let seSalveaza = false;
  let mesajEroare = null;

  async function handleSubmit() {
    if (!pacient.cnp || !pacient.nume) {
      mesajEroare = "CNP-ul si Numele sunt obligatorii!";
      return;
    }

    seSalveaza = true;
    mesajEroare = null;

    try {
      await createPacient(pacient);
      
      alert(`Pacientul ${pacient.nume} a fost adaugat!`);
      inchide();
      
      window.location.reload();
    } catch (err) {
      // MAGIA SE ÎNTÂMPLĂ AICI:
      // Verificăm dacă primim 'detail' (cum trimite FastAPI)
      if (err && err.detail) {
        mesajEroare = err.detail;
      }
      // Altfel, dacă e o eroare normală de JS și nu e [object Object]
      else if (err && err.message && !err.message.includes('[object Object]')) {
        mesajEroare = "Eroare: " + err.message;
      }
      // Dacă eroarea a fost "strivită" pe drum, afișăm mesajul nostru
      else {
        mesajEroare = "Eroare la salvare! Verificați ca CNP-ul să aibă 13 cifre.";
      }
    } finally {
      seSalveaza = false;
    }
  }

  function inchide() {
    esteVizibil = false;
    pacient = { cnp: '', nume: '', telefon: '', email: '' };
    mesajEroare = null;
  }
</script>

{#if esteVizibil}
<div class="overlay" on:click|self={inchide}>
  <div class="dialog">
    <button class="close-x" on:click={inchide}>✕</button>
    <h2>Adauga Pacient Nou</h2>

    {#if mesajEroare}
      <p class="error">{mesajEroare}</p>
    {/if}

    <div class="form">
      <label for="cnp">CNP *</label>
      <input id="cnp" type="text" bind:value={pacient.cnp} placeholder="ex: 190..." />

      <label for="nume">Nume Complet *</label>
      <input id="nume" type="text" bind:value={pacient.nume} placeholder="Nume Prenume" />

      <label for="tel">Telefon</label>
      <input id="tel" type="text" bind:value={pacient.telefon} placeholder="07xx..." />

      <label for="email">Email</label>
      <input id="email" type="email" bind:value={pacient.email} placeholder="exemplu@mail.com" />

      <div class="actions">
        <button class="btn-cancel" on:click={inchide}>Anuleaza</button>
        <button class="btn-save" on:click={handleSubmit} disabled={seSalveaza}>
          {seSalveaza ? 'Se salveaza...' : 'Salveaza Pacient'}
        </button>
      </div>
    </div>
  </div>
</div>
{/if}

<style>
  .overlay {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.6); display: flex; justify-content: center; align-items: center; z-index: 1100;
  }
  .dialog {
    background: white; padding: 2rem; border-radius: 12px; width: 400px; position: relative;
  }
  .close-x { position: absolute; top: 1rem; right: 1rem; border: none; background: none; cursor: pointer; font-size: 1.2rem; }
  h2 { margin-top: 0; color: #333; }
  .form { display: flex; flex-direction: column; gap: 0.8rem; }
  label { font-size: 0.9rem; font-weight: bold; color: #555; }
  input { padding: 0.6rem; border: 1px solid #ccc; border-radius: 6px; }
  .error { color: white; background: #d9534f; padding: 0.5rem; border-radius: 4px; font-size: 0.8rem; }
  .actions { display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 1rem; }
  .btn-save { background: #9c27b0; color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 6px; cursor: pointer; font-weight: bold; }
  .btn-cancel { background: #eee; border: none; padding: 0.6rem 1.2rem; border-radius: 6px; cursor: pointer; }
</style>