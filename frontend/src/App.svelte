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
  
  // Date Doctor
  let programariAzi = []
  let programariViitoare = [] 
  let listaTotiPacientii = []

  // Date Pacient
  let programariPacient = []

  const azi = new Date()
  const isoAzi = azi.toLocaleDateString('sv-SE')
  const ZILE_LUNG = ['Duminica', 'Luni', 'Marti', 'Miercuri', 'Joi', 'Vineri', 'Sambata']
  const LUNI_LUNG = ['Ianuarie','Februarie','Martie','Aprilie','Mai','Iunie','Iulie','August','Septembrie','Octombrie','Noiembrie','Decembrie']

  function formatDataLung(d) {
    return `${ZILE_LUNG[d.getDay()]}, ${d.getDate()} ${LUNI_LUNG[d.getMonth()]} ${d.getFullYear()}`
  }

  // Funcție pentru formatarea numelui (ex: "pop ana" -> "Pop Ana")
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
      
      programariAzi = toate.filter(p => {
        const dataProgramare = p.data || (p.slot && p.slot.data);
        return dataProgramare && String(dataProgramare).startsWith(isoAzi);
      }).sort((a, b) => (a.ora || a.slot?.start_time || '').localeCompare(b.ora || b.slot?.start_time || ''));

      programariViitoare = toate.filter(p => {
        const dataProgramare = p.data || (p.slot && p.slot.data);
        return dataProgramare && String(dataProgramare) > isoAzi;
      }).sort((a, b) => {
        const dataA = a.data || a.slot?.data;
        const dataB = b.data || b.slot?.data;
        if(dataA === dataB) {
          return (a.ora || a.slot?.start_time || '').localeCompare(b.ora || b.slot?.start_time || '');
        }
        return String(dataA).localeCompare(String(dataB));
      });

      getPacienti().then(res => listaTotiPacientii = res).catch(() => {});
    } catch(e) {
      console.error(e);
    }
  }

  async function incarcaDatePacient() {
    try {
      const pid = localStorage.getItem('pacient_id');
      if(!pid) return;

      const toate = await getProgramari();
      programariPacient = toate.filter(p => {
        const dataProgramare = p.data || (p.slot && p.slot.data);
        return p.pacienti_id === parseInt(pid) && dataProgramare && String(dataProgramare) >= isoAzi;
      }).sort((a, b) => {
        const dataA = a.data || a.slot?.data;
        const dataB = b.data || b.slot?.data;
        return String(dataA).localeCompare(String(dataB));
      });
    } catch(e) {
      console.error(e);
    }
  }

  $: if (tab === 'pacienti' && isAuthenticated && userRole === 'doctor') {
    getPacienti().then(res => listaTotiPacientii = res).catch(() => {});
  }

  async function handleAuth() {
    if (!emailInput || !parolaInput) {
      afiseazaToast("Te rog completeaza email-ul si parola!");
      return;
    }
    isLoadingAuth = true;
    try {
      const endpoint = authMode === 'login' ? '/login' : '/register';
      const res = await fetch(`http://127.0.0.1:8000/api/auth${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: emailInput, parola: parolaInput })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Eroare");
      
      if (authMode === 'register') {
        afiseazaToast("Cont creat! Loghează-te.");
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
    } catch (err) {
      alert(err.message);
    } finally {
      isLoadingAuth = false;
    }
  }

  function handleLogout() {
    localStorage.removeItem('token');
    localStorage.removeItem('rol');
    localStorage.removeItem('pacient_id');
    isAuthenticated = false;
    window.location.reload(); 
  }

  function onSelectData(e) { dataSelectata = e.detail; slotSelectat = null; }
  function onSelectSlot(e) { slotSelectat = e.detail; dialogOpen = true; }

  async function handleStergePacient(id, nume) {
    if (confirm(`Stergi pacientul ${nume}?`)) {
      try {
        await deletePacient(id);
        listaTotiPacientii = listaTotiPacientii.filter(p => p.id !== id);
        afiseazaToast(`Pacient sters.`);
      } catch (err) {
        alert(err.message);
      }
    }
  }

  function onProgramareSuccess(e) {
    dialogOpen = false; slotSelectat = null;
    if (userRole === 'doctor') incarcaDateDoctor();
    if (userRole === 'pacient') incarcaDatePacient();
    afiseazaToast('Succes!')
  }

  function afiseazaToast(msg) {
    toast = msg; clearTimeout(toastTimer); toastTimer = setTimeout(() => toast = null, 3000);
  }

  const NAV_ITEMS = [
    { id: 'programari', icon: 'calendar', label: 'Programari' },
    { id: 'pacienti',   icon: 'users',    label: 'Pacienti' },
    { id: 'asteptare',  icon: 'clock',    label: 'Asteptare' },
    { id: 'info',       icon: 'info',     label: 'Info' },
  ]
</script>

{#if !isAuthenticated}
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <div class="logo-circle auth-logo">
           <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z" fill="white" opacity="0.3"/>
            <path d="M11 7h2v10h-2zM7 11h10v2H7z" fill="white"/>
          </svg>
        </div>
        <h2>{authMode === 'login' ? 'Conectare' : 'Cont Nou'}</h2>
      </div>
      <div class="auth-form">
        <div class="input-group">
          <label>Email</label>
          <input type="email" bind:value={emailInput} placeholder="doctor@clinica.ro" class="auth-input"/>
        </div>
        <div class="input-group">
          <label>Parolă</label>
          <input type="password" bind:value={parolaInput} placeholder="••••••••" class="auth-input"/>
        </div>
        <button class="btn-auth" on:click={handleAuth} disabled={isLoadingAuth}>
          {isLoadingAuth ? '...' : (authMode === 'login' ? 'Intră în cont' : 'Creează cont')}
        </button>
      </div>
      <div class="auth-footer">
        <span class="auth-link" on:click={() => authMode = authMode === 'login' ? 'register' : 'login'}>
          {authMode === 'login' ? 'Nu ai cont? Înregistrează-te' : 'Ai deja cont? Conectează-te'}
        </span>
      </div>
    </div>
  </div>

{:else}
  {#if userRole === 'doctor'}
    <div class="shell">
      <aside class="sidebar">
        <div class="sidebar-logo">
          <div class="logo-circle">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M11 7h2v10h-2zM7 11h10v2H7z" fill="white"/></svg>
          </div>
        </div>
        {#each NAV_ITEMS as item}
          <button class="nav-btn" class:active={tab === item.id} on:click={() => tab = item.id} title={item.label}>
            {#if item.icon === 'calendar'}<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="3"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            {:else if item.icon === 'users'}<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
            {:else if item.icon === 'clock'}<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            {:else if item.icon === 'info'}<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>{/if}
          </button>
        {/each}
        <div class="sidebar-spacer" style="flex:1"></div>
        <button class="nav-btn logout-btn" on:click={handleLogout} title="Ieșire">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2.5">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
        </button>
      </aside>

      <div class="content">
        {#if tab === 'programari'}
          <div class="top-bar">
            <div class="greeting">
              <h1>Buna dimineata, Dr. Ionescu 👋</h1>
              <p class="sub-date">{formatDataLung(azi)} &bull; {programariAzi.length} programari azi</p>
            </div>
            <div class="top-actions">
              <button class="btn-secondary" on:click={() => arataDialogPacient = true}>Pacient nou</button>
              <button class="btn-new" on:click={() => { dataSelectata = isoAzi; afiseazaToast('Selecteaza o ora 👉') }}>Programare noua</button>
            </div>
          </div>
          <div class="main-grid">
            <div class="left-panel">
               
               <div class="panel-label">Programari Astazi</div>
               <div class="today-list">
                 {#each programariAzi as p}
                    <div class="today-card">
                      <div class="today-time">{p.ora || p.slot?.start_time || '--:--'}</div>
                      <div class="today-info">
                        <div class="pacient-name">
                          {formateazaNume(listaTotiPacientii.find(pac => pac.id === p.pacienti_id)?.nume) || `Pacient #${p.pacienti_id}`}
                        </div>
                        <div class="pacient-type">{p.type || 'Consultație'}</div>
                      </div>
                    </div>
                 {/each}
                 {#if programariAzi.length === 0}
                    <div class="msg">Nicio programare azi.</div>
                 {/if}
               </div>

               <div class="panel-label mt-divider">Următoarele Programări</div>
               <div class="today-list">
                 {#each programariViitoare as p}
                    <div class="today-card future-card">
                      <div class="future-datetime">
                        <span class="f-date">{(p.data || p.slot?.data).substring(8,10)}/{(p.data || p.slot?.data).substring(5,7)}</span>
                        <span class="today-time">{p.ora || p.slot?.start_time || '--:--'}</span>
                      </div>
                      <div class="today-info">
                        <div class="pacient-name">
                          {formateazaNume(listaTotiPacientii.find(pac => pac.id === p.pacienti_id)?.nume) || `Pacient #${p.pacienti_id}`}
                        </div>
                        <div class="pacient-type">{p.type || 'Consultație'}</div>
                      </div>
                    </div>
                 {/each}
                 {#if programariViitoare.length === 0}
                    <div class="msg">Nu există programări viitoare.</div>
                 {/if}
               </div>

            </div>
            <div class="right-panel">
              <div class="card-wrap"><Calendar on:select={onSelectData} /></div>
              <div class="card-wrap"><Sloturi data={dataSelectata} on:select={onSelectSlot} /></div>
            </div>
          </div>
        {:else if tab === 'pacienti'}
          <div class="top-bar">
            <div class="greeting"><h1>Baza de date Pacienti</h1></div>
            <button class="btn-new" on:click={() => arataDialogPacient = true}>Adauga Pacient</button>
          </div>
          <div class="panel-lista">
            <div class="table-container">
              <table class="tabel-date">
                <thead><tr><th>ID</th><th>Nume</th><th>Actiuni</th></tr></thead>
                <tbody>
                  {#each listaTotiPacientii as p}
                    <tr>
                      <td class="td-id">#{p.id}</td>
                      <td class="font-bold">{formateazaNume(p.nume)}</td>
                      <td><button class="btn-sterge" on:click={() => handleStergePacient(p.id, p.nume)}>Sterge</button></td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          </div>
        {:else if tab === 'asteptare'}
          <div class="top-bar"><h1>Lista de asteptare</h1></div>
          <div class="lista-wrap"><ListaAsteptare /></div>
        {:else if tab === 'info'}
          <div class="top-bar">
            <div class="greeting">
              <h1>Informații și Statistici</h1>
              <p class="sub-date">Panoul general al clinicii</p>
            </div>
          </div>
          <div class="info-grid">
            <div class="info-card">
              <h3>📊 Statistici Rapide</h3>
              <div class="stat-item"><span>Pacienți înregistrați:</span><strong>{listaTotiPacientii.length}</strong></div>
              <div class="stat-item"><span>Programări azi:</span><strong>{programariAzi.length}</strong></div>
            </div>
            <div class="info-card">
              <h3>👩‍⚕️ Profil Medic</h3>
              <div class="stat-item"><span>Email cont:</span><strong>doctor@clinica.ro</strong></div>
              <div class="stat-item"><span>Rol sistem:</span><strong style="text-transform: capitalize; color: var(--accent);">{userRole}</strong></div>
            </div>
            <div class="info-card full-width">
              <h3>🕒 Program de lucru al clinicii</h3>
              <div class="hours-grid">
                <div class="day-row"><span>Luni - Vineri:</span> <strong>08:00 - 18:00</strong></div>
                <div class="day-row"><span>Sâmbătă:</span> <strong>09:00 - 14:00</strong></div>
                <div class="day-row"><span>Duminică:</span> <strong style="color: #ef4444;">Închis</strong></div>
              </div>
            </div>
          </div>
        {/if}
      </div>
    </div>
  {:else}
    <div class="patient-portal">
      <header class="patient-header">
        <div class="patient-brand">
          <div class="logo-circle">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM11 7h2v10h-2V7zm-4 4h10v2H7v-2z"/></svg>
          </div>
          <h3>Portal Pacient</h3>
        </div>
        <button class="btn-logout-patient" on:click={handleLogout}>Deconectare</button>
      </header>
      
      <main class="patient-main">
        <div class="patient-grid">
          <div class="patient-left-col">
            <div class="card-wrap welcome-card">
              <h2>Salutare! 👋</h2>
              <p>Acesta este contul tău medical. Alege o zi din calendar pentru o programare nouă sau verifică-le pe cele existente.</p>
            </div>

            {#if slotSelectat}
              <div class="selection-summary animate-in">
                <h4>Rezervare nouă:</h4>
                <p><strong>Data:</strong> {dataSelectata}</p>
                <p><strong>Ora:</strong> {slotSelectat.ora || slotSelectat.start_time}</p>
                <button class="btn-confirm" on:click={() => dialogOpen = true}>Confirmă Programarea</button>
              </div>
            {/if}

            <div class="card-wrap">
              <h3 class="section-title">📅 Programările Mele</h3>
              {#if programariPacient.length === 0}
                <p class="msg">Nu ai nicio programare viitoare.</p>
              {:else}
                <div class="appt-list">
                  {#each programariPacient as p}
                    <div class="appt-card">
                      <div class="appt-date-box">
                        <span class="a-day">{(p.data || p.slot?.data).substring(8,10)}</span>
                        <span class="a-month">{(p.data || p.slot?.data).substring(5,7)}</span>
                      </div>
                      <div class="appt-info">
                        <strong>Ora {p.ora || p.slot?.start_time || '--:--'}</strong>
                        <span>{p.type || 'Consultație'}</span>
                      </div>
                    </div>
                  {/each}
                </div>
              {/if}
            </div>

            <div class="card-wrap contact-card">
              <h3 class="section-title">🏥 Contact Clinică</h3>
              <div class="contact-row"><span>📞</span> <strong>021 999 888</strong></div>
              <div class="contact-row"><span>📍</span> <span>Str. Sănătății, Nr. 10</span></div>
              <div class="contact-row"><span>🕒</span> <span>L-V: 08:00 - 18:00</span></div>
            </div>
          </div>

          <div class="patient-booking">
            <div class="card-wrap"><Calendar on:select={onSelectData} /></div>
            <div class="card-wrap">
              <h4 class="slot-title">{dataSelectata ? `Ore pentru ${dataSelectata}` : 'Alege o data'}</h4>
              <Sloturi data={dataSelectata} on:select={onSelectSlot} />
            </div>
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
{#if toast} <div class="toast">{toast}</div> {/if}

<style>
  :global(:root) {
    --accent: #0d9488;
    --accent-light: rgba(13, 148, 136, 0.1);
    --bg: #f8fafc;
    --bg-sidebar: #0f172a;
    --bg-card: #ffffff;
    --border: #e2e8f0;
    --text-primary: #0f172a;
    --text-secondary: #334155;
    --text-muted: #64748b;
    --radius: 16px;
    --radius-sm: 10px;
    --sidebar-w: 72px;
  }

  /* --- AUTH & GLOBAL --- */
  .auth-page { display: flex; align-items: center; justify-content: center; min-height: 100vh; background: #f1f5f9; font-family: sans-serif; }
  .auth-card { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); width: 320px; text-align: center; }
  .auth-form { display: flex; flex-direction: column; gap: 16px; margin-top: 20px; text-align: left; }
  .auth-input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 10px; box-sizing: border-box; }
  .btn-auth { background: var(--accent); color: white; border: none; padding: 12px; border-radius: 10px; cursor: pointer; font-weight: bold; }
  .auth-link { color: var(--accent); cursor: pointer; font-size: 14px; margin-top: 15px; display: block; }
  .toast { position: fixed; bottom: 30px; right: 30px; background: #1e293b; color: white; padding: 16px 24px; border-radius: 12px; z-index: 1000; font-weight: 600; }
  .msg { font-size: 13px; color: var(--text-muted); font-style: italic; padding: 10px 0; }

  /* --- DOCTOR --- */
  .shell { display: flex; min-height: 100vh; background: var(--bg); font-family: sans-serif; }
  .sidebar { width: var(--sidebar-w); background: var(--bg-sidebar); display: flex; flex-direction: column; align-items: center; padding: 20px 0; position: fixed; height: 100vh; z-index: 100; }
  .nav-btn { background: none; border: none; color: #94a3b8; padding: 14px; cursor: pointer; border-radius: 12px; margin-bottom: 8px; transition: 0.2s; }
  .nav-btn:hover { background: rgba(255,255,255,0.05); color: white; }
  .nav-btn.active { background: var(--accent); color: white; }
  .logout-btn { margin-top: auto; color: #ef4444; }
  .logout-btn:hover { background: rgba(239, 68, 68, 0.1) !important; }
  .content { margin-left: var(--sidebar-w); padding: 40px; flex: 1; }
  .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; }
  h1 { font-size: 24px; font-weight: 700; color: var(--text-primary); margin: 0; }
  .sub-date { color: var(--text-muted); font-size: 14px; }
  .top-actions { display: flex; gap: 12px; }
  .btn-secondary { padding: 10px 20px; background: white; border: 1px solid var(--border); border-radius: 12px; font-weight: 600; cursor: pointer; }
  .btn-new { padding: 10px 20px; background: var(--accent); color: white; border: none; border-radius: 12px; font-weight: 600; cursor: pointer; }
  .main-grid { display: grid; grid-template-columns: 320px 1fr; gap: 32px; align-items: start; }
  .left-panel { background: white; border: 1px solid var(--border); border-radius: var(--radius); padding: 24px; max-height: calc(100vh - 140px); overflow-y: auto; }
  .today-card { display: flex; align-items: flex-start; gap: 12px; padding: 12px; background: #f8fafc; border-radius: 12px; margin-bottom: 8px; border: 1px solid var(--border); }
  .today-time { font-weight: 700; color: var(--accent); min-width: 45px; }
  .mt-divider { margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--border); }
  .future-card { align-items: center; }
  .future-datetime { display: flex; flex-direction: column; align-items: center; min-width: 55px; background: #e2e8f0; padding: 6px; border-radius: 8px; }
  .f-date { font-size: 11px; color: var(--text-secondary); font-weight: 800; letter-spacing: 0.5px; }
  .pacient-name { font-weight: 700; color: var(--text-primary); font-size: 14px; }
  .pacient-type { font-size: 11px; color: var(--accent); font-weight: 700; margin-top: 4px; background: var(--accent-light); padding: 3px 8px; border-radius: 6px; display: inline-block; }
  .right-panel { display: flex; flex-direction: column; gap: 24px; }
  .card-wrap { background: white; border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; margin-bottom: 16px; }

  /* --- DOCTOR: TABLES & INFO --- */
  .panel-lista, .lista-wrap { background: white; border: 1px solid var(--border); border-radius: var(--radius); padding: 24px; }
  .tabel-date { width: 100%; border-collapse: collapse; }
  .tabel-date th { text-align: left; padding: 16px; background: #f8fafc; border-bottom: 2px solid var(--border); color: var(--text-muted); font-size: 12px; text-transform: uppercase; }
  .tabel-date td { padding: 16px; border-bottom: 1px solid var(--border); }
  .td-id { font-family: monospace; color: var(--accent); font-weight: 700; }
  .font-bold { font-weight: 600; color: var(--text-primary); }
  .btn-sterge { background: #fee2e2; color: #ef4444; border: none; padding: 6px 12px; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 12px; }

  .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; max-width: 900px; }
  .info-card { background: white; border: 1px solid var(--border); border-radius: var(--radius); padding: 28px; box-shadow: 0 4px 12px rgba(0,0,0,0.02); }
  .info-card.full-width { grid-column: 1 / -1; }
  .info-card h3 { margin-top: 0; margin-bottom: 24px; color: var(--text-primary); font-size: 18px; display: flex; align-items: center; gap: 10px; }
  .stat-item { display: flex; justify-content: space-between; padding: 14px 0; border-bottom: 1px solid #f1f5f9; font-size: 15px; }
  .stat-item:last-child { border-bottom: none; padding-bottom: 0; }
  .stat-item span { color: var(--text-muted); font-weight: 500; }
  .stat-item strong { color: var(--text-primary); font-weight: 700; font-size: 16px; }
  .hours-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
  .day-row { display: flex; flex-direction: column; gap: 6px; padding: 16px; background: #f8fafc; border-radius: 12px; text-align: center; border: 1px solid var(--border); }
  .day-row span { color: var(--text-secondary); font-weight: 600; font-size: 14px; }
  .day-row strong { color: var(--text-primary); font-weight: 800; font-size: 16px; }

  /* --- PACIENT PORTAL MODIFICAT --- */
  .patient-header { display: flex; justify-content: space-between; padding: 20px 40px; background: white; border-bottom: 1px solid #eee; align-items: center; }
  .patient-brand { display: flex; align-items: center; gap: 12px; }
  .btn-logout-patient { border: 1.5px solid #ef4444; color: #ef4444; background: none; padding: 8px 16px; border-radius: 10px; cursor: pointer; font-weight: 600; transition: 0.2s; }
  .btn-logout-patient:hover { background: #ef4444; color: white; }
  
  .patient-main { padding: 40px; display: flex; justify-content: center; background: var(--bg); min-height: calc(100vh - 80px); font-family: sans-serif;}
  .patient-grid { display: grid; grid-template-columns: 380px 1fr; gap: 32px; max-width: 1200px; width: 100%; align-items: start; }
  
  .patient-left-col { display: flex; flex-direction: column; gap: 24px; }
  .welcome-card { background: white; border: 1px solid var(--border); }
  .patient-left-col h2 { font-size: 26px; margin-bottom: 12px; color: var(--text-primary); }
  .patient-left-col p { color: var(--text-muted); line-height: 1.5; font-size: 15px; margin: 0; }
  
  .section-title { font-size: 16px; color: var(--text-primary); margin: 0 0 16px 0; display: flex; align-items: center; gap: 8px;}
  
  .appt-list { display: flex; flex-direction: column; gap: 12px; }
  .appt-card { display: flex; align-items: center; gap: 16px; background: #f8fafc; padding: 12px; border-radius: 12px; border: 1px solid var(--border); }
  .appt-date-box { background: var(--accent); color: white; border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; width: 50px; height: 50px; flex-shrink: 0; }
  .a-day { font-size: 18px; font-weight: 800; line-height: 1; }
  .a-month { font-size: 11px; font-weight: 600; text-transform: uppercase; margin-top: 2px;}
  .appt-info { display: flex; flex-direction: column; gap: 4px; }
  .appt-info strong { color: var(--text-primary); font-size: 14px; }
  .appt-info span { color: var(--text-muted); font-size: 13px; }

  .contact-card { background: linear-gradient(145deg, #ffffff, #f8fafc); }
  .contact-row { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; color: var(--text-secondary); font-size: 14px; }
  .contact-row:last-child { margin-bottom: 0; }
  .contact-row strong { color: var(--accent); }

  .selection-summary { background: white; border: 2px solid var(--accent); padding: 24px; border-radius: var(--radius); box-shadow: 0 10px 20px rgba(13, 148, 136, 0.1); }
  .btn-confirm { width: 100%; background: var(--accent); color: white; border: none; padding: 14px; border-radius: 12px; font-weight: 700; margin-top: 15px; cursor: pointer; transition: 0.2s;}
  .btn-confirm:hover { background: #0f766e; }
  
  .animate-in { animation: slideUp 0.3s ease-out; }
  @keyframes slideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
  
  .slot-title { margin: 0 0 20px 0; color: var(--text-primary); font-size: 16px; }
</style>