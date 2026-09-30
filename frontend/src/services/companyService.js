// frontend/src/services/companyService.js
import api from './api'

export default {
  getProfile() { return api.get('/api/company/profile') },
  updateProfile(payload) { return api.put('/api/company/profile', payload) },
  dashboard() { return api.get('/api/company/dashboard') },
  listDrives(params) { return api.get('/api/company/drives', { params }) },
  createDrive(payload) { return api.post('/api/company/drives', payload) },
  getDrive(id) { return api.get(`/api/company/drives/${id}`) },
  updateDrive(id, payload) { return api.put(`/api/company/drives/${id}`, payload) },
  closeDrive(id) { return api.post(`/api/company/drives/${id}/close`) },
  driveApplications(id) { return api.get(`/api/company/drives/${id}/applications`) },
  updateApplicationStatus(id, status) { return api.post(`/api/company/applications/${id}/status`, { status }) },
  scheduleInterview(id, payload) { return api.post(`/api/company/applications/${id}/interview`, payload) },
  updateInterviewResult(id, payload) { return api.post(`/api/company/interviews/${id}/result`, payload) },
  exportCsv() { return api.post('/api/company/export-csv') },
  exportStatus(taskId) { return api.get(`/api/company/export-status/${taskId}`) },
  reports() { return api.get('/api/company/reports') }
}
