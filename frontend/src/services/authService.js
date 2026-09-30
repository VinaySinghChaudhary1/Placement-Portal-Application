// frontend/src/services/authService.js
import api from './api'

export default {
  login(payload) {
    return api.post('/login', payload)
  },
  logout() {
    return api.post('/logout')
  },
  registerStudent(payload) {
    return api.post('/register/student', payload)
  },
  registerCompany(payload) {
    return api.post('/register/company', payload)
  },
  getCurrentUser() {
    return api.get('/user')
  }
}
