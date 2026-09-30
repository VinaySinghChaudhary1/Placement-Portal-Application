// frontend/src/services/api.js
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 20000
})

export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common['Authentication-Token'] = token
  } else {
    delete api.defaults.headers.common['Authentication-Token']
  }
}

const saved = localStorage.getItem('token')
if (saved) setAuthToken(saved)

api.interceptors.response.use(
  (res) => res,
  (error) => {
    const resp = error.response
    if (!resp) {
      window.dispatchEvent(new CustomEvent('api:error', { detail: 'Network error. Is the backend running?' }))
      return Promise.reject(error)
    }
    const msg = (resp.data && (resp.data.message || resp.data.error)) || `Error ${resp.status}`
    if (resp.status === 401) {
      window.dispatchEvent(new CustomEvent('auth:unauthorized', { detail: msg }))
    } else if (resp.status === 403) {
      window.dispatchEvent(new CustomEvent('auth:forbidden', { detail: msg }))
    } else {
      window.dispatchEvent(new CustomEvent('api:error', { detail: msg }))
    }
    return Promise.reject(error)
  }
)

export default api
