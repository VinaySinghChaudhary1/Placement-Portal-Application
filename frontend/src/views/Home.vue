<template>
  <div>
    <section class="auth-shell" style="min-height: 80vh;">
      <div class="container text-center py-5">
        <i class="bi bi-mortarboard-fill display-1 text-primary"></i>
        <h1 class="fw-bold mt-3">Placement Portal</h1>
        <p class="lead text-muted mx-auto" style="max-width:640px;">
          One platform for the institute placement cell, recruiting companies, and students —
          manage drives, applications, interviews and placement history end to end.
        </p>
        <div v-if="isLoggedIn" class="d-flex justify-content-center gap-3 mt-4 flex-wrap">
          <router-link :to="dashboardLink" class="btn btn-primary btn-lg px-4"><i class="bi bi-speedometer2 me-2"></i>Go to my dashboard</router-link>
        </div>
        <div v-else class="d-flex justify-content-center gap-3 mt-4 flex-wrap">
          <router-link to="/register/student" class="btn btn-primary btn-lg px-4"><i class="bi bi-person-badge me-2"></i>I'm a student</router-link>
          <router-link to="/register/company" class="btn btn-outline-primary btn-lg px-4"><i class="bi bi-building me-2"></i>I'm a company</router-link>
          <router-link to="/login" class="btn btn-outline-secondary btn-lg px-4"><i class="bi bi-box-arrow-in-right me-2"></i>Login</router-link>
        </div>
      </div>
    </section>
    <section class="container py-5">
      <div class="row g-4">
        <div class="col-md-4">
          <div class="card h-100 p-4">
            <i class="bi bi-shield-check fs-2 text-primary mb-2"></i>
            <h5>Admin oversight</h5>
            <p class="text-muted small mb-0">Every company and drive is vetted by the institute placement cell before it goes live.</p>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card h-100 p-4">
            <i class="bi bi-briefcase fs-2 text-primary mb-2"></i>
            <h5>Streamlined drives</h5>
            <p class="text-muted small mb-0">Companies post drives with clear eligibility criteria; students only see what they qualify for.</p>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card h-100 p-4">
            <i class="bi bi-graph-up-arrow fs-2 text-primary mb-2"></i>
            <h5>Track everything</h5>
            <p class="text-muted small mb-0">Applications, interviews and placement history, all in one dashboard with real-time status.</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'Home',
  computed: {
    ...mapGetters('auth', ['isLoggedIn', 'role']),
    dashboardLink() {
      if (this.role === 'admin') return '/admin'
      if (this.role === 'company') return '/company'
      if (this.role === 'student') return '/student'
      return '/home'
    }
  }
}
</script>
