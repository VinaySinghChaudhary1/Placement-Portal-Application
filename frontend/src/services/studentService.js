// frontend/src/services/studentService.js
import api from './api'

export default {
  getProfile() { return api.get('/api/student/profile') },
  updateProfile(payload) { return api.put('/api/student/profile', payload) },
  uploadResume(formData) {
    return api.post('/api/student/resume', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  browseDrives(params) { return api.get('/api/student/drives', { params }) },
  getDrive(id) { return api.get(`/api/student/drives/${id}`) },
  apply(id) { return api.post(`/api/student/drives/${id}/apply`) },
  myApplications() { return api.get('/api/student/applications') },
  applicationDetail(id) { return api.get(`/api/student/applications/${id}`) },
  exportCsv() { return api.post('/api/student/export-csv') },
  exportStatus(taskId) { return api.get(`/api/student/export-status/${taskId}`) },
  reports() { return api.get('/api/student/reports') }
}
