<script>
  import { onMount } from 'svelte'
  import Calendar from './lib/Calendar.svelte'
  import Sloturi from './lib/Sloturi.svelte'
  import DialogProgramare from './lib/DialogProgramare.svelte'
  import DialogProgramarePacient from './lib/DialogProgramarePacient.svelte'
  import ListaAsteptare from './lib/ListaAsteptare.svelte'
  import AdaugaPacient from './lib/AdaugaPacient.svelte'
  import { getProgramari, getPacienti, deletePacient } from './lib/api.js'

  let isAuthenticated = false;
  let userRole = null; 
  let authMode = 'login'; 
  let emailInput = '';
  let parolaInput = '';
  let isLoadingAuth = false;

  let tab = 'programari'
  let dataSelectata = null
  let slotSelectat = null
  let dialogOpen = false
  let arataDialogPacient = false
  let toast = null
  let toastTimer = null
  
  let programariAzi = []
  let programariViitoare = [] 
  let listaTotiPacientii = []
  let programariPacient = []

  const azi = new Date()
  const isoAzi = azi.toLocaleDateString('sv-SE')
  const ZILE_LUNG = ['Duminica', 'Luni', 'Marti', 'Miercuri', 'Joi', 'Vineri', 'Sambata']
  const LUNI_LUNG = ['Ian', 'Feb', 'Mar', 'Apr', 'Mai', 'Iun', 'Iul', 'Aug', 'Sep', 'Oct', 'Noi', 'Dec']

  function formatDataLung(d) {
    return `${ZILE_LUNG[d.getDay()]}, ${d.getDate()} ${LUNI_LUNG[d.getMonth()]} ${d.getFullYear()}`
  }

  function formateazaNume(nume) {
    if (!nume) return '';
    return nume.toLowerCase().split(' ').map(cuvant => cuvant.charAt(0).toUpperCase() + cuvant.slice(1)).join(' ');
  }

  onMount(() => {
    const token = localStorage.getItem('token');
    const rol = localStorage.getItem('rol');
    if (token && rol) {
      isAuthenticated = true;
      userRole = rol;
      if (userRole === 'doctor') incarcaDateDoctor();
      if (userRole === 'pacient') incarcaDatePacient();
    }
  })

  async function incarcaDateDoctor() {
    try {
      const toate = await getProgramari();
      programariAzi = toate.filter(p => p.data === isoAzi).sort((a, b) => a.ora.localeCompare(b.ora));
      programariViitoare = toate.filter(p => p.data > isoAzi).sort((a, b) => a.data.localeCompare(b.data) || a.ora.localeCompare(b.ora));
      getPacienti().then(res => listaTotiPacientii = res).catch(() => {});
    } catch(e) { console.error(e); }
  }

  async function incarcaDatePacient() {
    try {
      const pid = localStorage.getItem('pacient_id');
      if(!pid) return;
      const toate = await getProgramari();
      programariPacient = toate.filter(p => p.pacienti_id === parseInt(pid) && p.data >= isoAzi)
                             .sort((a, b) => a.data.localeCompare(b.data) || a.ora.localeCompare(b.ora));
    } catch(e) { console.error(e); }
  }

  async function handleAnuleazaProgramare(id) {
    if (!confirm("Ești sigur că vrei să anulezi această programare?")) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000/programari/${id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error("Eroare");
      afiseazaToast("Programare anulată cu succes!");
      if (userRole === 'doctor') incarcaDateDoctor();
      if (userRole === 'pacient') incarcaDatePacient();
    } catch (err) { alert("Nu am putut anula."); }
  }

  async function handleAuth() {
    if (!emailInput || !parolaInput) { afiseazaToast("Te rog completează ambele câmpuri!"); return; }
    isLoadingAuth = true;
    try {
      const endpoint = authMode === 'login' ? '/login' : '/register';
      const res = await fetch(`http://127.0.0.1:8000/api/auth${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: emailInput, parola: parolaInput })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Eroare de autentificare");
      
      if (authMode === 'register') {
        afiseazaToast("Cont creat! Acum te poți autentifica.");
        authMode = 'login';
        parolaInput = '';
      } else {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('rol', data.rol);
        localStorage.setItem('pacient_id', data.pacient_id); 
        isAuthenticated = true;
        userRole = data.rol;
        if (userRole === 'doctor') incarcaDateDoctor();
        if (userRole === 'pacient') incarcaDatePacient();
      }
    } catch (err) { alert(err.message); } finally { isLoadingAuth = false; }
  }

  function handleLogout() {
    localStorage.clear();
    isAuthenticated = false;
    window.location.reload(); 
  }

  function onSelectData(e) { dataSelectata = e.detail; slotSelectat = null; }
  function onSelectSlot(e) { slotSelectat = e.detail; dialogOpen = true; }

  async function handleStergePacient(id, nume) {
    if (confirm(`Ești sigur că vrei să ștergi contul pacientului ${nume}?`)) {
      try {
        await deletePacient(id);
        listaTotiPacientii = listaTotiPacientii.filter(p => p.id !== id);
        afiseazaToast(`Pacient șters din sistem.`);
      } catch (err) { alert(err.message); }
    }
  }

  function onProgramareSuccess() {
    dialogOpen = false; slotSelectat = null;
    if (userRole === 'doctor') incarcaDateDoctor();
    if (userRole === 'pacient') incarcaDatePacient();
    afiseazaToast('Programarea a fost salvată cu succes!')
  }

  function afiseazaToast(msg) {
    toast = msg; clearTimeout(toastTimer); toastTimer = setTimeout(() => toast = null, 3500);
  }

  const NAV_ITEMS = [
    { id: 'programari', icon: 'M19 4h-1V3c0-.6-.4-1-1-1s-1 .4-1 1v1H8V3c0-.6-.4-1-1-1s-1 .4-1 1v1H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10z', label: 'Programări' },
    { id: 'pacienti',   icon: 'M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z', label: 'Pacienți' },
    { id: 'asteptare',  icon: 'M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z', label: 'Așteptare' },
    { id: 'info',       icon: 'M11 7h2v2h-2zm0 4h2v6h-2zm1-9C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z', label: 'Informații' },
  ]
</script>

<svelte:head>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</svelte:head>

{#if !isAuthenticated}
  <div class="auth-page">
    <div class="auth-card">
      <div class="brand-header">
        <div class="logo-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="white"><path d="M19 3H5c-1.1 0-1.99.9-1.99 2L3 19c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-1 11h-4v4h-4v-4H6v-4h4V6h4v4h4v4z"/></svg>
        </div>
        <h2>{authMode === 'login' ? 'Conectare Sistem' : 'Cont Nou Pacient'}</h2>
        <p class="auth-subtitle">{authMode === 'login' ? 'Introdu datele pentru a accesa platforma' : 'Creează un cont pentru a te programa'}</p>
      </div>
      <div class="auth-form">
        <div class="input-group">
          <label>Adresă Email</label>
          <input type="email" bind:value={emailInput} placeholder="nume@email.ro" class="modern-input"/>
        </div>
        <div class="input-group">
          <label>Parolă</label>
          <input type="password" bind:value={parolaInput} placeholder="••••••••" class="modern-input"/>
        </div>
        <button class="btn-primary btn-full" on:click={handleAuth} disabled={isLoadingAuth}>
          {isLoadingAuth ? 'Se procesează...' : (authMode === 'login' ? 'Autentificare' : 'Creează Cont')}
        </button>
      </div>
      <div class="auth-footer">
        <button class="btn-text" on:click={() => authMode = authMode === 'login' ? 'register' : 'login'}>
          {authMode === 'login' ? 'Ești pacient nou? Creează un cont' : 'Ai deja cont? Mergi la Autentificare'}
        </button>
      </div>
    </div>
  </div>

{:else}
  {#if userRole === 'doctor'}
    <div class="shell">
      <aside class="sidebar">
        <div class="sidebar-brand">
          <div class="logo-icon-small"><svg width="20" height="20" viewBox="0 0 24 24" fill="white"><path d="M19 3H5c-1.1 0-1.99.9-1.99 2L3 19c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-1 11h-4v4h-4v-4H6v-4h4V6h4v4h4v4z"/></svg></div>
        </div>
        <nav class="nav-menu">
          {#each NAV_ITEMS as item}
            <button class="nav-btn" class:active={tab === item.id} on:click={() => tab = item.id} title={item.label}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d={item.icon}/></svg>
              <span class="tooltip">{item.label}</span>
            </button>
          {/each}
        </nav>
        <button class="nav-btn btn-logout" on:click={handleLogout} title="Deconectare">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
        </button>
      </aside>

      <main class="content-area">
        {#if tab === 'programari'}
          <header class="page-header">
            <div>
              <h1 class="page-title">Bun venit, Dr. Ionescu 👋</h1>
              <p class="page-subtitle">{formatDataLung(azi)} &bull; {programariAzi.length} programări astăzi</p>
            </div>
            <div class="header-actions">
              <button class="btn-outline" on:click={() => arataDialogPacient = true}>+ Pacient Nou</button>
              <button class="btn-primary" on:click={() => { dataSelectata = isoAzi; afiseazaToast('Selectează o oră din calendar 👉') }}>Adaugă Programare</button>
            </div>
          </header>

          <div class="dashboard-grid">
            <div class="agenda-panel">
               <h3 class="panel-heading">Programări Astăzi</h3>
               <div class="card-list">
                 {#each programariAzi as p}
                    <div class="appt-card doctor-card">
                      <div class="appt-time-accent">{p.ora}</div>
                      <div class="appt-details">
                        <strong class="pacient-name">{formateazaNume(listaTotiPacientii.find(pac => pac.id === p.pacienti_id)?.nume) || `Pacient #${p.pacienti_id}`}</strong>
                        <span class="appt-type-badge">{p.type}</span>
                      </div>
                      <button class="btn-icon-danger" on:click={() => handleAnuleazaProgramare(p.id)} title="Anulează programarea">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                      </button>
                    </div>
                 {/each}
                 {#if programariAzi.length === 0}
                    <div class="empty-state">
                      <div class="empty-icon">☕</div>
                      <p>Nicio programare pentru astăzi.</p>
                    </div>
                 {/if}
               </div>

               <h3 class="panel-heading mt-6">Următoarele Programări</h3>
               <div class="card-list">
                 {#each programariViitoare as p}
                    <div class="appt-card doctor-card future">
                      <div class="appt-date-pill">
                        <span class="day">{p.data.substring(8,10)}</span>
                        <span class="month">{LUNI_LUNG[parseInt(p.data.substring(5,7))-1]}</span>
                      </div>
                      <div class="appt-details">
                        <strong class="pacient-name">{formateazaNume(listaTotiPacientii.find(pac => pac.id === p.pacienti_id)?.nume) || `Pacient #${p.pacienti_id}`}</strong>
                        <div class="appt-meta">
                          <span class="appt-time-small">🕒 {p.ora}</span> &bull; <span class="appt-type-text">{p.type}</span>
                        </div>
                      </div>
                      <button class="btn-icon-danger" on:click={() => handleAnuleazaProgramare(p.id)} title="Anulează programarea">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                      </button>
                    </div>
                 {/each}
                 {#if programariViitoare.length === 0}
                   <p class="text-muted text-sm">Nu există programări în zilele următoare.</p>
                 {/if}
               </div>
            </div>
            
            <div class="booking-panel">
              <div class="glass-card"><Calendar on:select={onSelectData} /></div>
              <div class="glass-card mt-4"><Sloturi data={dataSelectata} on:select={onSelectSlot} /></div>
            </div>
          </div>

        {:else if tab === 'pacienti'}
          <header class="page-header">
            <h1 class="page-title">Bază de Date Pacienți</h1>
            <button class="btn-primary" on:click={() => arataDialogPacient = true}>Adaugă Pacient</button>
          </header>
          <div class="glass-card table-wrapper">
            <table class="modern-table">
              <thead><tr><th>ID</th><th>Nume Pacient</th><th>Acțiuni</th></tr></thead>
              <tbody>
                {#each listaTotiPacientii as p}
                  <tr>
                    <td class="text-muted">#{p.id}</td>
                    <td class="font-medium">{formateazaNume(p.nume)}</td>
                    <td><button class="btn-text-danger" on:click={() => handleStergePacient(p.id, p.nume)}>Șterge Fișa</button></td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>

        {:else if tab === 'asteptare'}
          <header class="page-header"><h1 class="page-title">Lista de Așteptare</h1></header>
          <div class="glass-card"><ListaAsteptare /></div>

        {:else if tab === 'info'}
          <header class="page-header"><h1 class="page-title">Panou de Control</h1></header>
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon">👥</div>
              <div class="stat-info">
                <span class="stat-label">Total Pacienți</span>
                <span class="stat-value">{listaTotiPacientii.length}</span>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">📅</div>
              <div class="stat-info">
                <span class="stat-label">Programări Azi</span>
                <span class="stat-value">{programariAzi.length}</span>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">🛡️</div>
              <div class="stat-info">
                <span class="stat-label">Statut Cont</span>
                <span class="stat-value text-accent" style="text-transform: capitalize;">{userRole}</span>
              </div>
            </div>
          </div>
        {/if}
      </main>
    </div>

  {:else}
    <div class="patient-layout">
      <nav class="patient-nav">
        <div class="patient-container nav-content">
          <div class="brand-header nav-brand">
            <div class="logo-icon-small"><svg width="20" height="20" viewBox="0 0 24 24" fill="white"><path d="M19 3H5c-1.1 0-1.99.9-1.99 2L3 19c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-1 11h-4v4h-4v-4H6v-4h4V6h4v4h4v4z"/></svg></div>
            <span class="brand-name">Clinica GI Med</span>
          </div>
          <button class="btn-outline-danger btn-sm" on:click={handleLogout}>Deconectare</button>
        </div>
      </nav>

      <main class="patient-container main-patient-grid">
        <div class="patient-sidebar">
          <div class="welcome-box">
            <h2>Salutare! 👋</h2>
            <p>Acesta este portalul tău medical. Selectează o zi din calendar pentru a programa o vizită la clinică.</p>
          </div>

          {#if slotSelectat}
            <div class="booking-summary-card">
              <div class="summary-header">Rezervare în curs</div>
              <div class="summary-body">
                <div class="summary-row"><span>Data:</span> <strong>{dataSelectata}</strong></div>
                <div class="summary-row"><span>Ora:</span> <strong class="text-accent">{slotSelectat.ora || slotSelectat.start_time}</strong></div>
              </div>
              <button class="btn-primary btn-full mt-4" on:click={() => dialogOpen = true}>Finalizează Programarea</button>
            </div>
          {/if}

          <div class="glass-card">
            <h3 class="panel-heading flex-align"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" class="text-accent mr-2"><path d="M19 4h-1V3c0-.6-.4-1-1-1s-1 .4-1 1v1H8V3c0-.6-.4-1-1-1s-1 .4-1 1v1H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10z"/></svg> Programările Mele</h3>
            <div class="mt-4">
              {#if programariPacient.length === 0}
                <div class="empty-state small">Nu ai nicio programare viitoare.</div>
              {:else}
                <div class="card-list">
                  {#each programariPacient as p}
                    <div class="appt-card patient-card">
                      <div class="appt-date-pill">
                        <span class="day">{p.data.substring(8,10)}</span>
                        <span class="month">{LUNI_LUNG[parseInt(p.data.substring(5,7))-1]}</span>
                      </div>
                      <div class="appt-details">
                        <strong class="appt-time">Ora {p.ora}</strong>
                        <span class="appt-type-text">{p.type}</span>
                      </div>
                      <button class="btn-icon-danger" on:click={() => handleAnuleazaProgramare(p.id)} title="Anulează programarea">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                      </button>
                    </div>
                  {/each}
                </div>
              {/if}
            </div>
          </div>

          <div class="glass-card contact-widget">
            <h3 class="panel-heading mb-4">Contact Clinică</h3>
            <div class="contact-item"><span class="icon">📞</span> <strong>021 999 888</strong></div>
            <div class="contact-item"><span class="icon">📍</span> <span>Str. Sănătății, Nr. 10</span></div>
          </div>
        </div>

        <div class="patient-content">
          <div class="glass-card calendar-wrapper"><Calendar on:select={onSelectData} /></div>
          <div class="glass-card mt-6">
            <h4 class="panel-heading mb-4">{dataSelectata ? `Ore disponibile pentru ${dataSelectata}` : 'Selectează o dată din calendar'}</h4>
            <Sloturi data={dataSelectata} on:select={onSelectSlot} />
          </div>
        </div>
      </main>
    </div>
  {/if}
{/if}

{#if dialogOpen && slotSelectat}
  {#if userRole === 'doctor'}
    <DialogProgramare slot={slotSelectat} data={dataSelectata} on:success={onProgramareSuccess} on:close={() => { dialogOpen = false; slotSelectat = null }} />
  {:else}
    <DialogProgramarePacient slot={slotSelectat} data={dataSelectata} on:success={onProgramareSuccess} on:close={() => { dialogOpen = false; slotSelectat = null }} />
  {/if}
{/if}

<AdaugaPacient bind:esteVizibil={arataDialogPacient} />

{#if toast} 
  <div class="toast-notification animate-slide-up">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
    <span>{toast}</span>
  </div> 
{/if}

<style>
  :global(:root) {
    --primary: #0f172a;       /* Slate 900 - Text principal */
    --primary-light: #334155; /* Slate 700 - Text secundar */
    --accent: #0d9488;        /* Teal 600 - Culoare brand */
    --accent-hover: #0f766e;  /* Teal 700 */
    --accent-light: #f0fdfa;  /* Teal 50 */
    --danger: #ef4444;        /* Red 500 */
    --danger-light: #fef2f2;  /* Red 50 */
    --bg-main: #f8fafc;       /* Slate 50 - Fundal aplicatie */
    --bg-card: #ffffff;       /* Alb pur */
    --border: #e2e8f0;        /* Slate 200 */
    
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 24px;
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  }

  :global(body) {
    margin: 0;
    font-family: 'Inter', sans-serif;
    background-color: var(--bg-main);
    color: var(--primary);
    -webkit-font-smoothing: antialiased;
  }

  /* --- UTILITIES --- */
  h1, h2, h3, h4, p { margin: 0; }
  .text-muted { color: #64748b; }
  .text-sm { font-size: 0.875rem; }
  .text-accent { color: var(--accent); }
  .font-medium { font-weight: 500; }
  .mt-4 { margin-top: 1rem; }
  .mt-6 { margin-top: 1.5rem; }
  .mb-4 { margin-bottom: 1rem; }
  .flex-align { display: flex; align-items: center; }
  .mr-2 { margin-right: 0.5rem; }

  /* --- BUTTONS --- */
  button { font-family: inherit; cursor: pointer; transition: all 0.2s ease; }
  .btn-primary { background: var(--accent); color: white; border: none; padding: 0.625rem 1.25rem; border-radius: var(--radius-sm); font-weight: 600; font-size: 0.875rem; box-shadow: var(--shadow-sm); }
  .btn-primary:hover:not(:disabled) { background: var(--accent-hover); transform: translateY(-1px); box-shadow: var(--shadow-md); }
  .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
  .btn-outline { background: transparent; color: var(--primary-light); border: 1px solid var(--border); padding: 0.625rem 1.25rem; border-radius: var(--radius-sm); font-weight: 600; font-size: 0.875rem; background: var(--bg-card);}
  .btn-outline:hover { background: #f1f5f9; border-color: #cbd5e1; color: var(--primary); }
  .btn-outline-danger { background: transparent; color: var(--danger); border: 1px solid var(--danger); padding: 0.5rem 1rem; border-radius: var(--radius-sm); font-weight: 600; font-size: 0.875rem; }
  .btn-outline-danger:hover { background: var(--danger); color: white; }
  .btn-full { width: 100%; padding: 0.75rem; font-size: 1rem; }
  .btn-text { background: none; border: none; color: var(--accent); font-weight: 500; font-size: 0.875rem; }
  .btn-text:hover { text-decoration: underline; }
  .btn-text-danger { background: none; border: none; color: var(--danger); font-weight: 500; font-size: 0.875rem; padding: 0.25rem 0.5rem; border-radius: 4px;}
  .btn-text-danger:hover { background: var(--danger-light); }
  .btn-icon-danger { display: flex; align-items: center; justify-content: center; background: var(--danger-light); color: var(--danger); border: none; width: 32px; height: 32px; border-radius: 50%; opacity: 0.8; }
  .btn-icon-danger:hover { opacity: 1; transform: scale(1.05); background: #fecaca; }

  /* --- BRANDING --- */
  .logo-icon { width: 48px; height: 48px; background: var(--accent); border-radius: 14px; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto; box-shadow: 0 4px 12px rgba(13, 148, 136, 0.2); }
  .logo-icon-small { width: 36px; height: 36px; background: var(--accent); border-radius: 10px; display: flex; align-items: center; justify-content: center; }

  /* --- AUTH PAGE --- */
  .auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 1rem; }
  .auth-card { background: var(--bg-card); width: 100%; max-width: 400px; padding: 2.5rem 2rem; border-radius: var(--radius-xl); box-shadow: var(--shadow-lg); border: 1px solid var(--border); }
  .brand-header { text-align: center; margin-bottom: 2rem; }
  .brand-header h2 { font-size: 1.5rem; font-weight: 700; color: var(--primary); margin-bottom: 0.5rem; }
  .auth-subtitle { color: var(--text-muted); font-size: 0.875rem; }
  .auth-form { display: flex; flex-direction: column; gap: 1.25rem; }
  .input-group { display: flex; flex-direction: column; gap: 0.375rem; }
  .input-group label { font-size: 0.875rem; font-weight: 500; color: var(--primary-light); }
  .modern-input { padding: 0.75rem 1rem; border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: 1rem; transition: border-color 0.2s, box-shadow 0.2s; outline: none; background: #f8fafc;}
  .modern-input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-light); background: white;}
  .auth-footer { margin-top: 1.5rem; text-align: center; border-top: 1px solid var(--border); padding-top: 1.5rem; }

  /* --- DOCTOR DASHBOARD --- */
  .shell { display: flex; min-height: 100vh; }
  .sidebar { width: 80px; background: var(--primary); display: flex; flex-direction: column; align-items: center; padding: 1.5rem 0; border-right: 1px solid var(--border); position: fixed; height: 100vh; z-index: 10; }
  .sidebar-brand { margin-bottom: 2rem; }
  .nav-menu { display: flex; flex-direction: column; gap: 0.5rem; width: 100%; padding: 0 0.75rem; box-sizing: border-box; }
  .nav-btn { position: relative; display: flex; align-items: center; justify-content: center; width: 100%; aspect-ratio: 1; border: none; background: transparent; color: #94a3b8; border-radius: var(--radius-md); transition: all 0.2s; }
  .nav-btn:hover { color: white; background: rgba(255,255,255,0.05); }
  .nav-btn.active { color: white; background: var(--accent); box-shadow: 0 4px 12px rgba(13, 148, 136, 0.3); }
  .btn-logout { margin-top: auto; color: #f87171; width: calc(100% - 1.5rem); }
  .btn-logout:hover { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
  
  .tooltip { position: absolute; left: calc(100% + 10px); background: var(--primary); color: white; padding: 0.5rem 0.75rem; border-radius: 6px; font-size: 0.75rem; font-weight: 500; opacity: 0; pointer-events: none; transform: translateX(-10px); transition: all 0.2s; white-space: nowrap; z-index: 50; box-shadow: var(--shadow-md); }
  .nav-btn:hover .tooltip { opacity: 1; transform: translateX(0); }

  .content-area { margin-left: 80px; flex: 1; padding: 2.5rem 3rem; max-width: 1400px; margin-right: auto;}
  .page-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 2rem; }
  .page-title { font-size: 1.875rem; font-weight: 700; letter-spacing: -0.025em; }
  .page-subtitle { color: var(--text-muted); margin-top: 0.5rem; font-size: 1rem;}
  .header-actions { display: flex; gap: 1rem; }

  .dashboard-grid { display: grid; grid-template-columns: 380px 1fr; gap: 2rem; align-items: start; }
  .glass-card, .agenda-panel { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 1.5rem; box-shadow: var(--shadow-sm); }
  .panel-heading { font-size: 1.125rem; font-weight: 600; color: var(--primary); margin-bottom: 1.25rem; }
  
  .card-list { display: flex; flex-direction: column; gap: 0.75rem; }
  .appt-card { display: flex; align-items: center; gap: 1rem; padding: 1rem; border-radius: var(--radius-md); border: 1px solid var(--border); background: #f8fafc; transition: border-color 0.2s; }
  .appt-card:hover { border-color: #cbd5e1; background: white; box-shadow: var(--shadow-sm);}
  
  .doctor-card .appt-time-accent { font-size: 1.125rem; font-weight: 700; color: var(--accent); min-width: 55px; }
  .appt-details { flex: 1; display: flex; flex-direction: column; gap: 0.25rem; }
  .pacient-name { font-size: 0.9375rem; color: var(--primary); }
  .appt-type-badge { align-self: flex-start; font-size: 0.6875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; background: var(--accent-light); color: var(--accent-hover); padding: 0.25rem 0.5rem; border-radius: 4px; }
  
  .appt-date-pill { display: flex; flex-direction: column; align-items: center; justify-content: center; background: white; border: 1px solid var(--border); border-radius: 8px; width: 48px; height: 48px; flex-shrink: 0; box-shadow: 0 1px 2px rgba(0,0,0,0.02);}
  .appt-date-pill .day { font-size: 1.125rem; font-weight: 700; color: var(--primary); line-height: 1; }
  .appt-date-pill .month { font-size: 0.65rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; margin-top: 2px; }
  .appt-meta { font-size: 0.8125rem; color: var(--text-muted); }
  .appt-time-small { font-weight: 600; color: var(--primary-light); }

  .empty-state { text-align: center; padding: 2rem 1rem; color: var(--text-muted); }
  .empty-state.small { padding: 1rem; font-size: 0.875rem; background: #f8fafc; border-radius: var(--radius-md); border: 1px dashed var(--border);}
  .empty-icon { font-size: 2rem; margin-bottom: 0.5rem; opacity: 0.5; }

  /* Tabele Info */
  .table-wrapper { overflow-x: auto; }
  .modern-table { width: 100%; border-collapse: separate; border-spacing: 0; }
  .modern-table th { text-align: left; padding: 1rem; border-bottom: 2px solid var(--border); color: var(--text-muted); font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
  .modern-table td { padding: 1rem; border-bottom: 1px solid var(--border); font-size: 0.875rem; }
  .modern-table tr:last-child td { border-bottom: none; }
  .modern-table tbody tr:hover { background: #f8fafc; }

  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; }
  .stat-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 1.5rem; display: flex; align-items: center; gap: 1.25rem; box-shadow: var(--shadow-sm); }
  .stat-icon { font-size: 2rem; width: 56px; height: 56px; display: flex; align-items: center; justify-content: center; background: #f1f5f9; border-radius: 12px; }
  .stat-info { display: flex; flex-direction: column; }
  .stat-label { font-size: 0.875rem; color: var(--text-muted); font-weight: 500; }
  .stat-value { font-size: 1.5rem; font-weight: 700; color: var(--primary); }

  /* --- PATIENT PORTAL --- */
  .patient-layout { display: flex; flex-direction: column; min-height: 100vh; }
  .patient-nav { background: var(--bg-card); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 40; box-shadow: var(--shadow-sm); }
  .patient-container { max-width: 1200px; margin: 0 auto; width: 100%; padding: 0 1.5rem; }
  .nav-content { display: flex; justify-content: space-between; align-items: center; height: 72px; }
  .nav-brand { margin: 0; display: flex; align-items: center; gap: 0.75rem; }
  .brand-name { font-size: 1.25rem; font-weight: 700; color: var(--primary); letter-spacing: -0.02em; }
  
  .main-patient-grid { display: grid; grid-template-columns: 360px 1fr; gap: 2rem; padding-top: 2.5rem; padding-bottom: 2.5rem; align-items: start; }
  
  .patient-sidebar { display: flex; flex-direction: column; gap: 1.5rem; }
  .welcome-box h2 { font-size: 1.75rem; font-weight: 700; margin-bottom: 0.5rem; letter-spacing: -0.02em;}
  .welcome-box p { color: var(--primary-light); line-height: 1.6; font-size: 0.9375rem; }
  
  .booking-summary-card { background: var(--bg-card); border: 2px solid var(--accent); border-radius: var(--radius-lg); padding: 1.5rem; box-shadow: 0 10px 25px -5px rgba(13, 148, 136, 0.15); animation: slideUp 0.3s ease-out; position: relative; overflow: hidden;}
  .booking-summary-card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 4px; background: var(--accent); }
  .summary-header { font-size: 0.875rem; font-weight: 700; color: var(--accent); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem; }
  .summary-body { background: #f8fafc; padding: 1rem; border-radius: var(--radius-sm); border: 1px solid var(--border); }
  .summary-row { display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.9375rem; }
  .summary-row:last-child { margin-bottom: 0; }
  .summary-row span { color: var(--text-muted); }
  
  .patient-card .appt-date-pill { background: var(--accent); color: white; border: none; }
  .patient-card .appt-date-pill .day { color: white; }
  .patient-card .appt-date-pill .month { color: rgba(255,255,255,0.8); }
  .patient-card .appt-time { font-size: 1rem; color: var(--primary); }

  .contact-widget { background: linear-gradient(to bottom right, #ffffff, #f8fafc); }
  .contact-item { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; font-size: 0.9375rem; color: var(--primary-light); }
  .contact-item:last-child { margin-bottom: 0; }
  .contact-item .icon { display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; background: #f1f5f9; border-radius: 10px; font-size: 1.125rem; }

  /* Toast & Animations */
  .toast-notification { position: fixed; bottom: 2rem; right: 2rem; background: var(--primary); color: white; padding: 1rem 1.5rem; border-radius: var(--radius-md); box-shadow: var(--shadow-lg); font-weight: 500; font-size: 0.9375rem; z-index: 9999; display: flex; align-items: center; gap: 0.75rem; }
  .toast-notification svg { color: #34d399; }
  
  @keyframes slideUp { 
    from { opacity: 0; transform: translateY(15px); } 
    to { opacity: 1; transform: translateY(0); } 
  }
  .animate-slide-up { animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
</style>