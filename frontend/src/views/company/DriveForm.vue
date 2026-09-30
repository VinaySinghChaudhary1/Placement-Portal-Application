<template>
  <div class="container py-4" style="max-width:760px;">
    <h3 class="mb-4">{{ isEdit ? 'Edit drive' : 'Create a drive' }}</h3>
    <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
    <div v-if="success" class="alert alert-success py-2">{{ success }}</div>
    <form @submit.prevent="submit" class="card p-4">
      <div class="mb-3">
        <label class="form-label">Job title</label>
        <input v-model.trim="form.job_title" class="form-control" required>
      </div>
      <div class="mb-3">
        <label class="form-label">Job description</label>
        <textarea v-model.trim="form.job_description" class="form-control" rows="4" required></textarea>
      </div>
      <div class="row g-3">
        <div class="col-md-6">
          <label class="form-label">Eligible branches <span class="text-muted small">(comma separated, blank = all)</span></label>
          <input v-model.trim="branchesInput" class="form-control" placeholder="Computer Science, Electronics">
        </div>
        <div class="col-md-6">
          <label class="form-label">Eligible years <span class="text-muted small">(comma separated, blank = all)</span></label>
          <input v-model.trim="yearsInput" class="form-control" placeholder="2026, 2027">
        </div>
        <div class="col-md-4">
          <label class="form-label">Minimum CGPA</label>
          <input v-model.number="form.min_cgpa" type="number" step="0.01" min="0" max="10" class="form-control">
        </div>
        <div class="col-md-4">
          <label class="form-label">Package (LPA)</label>
          <input v-model.number="form.salary_package" type="number" step="0.1" min="0" class="form-control">
        </div>
        <div class="col-md-4">
          <label class="form-label">Location</label>
          <input v-model.trim="form.location" class="form-control">
        </div>
        <div class="col-md-6">
          <label class="form-label">Application deadline</label>
          <input v-model="form.application_deadline" type="datetime-local" class="form-control" required>
        </div>
      </div>
      <button type="submit" class="btn btn-primary mt-4" :disabled="loading">
        <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>{{ isEdit ? 'Save changes' : 'Submit for approval' }}
      </button>
    </form>
  </div>
</template>

<script>
import companyService from '@/services/companyService'

export default {
  name: 'CompanyDriveForm',
  props: { id: { type: [String, Number], default: null } },
  data() {
    return {
      form: { job_title: '', job_description: '', min_cgpa: 0, salary_package: null, location: '', application_deadline: '' },
      branchesInput: '', yearsInput: '', loading: false, error: '', success: ''
    }
  },
  computed: {
    isEdit() { return !!this.id }
  },
  async created() {
    if (this.isEdit) {
      const { data } = await companyService.getDrive(this.id)
      const d = data.drive
      this.form = {
        job_title: d.job_title, job_description: d.job_description, min_cgpa: d.min_cgpa,
        salary_package: d.salary_package, location: d.location,
        application_deadline: d.application_deadline ? d.application_deadline.replace(' ', 'T') : ''
      }
      this.branchesInput = (d.eligible_branches || []).join(', ')
      this.yearsInput = (d.eligible_years || []).join(', ')
    }
  },
  methods: {
    async submit() {
      this.loading = true
      this.error = ''
      const payload = {
        ...this.form,
        eligible_branches: this.branchesInput.split(',').map((s) => s.trim()).filter(Boolean),
        eligible_years: this.yearsInput.split(',').map((s) => s.trim()).filter(Boolean).map(Number)
      }
      try {
        if (this.isEdit) {
          await companyService.updateDrive(this.id, payload)
          this.success = 'Drive updated and resubmitted for approval.'
        } else {
          await companyService.createDrive(payload)
          this.success = 'Drive submitted for admin approval.'
        }
        setTimeout(() => this.$router.push('/company/drives'), 1200)
      } catch (e) {
        this.error = e.response?.data?.message || 'Could not save the drive.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
