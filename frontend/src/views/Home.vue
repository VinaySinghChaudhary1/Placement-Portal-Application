<template>
  <div>
    <!-- ============================================================ HERO -->
    <section class="pp-hero pp-gradient-anim py-5">
      <span class="pp-blob" style="width:260px;height:260px;background:#7c3aed;top:-60px;left:-60px;"></span>
      <span class="pp-blob" style="width:220px;height:220px;background:#22d3ee;bottom:-70px;right:-40px;animation-delay:-3s;"></span>
      <span class="pp-blob" style="width:160px;height:160px;background:#0d6efd;top:40%;right:12%;animation-delay:-6s;"></span>

      <div class="container py-5 position-relative">
        <div class="row align-items-center g-5">
          <div class="col-lg-7 text-center text-lg-start">
            <div class="pp-eyebrow mb-3" v-reveal>Institute Placement Cell</div>
            <h1 class="display-4 fw-bold mb-3" v-reveal="1">
              Where talent meets <span class="text-gradient-shine">opportunity</span>
            </h1>
            <p class="lead mb-4" style="max-width: 560px; opacity: 0.92;" v-reveal="2">
              One platform for the placement cell, recruiting companies and students —
              manage drives, applications, interviews and placement history end to end.
            </p>

            <div v-if="isLoggedIn" class="d-flex justify-content-center justify-content-lg-start gap-3 flex-wrap" v-reveal="3">
              <router-link :to="dashboardLink" class="btn btn-lg pp-btn-gradient px-4">
                <i class="bi bi-speedometer2 me-2"></i>Go to my dashboard
              </router-link>
            </div>
            <div v-else class="d-flex justify-content-center justify-content-lg-start gap-3 flex-wrap" v-reveal="3">
              <router-link to="/register/student" class="btn btn-lg pp-btn-gradient px-4">
                <i class="bi bi-person-badge me-2"></i>I'm a student
              </router-link>
              <router-link to="/register/company" class="btn btn-lg pp-btn-ghost-light px-4">
                <i class="bi bi-building me-2"></i>I'm a company
              </router-link>
              <router-link to="/login" class="btn btn-lg pp-btn-ghost-light px-4">
                <i class="bi bi-box-arrow-in-right me-2"></i>Login
              </router-link>
            </div>
          </div>

          <div class="col-lg-5 d-none d-lg-flex justify-content-center">
            <div class="pp-hero-art" v-reveal="2">
              <div class="pp-float-chip pp-pulse" style="top:4%; left:8%;"><i class="bi bi-mortarboard-fill"></i></div>
              <div class="pp-float-chip" style="top:55%; left:-4%; animation-delay:-2s;"><i class="bi bi-briefcase-fill"></i></div>
              <div class="pp-float-chip" style="top:70%; left:55%; animation-delay:-4s;"><i class="bi bi-trophy-fill"></i></div>
              <div class="pp-float-chip" style="top:10%; left:60%; animation-delay:-1s;"><i class="bi bi-graph-up-arrow"></i></div>
              <div class="pp-hero-ring"></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ===================================================== WHY US -->
    <section class="pp-section container">
      <div class="text-center mb-5">
        <div class="pp-eyebrow text-primary mb-2" v-reveal>Why this portal</div>
        <h2 class="fw-bold" v-reveal="1">Everything placements need, in one place</h2>
      </div>
      <div class="row g-4">
        <div class="col-md-4" v-reveal>
          <div class="pp-card h-100 p-4">
            <div class="pp-card-icon mb-3"><i class="bi bi-shield-check"></i></div>
            <h5>Admin oversight</h5>
            <p class="text-muted small mb-0">Every company and drive is vetted by the institute placement cell before it goes live.</p>
          </div>
        </div>
        <div class="col-md-4" v-reveal="1">
          <div class="pp-card h-100 p-4">
            <div class="pp-card-icon mb-3"><i class="bi bi-briefcase"></i></div>
            <h5>Streamlined drives</h5>
            <p class="text-muted small mb-0">Companies post drives with clear eligibility criteria; students only see what they qualify for.</p>
          </div>
        </div>
        <div class="col-md-4" v-reveal="2">
          <div class="pp-card h-100 p-4">
            <div class="pp-card-icon mb-3"><i class="bi bi-graph-up-arrow"></i></div>
            <h5>Track everything</h5>
            <p class="text-muted small mb-0">Applications, interviews and placement history, all in one dashboard with real-time status.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- =============================================== BUILT FOR ROLES -->
    <section class="pp-section" style="background: #f5f7fb;">
      <div class="container">
        <div class="text-center mb-5">
          <div class="pp-eyebrow text-primary mb-2" v-reveal>Built for every role</div>
          <h2 class="fw-bold" v-reveal="1">One portal, three experiences</h2>
        </div>
        <div class="row g-4">
          <div class="col-md-4" v-reveal>
            <div class="pp-card h-100 p-4">
              <div class="pp-card-icon mb-3" style="background: var(--pp-gradient-student);"><i class="bi bi-person-badge"></i></div>
              <h5>Students</h5>
              <ul class="small text-muted ps-3 mb-3">
                <li>Browse drives you're eligible for</li>
                <li>Apply and track status in real time</li>
                <li>See your application &amp; interview history</li>
              </ul>
              <router-link v-if="!isLoggedIn" to="/register/student" class="btn btn-sm btn-outline-primary">Register as student</router-link>
            </div>
          </div>
          <div class="col-md-4" v-reveal="1">
            <div class="pp-card h-100 p-4">
              <div class="pp-card-icon mb-3" style="background: var(--pp-gradient-company);"><i class="bi bi-building"></i></div>
              <h5>Companies</h5>
              <ul class="small text-muted ps-3 mb-3">
                <li>Post drives with eligibility criteria</li>
                <li>Review applicants &amp; schedule interviews</li>
                <li>Export reports as CSV anytime</li>
              </ul>
              <router-link v-if="!isLoggedIn" to="/register/company" class="btn btn-sm btn-outline-success">Register as company</router-link>
            </div>
          </div>
          <div class="col-md-4" v-reveal="2">
            <div class="pp-card h-100 p-4">
              <div class="pp-card-icon mb-3" style="background: linear-gradient(135deg, var(--pp-indigo), var(--pp-violet));"><i class="bi bi-ui-checks-grid"></i></div>
              <h5>Placement cell</h5>
              <ul class="small text-muted ps-3 mb-3">
                <li>Approve companies &amp; drives before they go live</li>
                <li>Monthly activity reports &amp; portal-wide trends</li>
                <li>Full data export whenever you need it</li>
              </ul>
              <span v-if="!isLoggedIn" class="small text-muted fst-italic">Admin access is provisioned by the institute.</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ===================================================== HOW IT WORKS -->
    <section class="pp-section container">
      <div class="text-center mb-5">
        <div class="pp-eyebrow text-primary mb-2" v-reveal>Process</div>
        <h2 class="fw-bold" v-reveal="1">How it works</h2>
      </div>
      <div class="row g-4 position-relative">
        <div class="pp-step-line d-none d-md-block"></div>
        <div class="col-6 col-md-3 text-center" v-reveal>
          <div class="pp-step-num mx-auto mb-3">1</div>
          <h6 class="fw-semibold">Register</h6>
          <p class="small text-muted">Students and companies sign up in minutes.</p>
        </div>
        <div class="col-6 col-md-3 text-center" v-reveal="1">
          <div class="pp-step-num mx-auto mb-3">2</div>
          <h6 class="fw-semibold">Get verified</h6>
          <p class="small text-muted">The placement cell approves companies &amp; drives.</p>
        </div>
        <div class="col-6 col-md-3 text-center" v-reveal="2">
          <div class="pp-step-num mx-auto mb-3">3</div>
          <h6 class="fw-semibold">Apply &amp; review</h6>
          <p class="small text-muted">Eligible students apply; companies shortlist &amp; interview.</p>
        </div>
        <div class="col-6 col-md-3 text-center" v-reveal="3">
          <div class="pp-step-num mx-auto mb-3">4</div>
          <h6 class="fw-semibold">Get placed</h6>
          <p class="small text-muted">Track the outcome end to end, all in one dashboard.</p>
        </div>
      </div>
    </section>

    <!-- ===================================================== FINAL CTA -->
    <section class="pp-hero py-5">
      <span class="pp-blob" style="width:200px;height:200px;background:#22d3ee;top:-40px;right:-40px;"></span>
      <div class="container py-4 text-center position-relative">
        <h2 class="fw-bold mb-3" v-reveal>Ready to get started?</h2>
        <p class="mb-4" style="opacity:0.9;" v-reveal="1">Join your institute's placement portal today.</p>
        <div v-if="isLoggedIn" class="d-flex justify-content-center" v-reveal="2">
          <router-link :to="dashboardLink" class="btn btn-lg pp-btn-gradient px-4">Go to my dashboard</router-link>
        </div>
        <div v-else class="d-flex justify-content-center gap-3 flex-wrap" v-reveal="2">
          <router-link to="/register/student" class="btn btn-lg pp-btn-gradient px-4">Get started as a student</router-link>
          <router-link to="/contact" class="btn btn-lg pp-btn-ghost-light px-4">Contact the placement cell</router-link>
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

<style scoped>
.text-gradient-shine {
  background: linear-gradient(90deg, #a5b4fc, #67e8f9, #a5b4fc);
  background-size: 200% auto;
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation: pp-gradient-shift 6s linear infinite;
}

.pp-hero-art {
  position: relative;
  width: 320px;
  height: 320px;
}
.pp-hero-ring {
  position: absolute;
  inset: 20px;
  border: 2px dashed rgba(255, 255, 255, 0.25);
  border-radius: 50%;
}
.pp-float-chip {
  position: absolute;
  width: 68px;
  height: 68px;
  border-radius: 1.1rem;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  color: #fff;
  animation: pp-float 7s ease-in-out infinite;
  box-shadow: 0 16px 34px -12px rgba(0, 0, 0, 0.35);
}

.pp-step-num {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  color: #fff;
  background: var(--pp-gradient-brand);
  box-shadow: 0 10px 22px -8px rgba(99, 102, 241, 0.55);
  position: relative;
  z-index: 1;
}

@media (prefers-reduced-motion: reduce) {
  .text-gradient-shine { animation: none; }
}
</style>
