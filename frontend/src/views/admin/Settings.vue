<template>
  <div class="container py-4" style="max-width:700px;">
    <h3 class="mb-4">Scheduled job settings</h3>
    <div v-if="toast" class="alert alert-success py-2">{{ toast }}</div>
    <form v-if="form" @submit.prevent="save">
      <div class="card p-3 mb-3">
        <h6><i class="bi bi-bell me-2"></i>Daily deadline reminders</h6>
        <p class="small text-muted">Runs once a day and reminds eligible students who haven't applied yet, about drives whose deadline is approaching.</p>
        <div class="row g-2">
          <div class="col-4">
            <label class="form-label small">Hour (0-23)</label>
            <input type="number" min="0" max="23" v-model.number="form.daily_reminder_hour" class="form-control form-control-sm">
          </div>
          <div class="col-4">
            <label class="form-label small">Minute</label>
            <input type="number" min="0" max="59" v-model.number="form.daily_reminder_minute" class="form-control form-control-sm">
          </div>
          <div class="col-4">
            <label class="form-label small">Window (days before deadline)</label>
            <input type="number" min="1" max="30" v-model.number="form.daily_reminder_window_days" class="form-control form-control-sm">
          </div>
        </div>
      </div>
      <div class="card p-3 mb-3">
        <h6><i class="bi bi-envelope-paper me-2"></i>Monthly activity report</h6>
        <p class="small text-muted">Emailed automatically to the admin on the chosen day of every month.</p>
        <div class="row g-2">
          <div class="col-4">
            <label class="form-label small">Day of month</label>
            <input type="number" min="1" max="28" v-model.number="form.monthly_report_day" class="form-control form-control-sm">
          </div>
          <div class="col-4">
            <label class="form-label small">Hour (0-23)</label>
            <input type="number" min="0" max="23" v-model.number="form.monthly_report_hour" class="form-control form-control-sm">
          </div>
          <div class="col-4">
            <label class="form-label small">Minute</label>
            <input type="number" min="0" max="59" v-model.number="form.monthly_report_minute" class="form-control form-control-sm">
          </div>
        </div>
      </div>
      <button class="btn btn-primary" :disabled="saving">
        <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>Save settings
      </button>
    </form>
  </div>
</template>

<script>
import adminService from '@/services/adminService'

export default {
  name: 'AdminSettings',
  data() { return { form: null, saving: false, toast: '' } },
  async created() {
    const { data } = await adminService.getSettings()
    this.form = data
  },
  methods: {
    async save() {
      this.saving = true
      try {
        await adminService.updateSettings(this.form)
        this.toast = 'Settings saved. The scheduler will pick up the new times automatically.'
        setTimeout(() => { this.toast = '' }, 4000)
      } finally { this.saving = false }
    }
  }
}
</script>
