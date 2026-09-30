<template>
  <div>
    <section class="pp-hero pp-gradient-anim py-5">
      <span class="pp-blob" style="width:220px;height:220px;background:#7c3aed;top:-50px;right:10%;"></span>
      <div class="container py-5 text-center position-relative">
        <div class="pp-eyebrow mb-3" v-reveal>Get in touch</div>
        <h1 class="display-5 fw-bold mb-3" v-reveal="1">We'd love to hear from you</h1>
        <p class="lead mx-auto" style="max-width: 640px; opacity: 0.92;" v-reveal="2">
          Questions about the placement process, a technical issue, or a company
          that wants to know more — the placement cell is one message away.
        </p>
      </div>
    </section>

    <section class="pp-section container">
      <div class="row g-4 mb-5">
        <div class="col-md-4" v-reveal>
          <div class="pp-card h-100 p-4 text-center">
            <div class="pp-card-icon mb-3 mx-auto"><i class="bi bi-envelope"></i></div>
            <h6 class="fw-semibold">Email</h6>
            <a href="mailto:placements@institute.edu" class="small">placements@institute.edu</a>
          </div>
        </div>
        <div class="col-md-4" v-reveal="1">
          <div class="pp-card h-100 p-4 text-center">
            <div class="pp-card-icon mb-3 mx-auto"><i class="bi bi-telephone"></i></div>
            <h6 class="fw-semibold">Phone</h6>
            <span class="small text-muted">+91 00000 00000</span>
          </div>
        </div>
        <div class="col-md-4" v-reveal="2">
          <div class="pp-card h-100 p-4 text-center">
            <div class="pp-card-icon mb-3 mx-auto"><i class="bi bi-geo-alt"></i></div>
            <h6 class="fw-semibold">Office</h6>
            <span class="small text-muted">Institute Placement Cell, Campus Road</span>
          </div>
        </div>
      </div>

      <div class="row justify-content-center">
        <div class="col-lg-7">
          <div class="pp-card p-4 p-md-5" v-reveal>
            <h4 class="fw-bold mb-1">Send a message</h4>
            <p class="text-muted small mb-4">We typically reply within 1-2 business days.</p>

            <div v-if="result.type" :key="result.message" class="alert py-2" :class="result.type === 'error' ? 'alert-danger pp-shake' : 'alert-success'">
              {{ result.message }}
            </div>

            <form v-if="result.type !== 'success'" @submit.prevent="submit" novalidate class="pp-field">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Your name</label>
                  <input v-model.trim="form.name" class="form-control" required maxlength="100">
                </div>
                <div class="col-md-6">
                  <label class="form-label">Email address</label>
                  <input v-model.trim="form.email" type="email" class="form-control" required>
                </div>
                <div class="col-12">
                  <label class="form-label">Subject</label>
                  <input v-model.trim="form.subject" class="form-control" maxlength="150" placeholder="What's this about?">
                </div>
                <div class="col-12">
                  <label class="form-label">Message</label>
                  <textarea v-model.trim="form.message" class="form-control" rows="5" required minlength="10" maxlength="2000" placeholder="How can we help?"></textarea>
                </div>
                <!-- Honeypot: invisible to real users, off-screen rather than display:none so
                     basic bots that skip hidden fields still fill it. Left blank by a human. -->
                <div class="pp-honeypot" aria-hidden="true">
                  <label>Company website</label>
                  <input v-model="form.company_website" type="text" tabindex="-1" autocomplete="off">
                </div>
              </div>
              <button type="submit" class="btn pp-btn-gradient w-100 mt-4" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                <span v-else><i class="bi bi-send me-2"></i></span>Send message
              </button>
            </form>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import commonService from '@/services/commonService'

export default {
  name: 'Contact',
  data() {
    return {
      form: { name: '', email: '', subject: '', message: '', company_website: '' },
      loading: false,
      result: { type: '', message: '' }
    }
  },
  methods: {
    async submit() {
      this.loading = true
      this.result = { type: '', message: '' }
      try {
        const { data } = await commonService.submitContact(this.form)
        this.result = { type: 'success', message: data.message || 'Thanks — your message has been sent.' }
      } catch (e) {
        this.result = { type: 'error', message: e.response?.data?.message || 'Could not send your message. Please try again.' }
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
/* Standard "visually hidden" pattern — kept in normal flow (no huge negative
   offset that can cause page overflow/scrollbars) but invisible and
   unreachable by keyboard/tab for real users. */
.pp-honeypot {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
