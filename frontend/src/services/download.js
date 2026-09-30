// frontend/src/services/download.js
import api from './api'

/*
 * Downloads a backend-protected file (CSV/PDF exports) and saves it through
 * the browser.
 *
 * Why this exists: the export endpoints require the `Authentication-Token`
 * header (see api.js — auth here is token-based, not cookie/session-based).
 * A plain <a href="/api/exports/..."> or `window.location = link` navigation
 * is a fresh browser request that does NOT carry that header, so it always
 * came back 401 and nothing downloaded — that was the actual bug reported.
 *
 * Fetching the file through the existing `api` axios instance attaches the
 * auth header automatically; we then turn the response into a Blob and
 * trigger a save via a throwaway <a download> element.
 */
export async function downloadFromLink(link, suggestedFilename) {
  const res = await api.get(link, { responseType: 'blob' })

  const disposition = res.headers?.['content-disposition'] || ''
  const match = /filename="?([^"]+)"?/i.exec(disposition)
  const filename = match?.[1] || suggestedFilename || link.split('/').pop() || 'download'

  const blob = new Blob([res.data], { type: res.headers?.['content-type'] || 'application/octet-stream' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  window.URL.revokeObjectURL(url)
}
