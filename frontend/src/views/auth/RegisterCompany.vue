<template>
  <div class="auth-shell py-4">
    <div class="card auth-card shadow-sm">
      <div class="card-body p-4 p-md-5">
        <div class="text-center mb-4">
          <i class="bi bi-building text-primary display-5"></i>
          <h4 class="mt-2 mb-0">Company registration</h4>
          <p class="text-muted small">Register your company — an admin will review before you can post drives</p>
        </div>
        <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
        <div v-if="success" class="alert alert-success py-2">{{ success }}</div>
        <form v-if="!success" @submit.prevent="submit" novalidate>
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label">Company name</label>
              <input v-model.trim="form.company_name" class="form-control" required>
            </div>
            <div class="col-md-6">
              <label class="form-label">Username</label>
              <input v-model.trim="form.username" class="form-control" required>
            </div>
            <div class="col-md-6">
              <label class="form-label">Login email</label>
              <input v-model.trim="form.email" type="email" class="form-control" required>
            </div>
            <div class="col-md-6">
              <label class="form-label">HR contact name</label>
              <input v-model.trim="form.hr_contact_name" class="form-control">
            </div>
            <div class="col-md-6">
              <label class="form-label">HR phone</label>
              <input v-model.trim="form.hr_phone" class="form-control">
            </div>
            <div class="col-md-6">
              <label class="form-label">Website</label>
              <input v-model.trim="form.website" class="form-control" placeholder="https://">
            </div>
            <div class="col-md-6">
              <label class="form-label">Industry</label>
              <input v-model.trim="form.industry" class="form-control">
            </div>
            <div class="col-12">
              <label class="form-label">About the company</label>
              <textarea v-model.trim="form.description" class="form-control" rows="3"></textarea>
            </div>
            <div class="col-md-6">
              <label class="form-label">Password</label>
              <input v-model="form.password" type="password" class="form-control" required minlength="6">
            </div>
            <div class="col-md-6">
              <label class="form-label">Confirm password</label>
              <input v-model="form.confirm_password" type="password" class="form-control" required minlength="6">
            </div>
          </div>
          <button type="submit" class="btn btn-primary w-100 mt-4" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>Submit for approval
          </button>
        </form>
        <p class="text-center small text-muted mt-3 mb-0">
          Already registered? <router-link to="/login">Login</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RegisterCompany',
  data() {
    return {
      form: { username: '', email: '', password: '', confirm_password: '', company_name: '', hr_contact_name: '', hr_phone: '', website: '', industry: '', description: '' },
      loading: false, error: '', success: ''
    }
  },
  methods: {
    async submit() {
      this.loading = true
      this.error = ''
      try {
        const res = await this.$store.dispatch('auth/registerCompany', this.form)
        this.success = res.message + ' Redirecting to login…'
        setTimeout(() => this.$router.push('/login'), 1800)
      } catch (e) {
        this.error = e.response?.data?.message || 'Registration failed.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
