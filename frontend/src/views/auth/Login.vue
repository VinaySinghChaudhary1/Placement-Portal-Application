<template>
  <div class="pp-auth-shell">
    <div class="pp-auth-panel p-5 flex-column justify-content-center">
      <span class="pp-blob" style="width:220px;height:220px;background:#7c3aed;top:-40px;left:-40px;"></span>
      <span class="pp-blob" style="width:180px;height:180px;background:#22d3ee;bottom:-30px;right:-30px;animation-delay:-3s;"></span>
      <div class="position-relative">
        <div class="pp-brand-icon-lg mb-4"><i class="bi bi-mortarboard-fill"></i></div>
        <h2 class="fw-bold text-white mb-3">Welcome back to<br>Placement Portal</h2>
        <p class="text-white-50" style="max-width: 380px;">
          Sign in to track applications, manage drives, or oversee the whole placement pipeline —
          whichever seat you're in.
        </p>
        <ul class="list-unstyled text-white-50 small mt-4 d-flex flex-column gap-2">
          <li><i class="bi bi-check-circle me-2"></i>Real-time application &amp; drive status</li>
          <li><i class="bi bi-check-circle me-2"></i>Role-based dashboards for every user</li>
          <li><i class="bi bi-check-circle me-2"></i>Secure, token-based authentication</li>
        </ul>
      </div>
    </div>

    <div class="pp-auth-form-side">
      <div class="pp-auth-card p-4 p-md-5" v-reveal>
        <div class="text-center mb-4 d-lg-none">
          <div class="pp-brand-icon-lg mx-auto mb-2"><i class="bi bi-mortarboard-fill"></i></div>
        </div>
        <h4 class="fw-bold mb-1">Sign in</h4>
        <p class="text-muted small mb-4">Enter your credentials to access your account</p>

        <div v-if="error" :key="error" class="alert alert-danger py-2 pp-shake">{{ error }}</div>

        <form @submit.prevent="submit" novalidate class="pp-field">
          <div class="mb-3">
            <label class="form-label">Email address</label>
            <input v-model.trim="form.email" type="email" class="form-control" required placeholder="you@example.com" autocomplete="username">
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input v-model="form.password" type="password" class="form-control" required minlength="6" autocomplete="current-password">
          </div>
          <button type="submit" class="btn pp-btn-gradient w-100" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            <span v-else><i class="bi bi-box-arrow-in-right me-2"></i></span>Login
          </button>
        </form>

        <hr>
        <p class="text-center small text-muted mb-2">New here?</p>
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

<style scoped>
.pp-brand-icon-lg {
  width: 56px;
  height: 56px;
  border-radius: 1rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  color: #fff;
  background: var(--pp-gradient-brand);
  box-shadow: 0 10px 22px -8px rgba(99, 102, 241, 0.55);
}
</style>
