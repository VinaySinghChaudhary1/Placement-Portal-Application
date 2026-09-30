<template>
  <div class="auth-shell">
    <div class="card auth-card shadow-sm">
      <div class="card-body p-4 p-md-5">
        <div class="text-center mb-4">
          <i class="bi bi-mortarboard-fill text-primary display-5"></i>
          <h4 class="mt-2 mb-0">Welcome back</h4>
          <p class="text-muted small">Sign in to your Placement Portal account</p>
        </div>
        <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
        <form @submit.prevent="submit" novalidate>
          <div class="mb-3">
            <label class="form-label">Email address</label>
            <input v-model.trim="form.email" type="email" class="form-control" required placeholder="you@example.com">
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input v-model="form.password" type="password" class="form-control" required minlength="6">
          </div>
          <button type="submit" class="btn btn-primary w-100" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>Login
          </button>
        </form>
        <hr>
        <p class="text-center small text-muted mb-1">New here?</p>
        <div class="d-flex gap-2">
          <router-link to="/register/student" class="btn btn-outline-primary btn-sm flex-fill">Register as student</router-link>
          <router-link to="/register/company" class="btn btn-outline-secondary btn-sm flex-fill">Register as company</router-link>
        </div>
        <p class="text-center small text-muted mt-3 mb-0">
          Demo admin: <code>admin@placement.edu</code> / <code>Admin@123</code>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return { form: { email: '', password: '' }, loading: false, error: '' }
  },
  methods: {
    async submit() {
      this.loading = true
      this.error = ''
      try {
        const user = await this.$store.dispatch('auth/login', this.form)
        const redirect = this.$route.query.redirect
        const home = user.role === 'admin' ? '/admin' : user.role === 'company' ? '/company' : '/student'
        this.$router.push(redirect || home)
      } catch (e) {
        this.error = e.response?.data?.message || 'Login failed. Please check your credentials.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
