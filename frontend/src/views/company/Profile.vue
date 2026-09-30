<template>
  <div class="container py-4" style="max-width:700px;">
    <h3 class="mb-4">Company profile</h3>
    <div v-if="toast" class="alert alert-success py-2">{{ toast }}</div>
    <form v-if="form" @submit.prevent="save" class="card p-4">
      <div class="row g-3">
        <div class="col-md-6">
          <label class="form-label">Company name</label>
          <input v-model.trim="form.company_name" class="form-control" required>
        </div>
        <div class="col-md-6">
          <label class="form-label">Industry</label>
          <input v-model.trim="form.industry" class="form-control">
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
          <label class="form-label">HR email</label>
          <input v-model.trim="form.hr_email" type="email" class="form-control">
        </div>
        <div class="col-md-6">
          <label class="form-label">Website</label>
          <input v-model.trim="form.website" class="form-control">
        </div>
        <div class="col-12">
          <label class="form-label">About</label>
          <textarea v-model.trim="form.description" class="form-control" rows="4"></textarea>
        </div>
      </div>
      <div class="mt-3">
        <span class="text-muted small">Status: </span>
        <span class="badge text-capitalize" :class="form.approval_status==='approved' ? 'bg-success' : form.approval_status==='pending' ? 'bg-warning text-dark' : 'bg-danger'">{{ form.approval_status }}</span>
      </div>
      <button class="btn btn-primary mt-3" :disabled="saving">
        <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>Save changes
      </button>
    </form>
  </div>
</template>

<script>
import companyService from '@/services/companyService'

export default {
  name: 'CompanyProfile',
  data() { return { form: null, saving: false, toast: '' } },
  async created() {
    const { data } = await companyService.getProfile()
    this.form = data.profile
  },
  methods: {
    async save() {
      this.saving = true
      try {
        await companyService.updateProfile(this.form)
        this.toast = 'Profile updated.'
        setTimeout(() => { this.toast = '' }, 3000)
      } finally { this.saving = false }
    }
  }
}
</script>
