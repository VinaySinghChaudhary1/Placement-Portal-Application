<template>
  <div class="container py-4" style="max-width:800px;">
    <router-link to="/student/drives" class="small text-decoration-none"><i class="bi bi-arrow-left me-1"></i>Back to drives</router-link>
    <div v-if="drive" class="card p-4 mt-2">
      <div class="d-flex justify-content-between align-items-start flex-wrap gap-2">
        <div>
          <h3 class="mb-1">{{ drive.job_title }}</h3>
          <h6 class="text-muted">
            <router-link :to="`/companies/${drive.company_id}`" class="text-decoration-none">{{ drive.company_name }}</router-link>
          </h6>
        </div>
        <span v-if="drive.already_applied" class="badge bg-success fs-6">Applied</span>
      </div>

      <p class="mt-3">{{ drive.job_description }}</p>

      <div class="row g-3 my-2">
        <div class="col-6 col-md-3"><div class="text-muted small">Location</div><div class="fw-semibold">{{ drive.location || '—' }}</div></div>
        <div class="col-6 col-md-3"><div class="text-muted small">Package</div><div class="fw-semibold">{{ drive.salary_package ? drive.salary_package + ' LPA' : '—' }}</div></div>
        <div class="col-6 col-md-3"><div class="text-muted small">Min CGPA</div><div class="fw-semibold">{{ drive.min_cgpa }}</div></div>
        <div class="col-6 col-md-3"><div class="text-muted small">Deadline</div><div class="fw-semibold">{{ drive.application_deadline }}</div></div>
      </div>
      <div class="mb-3">
        <span class="text-muted small">Eligible branches: </span>
        <span v-if="drive.eligible_branches.length">{{ drive.eligible_branches.join(', ') }}</span>
        <span v-else>All branches</span>
        <br>
        <span class="text-muted small">Eligible years: </span>
        <span v-if="drive.eligible_years.length">{{ drive.eligible_years.join(', ') }}</span>
        <span v-else>All years</span>
      </div>

      <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
      <div v-if="!drive.eligible && !drive.already_applied" class="alert alert-warning py-2">{{ drive.ineligible_reason }}</div>

      <div class="d-flex gap-2">
        <button v-if="!drive.already_applied" class="btn btn-primary" :disabled="!drive.eligible || applying" @click="apply">
          <span v-if="applying" class="spinner-border spinner-border-sm me-2"></span>Apply now
        </button>
        <span v-else class="text-success"><i class="bi bi-check-circle me-1"></i>You've already applied to this drive.</span>
      </div>
    </div>
  </div>
</template>

<script>
import studentService from '@/services/studentService'

export default {
  name: 'StudentDriveDetail',
  props: { id: { type: [String, Number], required: true } },
  data() { return { drive: null, applying: false, error: '' } },
  async created() { await this.load() },
  methods: {
    async load() {
      const { data } = await studentService.getDrive(this.id)
      this.drive = data.drive
    },
    async apply() {
      this.applying = true
      this.error = ''
      try {
        await studentService.apply(this.id)
        await this.load()
      } catch (e) {
        this.error = e.response?.data?.message || 'Could not submit application.'
      } finally {
        this.applying = false
      }
    }
  }
}
</script>
