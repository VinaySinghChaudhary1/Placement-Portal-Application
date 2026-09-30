<template>
  <div class="pp-auth-shell">
    <div class="pp-auth-panel p-5 flex-column justify-content-center">
      <span class="pp-blob" style="width:220px;height:220px;background:#22d3ee;top:-40px;right:-40px;"></span>
      <span class="pp-blob" style="width:180px;height:180px;background:#0d6efd;bottom:-30px;left:-30px;animation-delay:-3s;"></span>
      <div class="position-relative">
        <div class="pp-brand-icon-lg mb-4"><i class="bi bi-person-badge"></i></div>
        <h2 class="fw-bold text-white mb-3">Your next opportunity<br>starts here</h2>
        <p class="text-white-50" style="max-width: 380px;">
          Browse drives you're eligible for, apply in a click, and track every
          application and interview in one place.
        </p>
        <ul class="list-unstyled text-white-50 small mt-4 d-flex flex-column gap-2">
          <li><i class="bi bi-check-circle me-2"></i>Only see drives you actually qualify for</li>
          <li><i class="bi bi-check-circle me-2"></i>Live status on every application</li>
          <li><i class="bi bi-check-circle me-2"></i>Your full placement history, exportable anytime</li>
        </ul>
      </div>
    </div>

    <div class="pp-auth-form-side py-4">
      <div class="pp-auth-card p-4 p-md-5" v-reveal>
        <div class="text-center mb-4 d-lg-none">
          <div class="pp-brand-icon-lg mx-auto mb-2"><i class="bi bi-person-badge"></i></div>
        </div>
        <h4 class="fw-bold mb-1">Student registration</h4>
        <p class="text-muted small mb-4">Create your account to browse and apply for drives</p>

        <div v-if="error" :key="error" class="alert alert-danger py-2 pp-shake">{{ error }}</div>
        <div v-if="success" class="alert alert-success py-2">{{ success }}</div>

        <form v-if="!success" @submit.prevent="submit" novalidate class="pp-field">
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
              <input v-model.trim="form.email" type="email" class="form-control" required autocomplete="username">
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
              <input v-model="form.password" type="password" class="form-control" required minlength="6" autocomplete="new-password">
            </div>
            <div class="col-md-6">
              <label class="form-label">Confirm password</label>
              <input v-model="form.confirm_password" type="password" class="form-control" required minlength="6" autocomplete="new-password">
            </div>
          </div>
          <button type="submit" class="btn pp-btn-gradient w-100 mt-4" :disabled="loading">
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
