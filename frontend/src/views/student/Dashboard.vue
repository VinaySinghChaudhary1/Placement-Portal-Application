<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
      <h3 class="mb-0">Welcome, {{ profile ? profile.full_name : '' }}</h3>
      <button class="btn btn-outline-primary btn-sm" @click="exportCsv" :disabled="exporting">
        <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
        <i v-else class="bi bi-download me-1"></i>Export my applications (CSV)
      </button>
    </div>
    <div v-if="exportMsg" class="alert alert-info py-2 d-flex justify-content-between align-items-center">
      <span>{{ exportMsg }}</span>
      <button v-if="exportLink" class="btn btn-sm btn-primary" @click="downloadExport">
        <i class="bi bi-download me-1"></i>Download CSV
      </button>
    </div>
    <div v-if="profile && profile.blacklisted" class="alert alert-danger">
      You have been blacklisted by the admin: {{ profile.blacklist_reason }}. You cannot apply to new drives.
    </div>

    <div class="row g-3 mb-4">
      <div class="col-6 col-md-3"><StatCard label="Open drives" :value="counts.open" icon="bi-briefcase" /></div>
      <div class="col-6 col-md-3"><StatCard label="Eligible for you" :value="counts.eligible" icon="bi-check2-circle" color="linear-gradient(135deg,#198754,#146c43)" /></div>
      <div class="col-6 col-md-3"><StatCard label="Applications" :value="counts.applications" icon="bi-file-earmark-text" color="linear-gradient(135deg,#fd7e14,#dc6803)" /></div>
      <div class="col-6 col-md-3"><StatCard label="Selected" :value="counts.selected" icon="bi-trophy" color="linear-gradient(135deg,#6f42c1,#59339d)" /></div>
    </div>

    <div class="row g-3">
      <div class="col-md-6">
        <router-link to="/student/drives" class="card p-4 text-decoration-none text-dark h-100">
          <i class="bi bi-search fs-3 text-primary mb-2"></i>
          <h6>Browse placement drives</h6>
          <p class="small text-muted mb-0">See approved drives filtered by your eligibility.</p>
        </router-link>
      </div>
      <div class="col-md-6">
        <router-link to="/student/applications" class="card p-4 text-decoration-none text-dark h-100">
          <i class="bi bi-clock-history fs-3 text-primary mb-2"></i>
          <h6>My applications &amp; history</h6>
          <p class="small text-muted mb-0">Track status of every drive you've applied to.</p>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import studentService from '@/services/studentService'
import StatCard from '@/components/shared/StatCard.vue'
import { downloadFromLink } from '@/services/download'

export default {
  name: 'StudentDashboard',
  components: { StatCard },
  data() {
    return {
      profile: null,
      counts: { open: 0, eligible: 0, applications: 0, selected: 0 },
      exporting: false,
      exportMsg: '',
      exportLink: ''
    }
  },
  async created() {
    const [{ data: profileData }, { data: drivesData }, { data: appsData }] = await Promise.all([
      studentService.getProfile(), studentService.browseDrives(), studentService.myApplications()
    ])
    this.profile = profileData.profile
    this.counts.open = drivesData.items.length
    this.counts.eligible = drivesData.items.filter((d) => d.eligible).length
    this.counts.applications = appsData.items.length
    this.counts.selected = appsData.items.filter((a) => a.status === 'selected').length
  },
  methods: {
    async exportCsv() {
      this.exporting = true
      this.exportMsg = ''
      this.exportLink = ''
      try {
        const { data } = await studentService.exportCsv()
        this.exportMsg = 'Export started — hang on a moment...'
        this.poll(data.task_id)
      } finally {
        this.exporting = false
      }
    },
    poll(taskId, attempt = 0) {
      if (attempt > 15) return
      setTimeout(async () => {
        const { data } = await studentService.exportStatus(taskId)
        if (data.state === 'SUCCESS') {
          this.exportLink = `/api/exports/csv/${data.filename}`
          this.exportMsg = `Export ready: ${data.filename}`
          // Download starts automatically; the button above lets them re-download.
          this.downloadExport()
        } else if (data.state === 'FAILURE') {
          this.exportMsg = 'Export failed. Please try again.'
        } else {
          this.poll(taskId, attempt + 1)
        }
      }, 2000)
    },
    async downloadExport() {
      if (!this.exportLink) return
      try {
        await downloadFromLink(this.exportLink)
      } catch (e) {
        console.error('[StudentDashboard] download failed:', e)
        this.exportMsg = 'Download failed — click "Download CSV" to try again.'
      }
    }
  }
}
</script>
