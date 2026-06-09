/**
 * Per-browser session id used to scope reading progress.
 *
 * Persisted in localStorage so progress survives reloads, and survives the
 * page being reopened. Cleared only when the user clears their site data.
 */
const SESSION_STORAGE_KEY = 'gdf.session_id'

const generateSessionId = (): string => {
  // Prefer the standard crypto.randomUUID when available.
  const c = (globalThis as unknown as { crypto?: Crypto }).crypto
  if (c && typeof c.randomUUID === 'function') {
    return c.randomUUID()
  }
  // Fallback for older environments.
  const random = Math.random().toString(36).slice(2)
  return `sess-${Date.now().toString(36)}-${random}`
}

export const getSessionId = (): string => {
  try {
    let id = localStorage.getItem(SESSION_STORAGE_KEY)
    if (!id) {
      id = generateSessionId()
      localStorage.setItem(SESSION_STORAGE_KEY, id)
    }
    return id
  } catch {
    // localStorage unavailable (private mode, etc.) — fall back to a
    // process-lifetime id so requests are at least internally consistent.
    return generateSessionId()
  }
}
