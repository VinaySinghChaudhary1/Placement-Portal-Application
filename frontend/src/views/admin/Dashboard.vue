<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-4">
      <h3 class="mb-0">Welcome, Admin</h3>
      <button class="btn btn-outline-primary" @click="exportCsv" :disabled="exporting">
        <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
        <i v-else class="bi bi-download me-1"></i>Export all data (CSV)
      </button>
    </div>

    <div v-if="exportMsg" class="alert alert-info py-2 d-flex justify-content-between align-items-center">
      <span>{{ exportMsg }}</span>
      <button v-if="exportLink" class="btn btn-sm btn-primary" @click="downloadExport">
        <i class="bi bi-download me-1"></i>Download CSV
      </button>
    </div>

    <div v-if="stats" class="row g-3 mb-4">
      <div class="col-6 col-md-3">
        <StatCard label="Total students" :value="stats.total_students" icon="bi-people-fill" color="linear-gradient(135deg,#0d6efd,#0b5ed7)" />
      </div>
      <div class="col-6 col-md-3">
        <StatCard label="Total companies" :value="stats.total_companies" icon="bi-building" color="linear-gradient(135deg,#198754,#146c43)" />
      </div>
      <div class="col-6 col-md-3">
        <StatCard label="Placement drives" :value="stats.total_drives" icon="bi-briefcase-fill" color="linear-gradient(135deg,#fd7e14,#dc6803)" />
      </div>
      <div class="col-6 col-md-3">
        <StatCard label="Students selected" :value="stats.total_selected" icon="bi-trophy-fill" color="linear-gradient(135deg,#6f42c1,#59339d)" />
      </div>
    </div>

    <div v-if="stats" class="row g-3 mb-4">
      <div class="col-md-6">
        <div class="card p-3">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <div class="text-muted small">Pending company approvals</div>
              <h4 class="mb-0">{{ stats.pending_companies }}</h4>
            </div>
            <router-link to="/admin/companies?status=pending" class="btn btn-sm btn-outline-primary">Review</router-link>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card p-3">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <div class="text-muted small">Pending drive approvals</div>
              <h4 class="mb-0">{{ stats.pending_drives }}</h4>
            </div>
            <router-link to="/admin/drives?status=pending" class="btn btn-sm btn-outline-primary">Review</router-link>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-3">
      <div class="col-md-4">
        <router-link to="/admin/companies" class="card p-4 text-decoration-none text-dark h-100">
          <i class="bi bi-building fs-3 text-primary mb-2"></i>
          <h6>Manage companies</h6>
          <p class="small text-muted mb-0">Approve, reject or blacklist company registrations.</p>
        </router-link>
      </div>
      <div class="col-md-4">
        <router-link to="/admin/students" class="card p-4 text-decoration-none text-dark h-100">
          <i class="bi bi-people fs-3 text-primary mb-2"></i>
          <h6>Manage students</h6>
          <p class="small text-muted mb-0">Search students and blacklist if required.</p>
        </router-link>
      </div>
      <div class="col-md-4">
        <router-link to="/admin/reports" class="card p-4 text-decoration-none text-dark h-100">
          <i class="bi bi-graph-up fs-3 text-primary mb-2"></i>
          <h6>Reports &amp; statistics</h6>
          <p class="small text-muted mb-0">Monthly activity report with charts, HTML or PDF.</p>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import StatCard from '@/components/shared/StatCard.vue'
import adminService from '@/services/adminService'
import { downloadFromLink } from '@/services/download'

export default {
  name: 'AdminDashboard',
  components: { StatCard },
  data() {
    return {
      stats: null,
      exporting: false,
      exportMsg: '',
      exportLink: '',
      dismissTimer: null
    }
  },
  async created() {
    const { data } = await adminService.dashboard()
    this.stats = data.stats
  },
  beforeUnmount() {
    if (this.dismissTimer) clearTimeout(this.dismissTimer)
  },
  methods: {
    async exportCsv() {
      this.exporting = true
      this.exportMsg = ''
      this.exportLink = ''
      if (this.dismissTimer) clearTimeout(this.dismissTimer)
      try {
        const { data } = await adminService.exportCsv()
        this.exportMsg = 'Export started — hang on a moment...'
        this.poll(data.task_id)
      } finally {
        this.exporting = false
      }
    },
    poll(taskId, attempt = 0) {
      if (attempt > 15) return
      setTimeout(async () => {
        const { data } = await adminService.exportStatus(taskId)
        if (data.state === 'SUCCESS') {
          this.exportLink = `/api/exports/csv/${data.filename}`
          this.exportMsg = `Export ready: ${data.filename}`
          this.downloadExport()
          if (this.dismissTimer) clearTimeout(this.dismissTimer)
          this.dismissTimer = setTimeout(() => {
            this.exportMsg = ''
            this.exportLink = ''
          }, 10000)
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
        console.error('[AdminDashboard] download failed:', e)
        this.exportMsg = 'Download failed — click "Download CSV" to try again.'
      }
    }
  }
}
</script>
