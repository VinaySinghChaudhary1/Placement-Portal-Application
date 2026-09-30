// frontend/src/services/adminService.js
import api from './api'

export default {
  dashboard() { return api.get('/api/admin/dashboard') },
  listCompanies(params) { return api.get('/api/admin/companies', { params }) },
  getCompany(id) { return api.get(`/api/admin/companies/${id}`) },
  updateCompany(id, payload) { return api.put(`/api/admin/companies/${id}`, payload) },
  companyReports(id) { return api.get(`/api/admin/companies/${id}/reports`) },
  approveCompany(id) { return api.post(`/api/admin/companies/${id}/approve`) },
  rejectCompany(id, reason) { return api.post(`/api/admin/companies/${id}/reject`, { reason }) },
  blacklistCompany(id, blacklisted, reason) { return api.post(`/api/admin/companies/${id}/blacklist`, { blacklisted, reason }) },
  toggleCompanyActive(id, active) { return api.post(`/api/admin/companies/${id}/deactivate`, { active }) },
  listStudents(params) { return api.get('/api/admin/students', { params }) },
  getStudent(id) { return api.get(`/api/admin/students/${id}`) },
  updateStudent(id, payload) { return api.put(`/api/admin/students/${id}`, payload) },
  studentReports(id) { return api.get(`/api/admin/students/${id}/reports`) },
  blacklistStudent(id, blacklisted, reason) { return api.post(`/api/admin/students/${id}/blacklist`, { blacklisted, reason }) },
  toggleStudentActive(id, active) { return api.post(`/api/admin/students/${id}/deactivate`, { active }) },
  listDrives(params) { return api.get('/api/admin/drives', { params }) },
  approveDrive(id) { return api.post(`/api/admin/drives/${id}/approve`) },
  rejectDrive(id, reason) { return api.post(`/api/admin/drives/${id}/reject`, { reason }) },
  listApplications(params) { return api.get('/api/admin/applications', { params }) },
  search(q) { return api.get('/api/admin/search', { params: { q } }) },
  getSettings() { return api.get('/api/admin/settings') },
  updateSettings(payload) { return api.put('/api/admin/settings', payload) },
  monthlyReportPreview(params) { return api.get('/api/admin/reports/monthly', { params }) },
  triggerMonthlyReport() { return api.post('/api/admin/reports/monthly/trigger') },
  triggerReminders() { return api.post('/api/admin/reminders/trigger') },
  reportsOverview() { return api.get('/api/admin/reports/overview') },
  exportCsv() { return api.post('/api/admin/export-csv') },
  exportStatus(taskId) { return api.get(`/api/admin/export-status/${taskId}`) }
}
