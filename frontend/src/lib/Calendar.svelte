<script>
  import { createEventDispatcher } from 'svelte'

  export let selectedDate = null
  const dispatch = createEventDispatcher()

  const ZILE = ['Lu', 'Ma', 'Mi', 'Jo', 'Vi', 'Sa', 'Du']
  const LUNI = ['Ianuarie','Februarie','Martie','Aprilie','Mai','Iunie','Iulie','August','Septembrie','Octombrie','Noiembrie','Decembrie']

  let azi = new Date()
  let luna = azi.getMonth()
  let an = azi.getFullYear()

  function zileLuna(l, a) {
    const prima = new Date(a, l, 1)
    const ultima = new Date(a, l + 1, 0)
    let offset = prima.getDay() - 1
    if (offset < 0) offset = 6
    const zile = []
    for (let i = 0; i < offset; i++) zile.push(null)
    for (let d = 1; d <= ultima.getDate(); d++) zile.push(d)
    return zile
  }

  function lunaAnt() {
    if (luna === 0) { luna = 11; an -= 1 } else luna -= 1
  }

  function lunaUrm() {
    if (luna === 11) { luna = 0; an += 1 } else luna += 1
  }

  function selectZi(zi) {
    if (!zi) return
    const d = new Date(an, luna, zi)
    const aziStart = new Date(azi.getFullYear(), azi.getMonth(), azi.getDate())
    if (d < aziStart) return
    const iso = `${an}-${String(luna + 1).padStart(2,'0')}-${String(zi).padStart(2,'0')}`
    selectedDate = iso
    dispatch('select', iso)
  }

  function esteAzi(zi) {
    return zi === azi.getDate() && luna === azi.getMonth() && an === azi.getFullYear()
  }

  function esteTrecut(zi) {
    if (!zi) return false
    return new Date(an, luna, zi) < new Date(azi.getFullYear(), azi.getMonth(), azi.getDate())
  }

  function esteSelectat(zi) {
    if (!zi || !selectedDate) return false
    return `${an}-${String(luna+1).padStart(2,'0')}-${String(zi).padStart(2,'0')}` === selectedDate
  }

  $: zile = zileLuna(luna, an)
</script>

<div class="cal">
  <div class="cal-header">
    <button class="nav" on:click={lunaAnt}>
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <polyline points="15 18 9 12 15 6"/>
      </svg>
    </button>
    <span class="luna-titlu">{LUNI[luna]} {an}</span>
    <button class="nav" on:click={lunaUrm}>
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <polyline points="9 18 15 12 9 6"/>
      </svg>
    </button>
  </div>

  <div class="zile-header">
    {#each ZILE as z}<span>{z}</span>{/each}
  </div>

  <div class="zile-grid">
    {#each zile as zi}
      <button
        class="zi"
        class:azi={esteAzi(zi)}
        class:sel={esteSelectat(zi)}
        class:trecut={esteTrecut(zi)}
        disabled={!zi || esteTrecut(zi)}
        on:click={() => selectZi(zi)}
      >
        {zi || ''}
      </button>
    {/each}
  </div>
</div>

<style>
  .cal {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px;
    user-select: none;
  }

  .cal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
  }

  .luna-titlu {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .nav {
    width: 28px;
    height: 28px;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
    transition: background 0.12s;
    padding: 0;
  }

  .nav:hover { background: var(--bg-hover); }

  .zile-header {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    margin-bottom: 6px;
  }

  .zile-header span {
    text-align: center;
    font-size: 11px;
    font-weight: 500;
    color: var(--text-muted);
    padding: 3px 0;
  }

  .zile-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 2px;
  }

  .zi {
    aspect-ratio: 1;
    border: none;
    background: none;
    border-radius: 6px;
    font-size: 13px;
    cursor: pointer;
    color: var(--text-primary);
    transition: background 0.1s;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .zi:hover:not(:disabled):not(.sel) { background: var(--bg-hover); }

  .zi.azi {
    font-weight: 700;
    color: var(--accent);
    border: 1.5px solid var(--accent);
  }

  .zi.sel {
    background: var(--accent);
    color: white;
    font-weight: 600;
  }

  .zi.trecut { color: var(--text-muted); opacity: 0.35; cursor: default; }
  .zi:disabled:not(.trecut) { pointer-events: none; }
</style>