<template>
  <div class="container py-4" style="max-width:640px;">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3 class="mb-0">Student profile</h3>
      <router-link :to="`/admin/students/${id}/reports`" class="btn btn-outline-primary btn-sm">
        <i class="bi bi-bar-chart-line me-1"></i>View report
      </router-link>
    </div>

    <div v-if="loading" class="text-center py-5"><span class="spinner-border text-primary"></span></div>
    <template v-else-if="form">
      <div class="mb-3">
        <span v-if="student.blacklisted" class="badge bg-danger me-1">Blocked</span>
        <span v-if="!student.active" class="badge bg-secondary">Deactivated</span>
      </div>
      <div v-if="toast" class="alert" :class="toastClass">{{ toast }}</div>

      <form class="card p-4" @submit.prevent="save">
        <h6 class="text-muted small text-uppercase mb-2">Account</h6>
        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <label class="form-label">Username</label>
            <input v-model="form.username" class="form-control">
          </div>
          <div class="col-md-6">
            <label class="form-label">Email</label>
            <input v-model="form.email" type="email" class="form-control">
          </div>
        </div>
        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <label class="form-label">New password</label>
            <input v-model="form.password" type="password" class="form-control" placeholder="Leave blank to keep unchanged">
          </div>
        </div>

        <h6 class="text-muted small text-uppercase mb-2 mt-2">Profile details</h6>
        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <label class="form-label">Full name</label>
            <input v-model="form.full_name" class="form-control">
          </div>
          <div class="col-md-6">
            <label class="form-label">Phone</label>
            <input v-model="form.phone" class="form-control">
          </div>
        </div>
        <div class="row g-3 mb-4">
          <div class="col-md-4">
            <label class="form-label">Branch</label>
            <input v-model="form.branch" class="form-control">
          </div>
          <div class="col-md-4">
            <label class="form-label">Graduation year</label>
            <input v-model="form.year" type="number" class="form-control">
          </div>
          <div class="col-md-4">
            <label class="form-label">CGPA</label>
            <input v-model="form.cgpa" type="number" step="0.01" min="0" max="10" class="form-control">
          </div>
        </div>

        <button class="btn btn-primary" type="submit" :disabled="saving">
          <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>Save changes
        </button>
      </form>
    </template>
  </div>
</template>

<script>
import adminService from '@/services/adminService'

export default {
  name: 'AdminStudentDetail',
  props: { id: { type: [String, Number], required: true } },
  data() {
    return { student: null, form: null, loading: false, saving: false, toast: '', toastClass: 'alert-success' }
  },
  created() { this.load() },
  methods: {
    async load() {
      this.loading = true
      try {
        const { data } = await adminService.getStudent(this.id)
        this.student = data.student
        this.form = {
          username: data.student.username, email: data.student.email, password: '',
          full_name: data.student.full_name, phone: data.student.phone,
          branch: data.student.branch, year: data.student.year, cgpa: data.student.cgpa
        }
      } finally { this.loading = false }
    },
    async save() {
      this.saving = true
      this.toast = ''
      try {
        const payload = { ...this.form }
        if (!payload.password) delete payload.password
        const { data } = await adminService.updateStudent(this.id, payload)
        this.student = data.student
        this.form.password = ''
        this.toastClass = 'alert-success'
        this.toast = 'Profile updated.'
      } catch (e) {
        this.toastClass = 'alert-danger'
        this.toast = e?.response?.data?.message || 'Update failed.'
      } finally {
        this.saving = false
      }
    }
  }
}
</script>
