// frontend/src/services/commonService.js
import api from './api'

export default {
  listCompanies() { return api.get('/api/companies') },
  getCompany(id) { return api.get(`/api/companies/${id}`) },
  search(q) { return api.get('/api/search', { params: { q } }) },
  notifications() { return api.get('/api/notifications') },
  markNotificationRead(id) { return api.post(`/api/notifications/${id}/read`) },
  markAllNotificationsRead() { return api.post('/api/notifications/read-all') },
  downloadUrl(relativePath) {
    const base = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000'
    return `${base}/static/${relativePath}`
  }
}
