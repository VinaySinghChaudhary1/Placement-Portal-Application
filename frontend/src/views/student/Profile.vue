<template>
  <div class="container py-4" style="max-width:700px;">
    <h3 class="mb-4">My profile</h3>
    <div v-if="toast" class="alert alert-success py-2">{{ toast }}</div>
    <form v-if="form" @submit.prevent="save" class="card p-4 mb-3">
      <div class="row g-3">
        <div class="col-md-6">
          <label class="form-label">Full name</label>
          <input v-model.trim="form.full_name" class="form-control" required>
        </div>
        <div class="col-md-6">
          <label class="form-label">Phone</label>
          <input v-model.trim="form.phone" class="form-control">
        </div>
        <div class="col-md-4">
          <label class="form-label">Branch</label>
          <input v-model.trim="form.branch" class="form-control" required>
        </div>
        <div class="col-md-4">
          <label class="form-label">Graduation year</label>
          <input v-model.number="form.year" type="number" class="form-control" required>
        </div>
        <div class="col-md-4">
          <label class="form-label">CGPA</label>
          <input v-model.number="form.cgpa" type="number" step="0.01" min="0" max="10" class="form-control" required>
        </div>
      </div>
      <button class="btn btn-primary mt-3" :disabled="saving">
        <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>Save changes
      </button>
    </form>

    <div class="card p-4">
      <h6>Resume</h6>
      <p class="small text-muted mb-2" v-if="form && form.resume_filename">Current: {{ form.resume_filename }}</p>
      <p class="small text-muted mb-2" v-else>No resume uploaded yet.</p>
      <input type="file" class="form-control mb-2" ref="fileInput" accept=".pdf,.doc,.docx">
      <button class="btn btn-outline-primary btn-sm" @click="upload" :disabled="uploading">
        <span v-if="uploading" class="spinner-border spinner-border-sm me-2"></span>Upload resume
      </button>
    </div>
  </div>
</template>

<script>
import studentService from '@/services/studentService'

export default {
  name: 'StudentProfile',
  data() { return { form: null, saving: false, uploading: false, toast: '' } },
  async created() {
    const { data } = await studentService.getProfile()
    this.form = data.profile
  },
  methods: {
    async save() {
      this.saving = true
      try {
        await studentService.updateProfile(this.form)
        this.toast = 'Profile updated.'
        setTimeout(() => { this.toast = '' }, 3000)
      } finally { this.saving = false }
    },
    async upload() {
      const file = this.$refs.fileInput.files[0]
      if (!file) return
      this.uploading = true
      try {
        const fd = new FormData()
        fd.append('resume', file)
        const { data } = await studentService.uploadResume(fd)
        this.form = data.profile
        this.toast = 'Resume uploaded.'
        setTimeout(() => { this.toast = '' }, 3000)
      } finally { this.uploading = false }
    }
  }
}
</script>
