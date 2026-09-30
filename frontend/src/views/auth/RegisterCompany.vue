<template>
  <div class="pp-auth-shell">
    <div class="pp-auth-panel p-5 flex-column justify-content-center">
      <span class="pp-blob" style="width:220px;height:220px;background:#198754;top:-40px;left:-40px;"></span>
      <span class="pp-blob" style="width:180px;height:180px;background:#22d3ee;bottom:-30px;right:-30px;animation-delay:-3s;"></span>
      <div class="position-relative">
        <div class="pp-brand-icon-lg mb-4"><i class="bi bi-building"></i></div>
        <h2 class="fw-bold text-white mb-3">Hire from a<br>verified talent pool</h2>
        <p class="text-white-50" style="max-width: 380px;">
          Post drives with clear eligibility criteria, review applicants, schedule
          interviews and export reports — all from one dashboard.
        </p>
        <ul class="list-unstyled text-white-50 small mt-4 d-flex flex-column gap-2">
          <li><i class="bi bi-check-circle me-2"></i>Every drive reviewed by the placement cell</li>
          <li><i class="bi bi-check-circle me-2"></i>Applicants filtered by your own eligibility rules</li>
          <li><i class="bi bi-check-circle me-2"></i>One-click CSV export of drives &amp; applicants</li>
        </ul>
      </div>
    </div>

    <div class="pp-auth-form-side py-4">
      <div class="pp-auth-card p-4 p-md-5" v-reveal>
        <div class="text-center mb-4 d-lg-none">
          <div class="pp-brand-icon-lg mx-auto mb-2"><i class="bi bi-building"></i></div>
        </div>
        <h4 class="fw-bold mb-1">Company registration</h4>
        <p class="text-muted small mb-4">Register your company — an admin will review before you can post drives</p>

        <div v-if="error" :key="error" class="alert alert-danger py-2 pp-shake">{{ error }}</div>
        <div v-if="success" class="alert alert-success py-2">{{ success }}</div>

        <form v-if="!success" @submit.prevent="submit" novalidate class="pp-field">
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
              <input v-model.trim="form.email" type="email" class="form-control" required autocomplete="username">
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
              <input v-model="form.password" type="password" class="form-control" required minlength="6" autocomplete="new-password">
            </div>
            <div class="col-md-6">
              <label class="form-label">Confirm password</label>
              <input v-model="form.confirm_password" type="password" class="form-control" required minlength="6" autocomplete="new-password">
            </div>
          </div>
          <button type="submit" class="btn pp-btn-gradient w-100 mt-4" :disabled="loading">
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
