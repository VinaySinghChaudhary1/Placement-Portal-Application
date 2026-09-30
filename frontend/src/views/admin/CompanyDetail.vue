<template>
  <div class="container py-4" style="max-width:700px;">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3 class="mb-0">Company profile</h3>
      <router-link :to="`/admin/companies/${id}/reports`" class="btn btn-outline-primary btn-sm">
        <i class="bi bi-bar-chart-line me-1"></i>View report
      </router-link>
    </div>

    <div v-if="loading" class="text-center py-5"><span class="spinner-border text-primary"></span></div>
    <template v-else-if="form">
      <div class="mb-3">
        <span class="badge text-capitalize me-1" :class="company.approval_status==='approved' ? 'bg-success' : company.approval_status==='pending' ? 'bg-warning text-dark' : 'bg-danger'">{{ company.approval_status }}</span>
        <span v-if="company.blacklisted" class="badge bg-danger me-1">Blocked</span>
        <span v-if="!company.active" class="badge bg-secondary">Deactivated</span>
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
            <label class="form-label">Login email</label>
            <input v-model="form.email" type="email" class="form-control">
          </div>
        </div>
        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <label class="form-label">New password</label>
            <input v-model="form.password" type="password" class="form-control" placeholder="Leave blank to keep unchanged">
          </div>
        </div>

        <h6 class="text-muted small text-uppercase mb-2 mt-2">Company details</h6>
        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <label class="form-label">Company name</label>
            <input v-model="form.company_name" class="form-control">
          </div>
          <div class="col-md-6">
            <label class="form-label">Industry</label>
            <input v-model="form.industry" class="form-control">
          </div>
          <div class="col-md-6">
            <label class="form-label">HR contact name</label>
            <input v-model="form.hr_contact_name" class="form-control">
          </div>
          <div class="col-md-6">
            <label class="form-label">HR phone</label>
            <input v-model="form.hr_phone" class="form-control">
          </div>
          <div class="col-md-6">
            <label class="form-label">HR email</label>
            <input v-model="form.hr_email" type="email" class="form-control">
          </div>
          <div class="col-md-6">
            <label class="form-label">Website</label>
            <input v-model="form.website" class="form-control">
          </div>
          <div class="col-12">
            <label class="form-label">About</label>
            <textarea v-model="form.description" class="form-control" rows="3"></textarea>
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
  name: 'AdminCompanyDetail',
  props: { id: { type: [String, Number], required: true } },
  data() {
    return { company: null, form: null, loading: false, saving: false, toast: '', toastClass: 'alert-success' }
  },
  created() { this.load() },
  methods: {
    async load() {
      this.loading = true
      try {
        const { data } = await adminService.getCompany(this.id)
        this.company = data.company
        this.form = {
          username: data.company.username, email: data.company.email, password: '',
          company_name: data.company.company_name, industry: data.company.industry,
          hr_contact_name: data.company.hr_contact_name, hr_phone: data.company.hr_phone,
          hr_email: data.company.hr_email, website: data.company.website, description: data.company.description
        }
      } finally { this.loading = false }
    },
    async save() {
      this.saving = true
      this.toast = ''
      try {
        const payload = { ...this.form }
        if (!payload.password) delete payload.password
        const { data } = await adminService.updateCompany(this.id, payload)
        this.company = data.company
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
