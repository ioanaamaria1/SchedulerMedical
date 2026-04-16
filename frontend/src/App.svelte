<script>
  import { onMount } from 'svelte'
  import Calendar from './lib/Calendar.svelte'
  import Sloturi from './lib/Sloturi.svelte'
  import DialogProgramare from './lib/DialogProgramare.svelte'
  import ListaAsteptare from './lib/ListaAsteptare.svelte'
  import AdaugaPacient from './lib/AdaugaPacient.svelte'
  import { getProgramari, getPacienti, deletePacient } from './lib/api.js'

  let tab = 'programari'
  let dataSelectata = null
  let slotSelectat = null
  let dialogOpen = false
  let arataDialogPacient = false
  let toast = null
  let toastTimer = null
  let programariAzi = []
  let listaTotiPacientii = []

  const azi = new Date()
  const isoAzi = azi.toISOString().split('T')[0]

  const ZILE_LUNG = ['Duminica', 'Luni', 'Marti', 'Miercuri', 'Joi', 'Vineri', 'Sambata']
  const LUNI_LUNG = ['Ianuarie','Februarie','Martie','Aprilie','Mai','Iunie','Iulie','August','Septembrie','Octombrie','Noiembrie','Decembrie']

  function formatDataLung(d) {
    return `${ZILE_LUNG[d.getDay()]}, ${d.getDate()} ${LUNI_LUNG[d.getMonth()]} ${d.getFullYear()}`
  }

  onMount(async () => {
    try {
      programariAzi = await getProgramari()
    } catch(e) {}
  })

  $: if (tab === 'pacienti') {
    getPacienti().then(res => listaTotiPacientii = res).catch(() => {});
  }

  function onSelectData(e) {
    dataSelectata = e.detail
    slotSelectat = null
  }

  function onSelectSlot(e) {
    slotSelectat = e.detail
    dialogOpen = true
  }

  async function handleStergePacient(id, nume) {
    if (confirm(`Esti sigur ca vrei sa stergi pacientul ${nume}?`)) {
      try {
        await deletePacient(id);
        listaTotiPacientii = listaTotiPacientii.filter(p => p.id !== id);
        afiseazaToast(`Pacientul ${nume} a fost sters cu succes.`);
      } catch (err) {
        alert("Eroare la stergere: " + err.message);
      }
    }
  }

  function onProgramareSuccess(e) {
    dialogOpen = false
    slotSelectat = null
    dataSelectata = dataSelectata
    getProgramari().then(r => programariAzi = r).catch(() => {})
    afiseazaToast('Programare salvata cu succes')
  }

  function afiseazaToast(msg) {
    toast = msg
    clearTimeout(toastTimer)
    toastTimer = setTimeout(() => toast = null, 3000)
  }

  const NAV_ITEMS = [
    { id: 'programari', icon: 'calendar', label: 'Programari' },
    { id: 'pacienti',   icon: 'users',    label: 'Pacienti' },
    { id: 'asteptare',  icon: 'clock',    label: 'Asteptare' },
    { id: 'info',       icon: 'info',     label: 'Info' },
    { id: 'docs',       icon: 'docs',     label: 'Documente' },
    { id: 'settings',   icon: 'settings', label: 'Setari' },
  ]
</script>

<div class="shell">
  <aside class="sidebar">
    <div class="sidebar-logo">
      <div class="logo-circle">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z" fill="white" opacity="0.3"/>
          <path d="M11 7h2v10h-2zM7 11h10v2H7z" fill="white"/>
        </svg>
      </div>
    </div>

    {#each NAV_ITEMS as item}
      <button
        class="nav-btn"
        class:active={tab === item.id}
        on:click={() => tab = item.id}
        title={item.label}
      >
        {#if item.icon === 'calendar'}
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <rect x="3" y="4" width="18" height="18" rx="3"/><line x1="16" y1="2" x2="16" y2="6"/>
            <line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
        {:else if item.icon === 'users'}
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
        {:else if item.icon === 'clock'}
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
          </svg>
        {:else if item.icon === 'info'}
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
        {:else if item.icon === 'docs'}
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>
          </svg>
        {:else if item.icon === 'settings'}
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
        {/if}
      </button>
    {/each}
  </aside>

  <div class="content">
    {#if tab === 'programari'}
      <div class="top-bar">
        <div class="greeting">
          <h1>Buna dimineata, Dr. Ionescu <span class="wave">👋</span></h1>
          <p class="sub-date">{formatDataLung(azi)} &bull; <span class="count-today">{programariAzi.length} programari azi</span></p>
        </div>
        <div class="top-actions">
          <div class="search-wrap">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="search-icon">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input type="text" placeholder="Cauta pacient..." class="search-input" />
          </div>
          
          <button class="btn-secondary" on:click={() => arataDialogPacient = true}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="17" y1="11" x2="23" y2="11"/>
            </svg>
            Pacient nou
          </button>

          <button class="btn-new" on:click={() => { dataSelectata = isoAzi }}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            Programare noua
          </button>
        </div>
      </div>

      <div class="main-grid">
        <div class="left-panel">
          <div class="panel-label">Programari Astazi</div>
          <div class="today-list">
            {#each programariAzi.slice(0, 6) as p, i}
              {@const culori = ['#0d9488','#ef4444','#f59e0b','#0d9488','#6366f1','#f97316']}
              <div class="today-card">
                <div class="today-time">{p.slot_id ? `${String(8 + i).padStart(2, '0')}:00` : '--:--'}</div>
                <div class="today-badge" style="background:{culori[i % culori.length]}20; border-color:{culori[i % culori.length]}">
                  <span class="badge-dot" style="background:{culori[i % culori.length]}"></span>
                </div>
                <div class="today-info">
                  <div class="today-name">Pacient #{p.pacienti_id}</div>
                  <div class="today-type">{p.type || 'consultatie'}</div>
                  <div class="today-dur">
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <rect x="3" y="4" width="18" height="18" rx="3"/><line x1="3" y1="10" x2="21" y2="10"/>
                    </svg>
                    30 min
                  </div>
                </div>
              </div>
            {/each}
            {#if programariAzi.length === 0}
              <div class="empty-state">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.3">
                  <rect x="3" y="4" width="18" height="18" rx="3"/><line x1="3" y1="10" x2="21" y2="10"/>
                </svg>
                <p>Nicio programare azi</p>
              </div>
            {/if}
          </div>
        </div>

        <div class="right-panel">
          <div class="calendar-wrap">
            <Calendar on:select={onSelectData} />
          </div>
          <div class="sloturi-wrap">
            <Sloturi data={dataSelectata} on:select={onSelectSlot} />
          </div>
        </div>
      </div>

    {:else if tab === 'pacienti'}
      <div class="top-bar">
        <div class="greeting">
          <h1>Baza de date Pacienti</h1>
          <p class="sub-date">Gestioneaza toti pacientii inregistrati in clinica</p>
        </div>
        <button class="btn-new" on:click={() => arataDialogPacient = true}>
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          Adauga Pacient
        </button>
      </div>

      <div class="panel-lista">
        {#if listaTotiPacientii.length === 0}
          <p class="msg">Nu exista niciun pacient inregistrat in sistem.</p>
        {:else}
          <div class="table-container">
            <table class="tabel-date">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nume Complet</th>
                  <th>CNP</th>
                  <th>Telefon</th>
                  <th>Actiuni</th>
                </tr>
              </thead>
              <tbody>
                {#each listaTotiPacientii as p}
                  <tr>
                    <td class="td-id">#{p.id}</td>
                    <td class="font-bold">{p.nume}</td>
                    <td>{p.cnp}</td>
                    <td>{p.telefon || '-'}</td>
                    <td>
                      <button class="btn-sterge" on:click={() => handleStergePacient(p.id, p.nume)}>
                        Sterge
                      </button>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {/if}
      </div>

    {:else if tab === 'asteptare'}
      <div class="top-bar">
        <div class="greeting">
          <h1>Lista de asteptare</h1>
          <p class="sub-date">Pacienti care asteapta un slot disponibil</p>
        </div>
      </div>
      <div class="lista-wrap">
        <ListaAsteptare />
      </div>

    {:else}
      <div class="top-bar">
        <div class="greeting">
          <h1>In constructie</h1>
          <p class="sub-date">Aceasta sectiune va fi disponibila in curand.</p>
        </div>
      </div>
    {/if}
  </div>
</div>

{#if dialogOpen && slotSelectat}
  <DialogProgramare
    slot={slotSelectat}
    data={dataSelectata}
    on:success={onProgramareSuccess}
    on:close={() => { dialogOpen = false; slotSelectat = null }}
  />
{/if}

<AdaugaPacient bind:esteVizibil={arataDialogPacient} />

{#if toast}
  <div class="toast">{toast}</div>
{/if}

<style>
  .shell { display: flex; min-height: 100vh; background: var(--bg); }
  .sidebar {
    width: var(--sidebar-w); background: var(--bg-sidebar); border-right: 1px solid var(--border);
    display: flex; flex-direction: column; align-items: center; padding: 12px 0;
    position: fixed; top: 0; left: 0; height: 100vh; z-index: 20; gap: 4px;
  }
  .sidebar-logo {
    width: 100%; display: flex; justify-content: center; padding: 8px 0 16px;
    border-bottom: 1px solid var(--border); margin-bottom: 8px;
  }
  .logo-circle {
    width: 38px; height: 38px; background: var(--accent); border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
  }
  .nav-btn {
    width: 42px; height: 42px; display: flex; align-items: center; justify-content: center;
    border: none; background: none; border-radius: 10px; cursor: pointer; color: var(--text-muted);
    transition: background 0.12s, color 0.12s;
  }
  .nav-btn:hover { background: var(--bg-hover); color: var(--text-secondary); }
  .nav-btn.active { background: var(--accent-light); color: var(--accent); }

  .content {
    margin-left: var(--sidebar-w); flex: 1; display: flex; flex-direction: column;
    min-height: 100vh; padding: 28px 32px; max-width: calc(100vw - var(--sidebar-w));
  }
  .top-bar { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 24px; gap: 16px; flex-wrap: wrap; }
  h1 { font-size: 22px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
  .wave { font-style: normal; }
  .sub-date { font-size: 13px; color: var(--text-muted); }
  .count-today { color: var(--accent); font-weight: 500; }
  .top-actions { display: flex; align-items: center; gap: 10px; }

  .search-wrap { position: relative; display: flex; align-items: center; }
  .search-icon { position: absolute; left: 10px; color: var(--text-muted); pointer-events: none; }
  .search-input {
    padding: 8px 12px 8px 32px; border: 1px solid var(--border); border-radius: var(--radius-sm);
    font-size: 13px; background: var(--bg-card); color: var(--text-primary); outline: none;
    width: 220px; transition: border-color 0.15s;
  }
  .search-input:focus { border-color: var(--accent); }

  .btn-secondary {
    display: flex; align-items: center; gap: 6px; padding: 8px 16px; background: var(--bg-card);
    color: var(--text-primary); border: 1px solid var(--border); border-radius: var(--radius-sm);
    font-size: 13px; font-weight: 500; cursor: pointer; white-space: nowrap; transition: all 0.15s;
  }
  .btn-secondary:hover { background: var(--bg-hover); border-color: var(--text-muted); }

  .btn-new {
    display: flex; align-items: center; gap: 6px; padding: 8px 16px; background: var(--accent);
    color: white; border: none; border-radius: var(--radius-sm); font-size: 13px; font-weight: 500;
    cursor: pointer; white-space: nowrap; transition: background 0.15s;
  }
  .btn-new:hover { background: var(--accent-hover); }

  .main-grid { display: grid; grid-template-columns: 280px 1fr; gap: 20px; align-items: start; }
  .left-panel { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
  .panel-label { font-size: 13px; font-weight: 600; color: var(--text-primary); padding: 14px 16px 10px; display: flex; justify-content: space-between; }
  
  .today-card { display: flex; align-items: flex-start; gap: 10px; padding: 12px 16px; border-top: 1px solid var(--border); cursor: pointer; transition: background 0.1s; }
  .today-card:hover { background: var(--bg-hover); }
  .today-time { font-size: 15px; font-weight: 700; color: var(--text-primary); min-width: 44px; line-height: 1.2; padding-top: 2px; }
  .today-badge { width: 36px; height: 36px; border-radius: 50%; border: 2px solid; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
  .badge-dot { width: 8px; height: 8px; border-radius: 50%; }
  .today-info { flex: 1; min-width: 0; }
  .today-name { font-size: 13px; font-weight: 500; color: var(--text-primary); margin-bottom: 1px; }
  .today-type { font-size: 12px; color: var(--text-muted); margin-bottom: 4px; text-transform: capitalize; }
  .today-dur { display: flex; align-items: center; gap: 4px; font-size: 11px; color: var(--text-muted); }

  .empty-state { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 32px 16px; color: var(--text-muted); font-size: 13px; }
  .right-panel { display: flex; flex-direction: column; gap: 16px; }
  .calendar-wrap, .sloturi-wrap { width: 100%; }
  .lista-wrap { max-width: 680px; }

  .panel-lista {
    background: var(--bg-card, white); border: 1px solid var(--border, #e2e8f0);
    border-radius: var(--radius, 12px); overflow: hidden;
  }
  .table-container { width: 100%; overflow-x: auto; }
  .tabel-date { width: 100%; border-collapse: collapse; text-align: left; font-size: 14px; }
  .tabel-date th { 
    padding: 14px 20px; border-bottom: 2px solid var(--border, #e2e8f0); 
    color: var(--text-muted, #64748b); font-weight: 600; background: #f8fafc;
  }
  .tabel-date td { padding: 14px 20px; border-bottom: 1px solid var(--border, #e2e8f0); color: #334155; }
  .td-id { color: #94a3b8 !important; font-weight: 500; }
  .font-bold { font-weight: 600; color: #0f172a !important; }
  .btn-sterge { 
    background: #fee2e2; color: #ef4444; border: none; padding: 6px 12px; 
    border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 600; transition: 0.2s;
  }
  .btn-sterge:hover { background: #fecaca; }
  .msg { padding: 20px; color: #64748b; text-align: center; }

  .toast {
    position: fixed; bottom: 24px; right: 24px; background: #0f172a; color: white;
    padding: 12px 20px; border-radius: 10px; font-size: 13px; font-weight: 500;
    z-index: 300; animation: slide-up 0.2s ease; box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  }

  @keyframes slide-up { from { transform: translateY(12px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
  @media (max-width: 900px) { .main-grid { grid-template-columns: 1fr; } .content { padding: 20px 16px; } }
</style>