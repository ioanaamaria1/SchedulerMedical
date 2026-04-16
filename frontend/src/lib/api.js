const BASE = 'http://localhost:8000'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Eroare necunoscuta' }))
    throw new Error(err.detail || 'Eroare server')
  }
  return res.json()
}

// Pacienti
export const getPacienti = () => request('/pacienti/')
export const getPacientByCnp = (cnp) => request(`/pacienti/${cnp}`)
export const createPacient = (data) => request('/pacienti/', { method: 'POST', body: JSON.stringify(data) })
export const deletePacient = (id) => request(`/pacienti/${id}`, { method: 'DELETE' })

// Sloturi
export const getSloturiZi = (data) => request(`/sloturi/${data}`)
export const getSloturiLibere = (data) => request(`/sloturi/libere/${data}`)

// Programari
export const getProgramari = () => request('/programari/')
export const createProgramare = (data) => request('/programari/', { method: 'POST', body: JSON.stringify(data) })
export const deleteProgramare = (id) => request(`/programari/${id}`, { method: 'DELETE' })

// Lista asteptare
export const getListaAsteptare = () => request('/lista-asteptare/')
export const addToListaAsteptare = (data) => request('/lista-asteptare/', { method: 'POST', body: JSON.stringify(data) })
export const deleteFromListaAsteptare = (id) => request(`/lista-asteptare/${id}`, { method: 'DELETE' })
