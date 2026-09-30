<template>
  <div class="auth-shell py-4">
    <div class="card auth-card shadow-sm">
      <div class="card-body p-4 p-md-5">
        <div class="text-center mb-4">
          <i class="bi bi-person-badge text-primary display-5"></i>
          <h4 class="mt-2 mb-0">Student registration</h4>
          <p class="text-muted small">Create your account to browse and apply for drives</p>
        </div>
        <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
        <div v-if="success" class="alert alert-success py-2">{{ success }}</div>
        <form v-if="!success" @submit.prevent="submit" novalidate>
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label">Full name</label>
              <input v-model.trim="form.full_name" class="form-control" required>
            </div>
            <div class="col-md-6">
              <label class="form-label">Username</label>
              <input v-model.trim="form.username" class="form-control" required>
            </div>
            <div class="col-md-6">
              <label class="form-label">Email</label>
              <input v-model.trim="form.email" type="email" class="form-control" required>
            </div>
            <div class="col-md-6">
              <label class="form-label">Phone</label>
              <input v-model.trim="form.phone" class="form-control">
            </div>
            <div class="col-md-4">
              <label class="form-label">Branch</label>
              <input v-model.trim="form.branch" class="form-control" required placeholder="Computer Science">
            </div>
            <div class="col-md-4">
              <label class="form-label">Graduation year</label>
              <input v-model.number="form.year" type="number" class="form-control" required min="2000" max="2100">
            </div>
            <div class="col-md-4">
              <label class="form-label">CGPA</label>
              <input v-model.number="form.cgpa" type="number" step="0.01" min="0" max="10" class="form-control" required>
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
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>Create account
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
  name: 'RegisterStudent',
  data() {
    return {
      form: { username: '', email: '', password: '', confirm_password: '', full_name: '', branch: '', year: new Date().getFullYear(), cgpa: null, phone: '' },
      loading: false, error: '', success: ''
    }
  },
  methods: {
    async submit() {
      this.loading = true
      this.error = ''
      try {
        const res = await this.$store.dispatch('auth/registerStudent', this.form)
        this.success = res.message + ' Redirecting to login…'
        setTimeout(() => this.$router.push('/login'), 1500)
      } catch (e) {
        this.error = e.response?.data?.message || 'Registration failed.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
