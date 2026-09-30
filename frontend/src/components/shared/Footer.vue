<template>
  <footer class="pp-footer pt-5 pb-4 mt-5">
    <div class="container">
      <div class="row g-4">
        <div class="col-lg-4">
          <div class="d-flex align-items-center mb-3">
            <span class="pp-brand-icon me-2"><i class="bi bi-mortarboard-fill"></i></span>
            <span class="fw-bold text-white fs-5">Placement Portal</span>
          </div>
          <p class="small mb-3" style="max-width: 320px;">
            One platform for the institute placement cell, recruiting companies and students —
            drives, applications, interviews and placement history, end to end.
          </p>
          <div class="d-flex gap-2">
            <a href="#" class="pp-social-btn" title="LinkedIn" aria-label="LinkedIn"><i class="bi bi-linkedin"></i></a>
            <a href="#" class="pp-social-btn" title="Twitter / X" aria-label="Twitter / X"><i class="bi bi-twitter-x"></i></a>
            <a href="#" class="pp-social-btn" title="Instagram" aria-label="Instagram"><i class="bi bi-instagram"></i></a>
          </div>
        </div>

        <div class="col-6 col-lg-2">
          <h6 class="fw-semibold mb-3">Quick links</h6>
          <ul class="list-unstyled small d-flex flex-column gap-2">
            <li><router-link to="/home">Home</router-link></li>
            <li><router-link to="/contact">Contact</router-link></li>
            <li><router-link to="/login">Login</router-link></li>
          </ul>
        </div>

        <div class="col-6 col-lg-3">
          <h6 class="fw-semibold mb-3">For students &amp; companies</h6>
          <ul class="list-unstyled small d-flex flex-column gap-2">
            <li><router-link to="/register/student"><i class="bi bi-person-badge me-1"></i>Student registration</router-link></li>
            <li><router-link to="/register/company"><i class="bi bi-building me-1"></i>Company registration</router-link></li>
          </ul>
        </div>

        <div class="col-lg-3">
          <h6 class="fw-semibold mb-3">Contact</h6>
          <ul class="list-unstyled small d-flex flex-column gap-2">
            <li><i class="bi bi-envelope me-2"></i><a href="mailto:placements@institute.edu">placements@institute.edu</a></li>
            <li><i class="bi bi-telephone me-2"></i><span>+91 00000 00000</span></li>
            <li><i class="bi bi-geo-alt me-2"></i><span>Institute Placement Cell, Campus Road</span></li>
          </ul>
        </div>
      </div>

      <hr class="border-secondary-subtle opacity-25 my-4">

      <div class="d-flex flex-wrap justify-content-between gap-2 small">
        <span>&copy; {{ year }} Placement Portal — Institute Placement Cell</span>
        <span>Built with Flask, Vue.js &amp; Bootstrap</span>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'Footer',
  computed: { year() { return new Date().getFullYear() } }
}
</script>

<style scoped>
.pp-brand-icon {
  width: 34px;
  height: 34px;
  border-radius: 0.6rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--pp-gradient-brand);
  color: #fff;
  font-size: 1rem;
}
</style>
