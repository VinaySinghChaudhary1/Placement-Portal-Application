<template>
  <div class="container py-4">
    <div v-if="data">
      <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
        <div>
          <h3 class="mb-0">Welcome, {{ data.profile.company_name }}</h3>
          <StatusBadge :status="data.profile.approval_status" />
          <span v-if="data.profile.blacklisted" class="badge bg-danger ms-1">Blacklisted</span>
        </div>
        <div class="d-flex gap-2">
          <button class="btn btn-outline-primary" @click="exportCsv" :disabled="exporting">
            <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="bi bi-download me-1"></i>Export report (CSV)
          </button>
          <router-link to="/company/drives/new" class="btn btn-primary" :class="{ disabled: data.profile.approval_status !== 'approved' || data.profile.blacklisted }">
            <i class="bi bi-plus-lg me-1"></i>Create drive
          </router-link>
        </div>
      </div>

      <div v-if="exportMsg" class="alert alert-info py-2 d-flex justify-content-between align-items-center">
        <span>{{ exportMsg }}</span>
        <button v-if="exportLink" class="btn btn-sm btn-primary" @click="downloadExport">
          <i class="bi bi-download me-1"></i>Download CSV
        </button>
      </div>

      <div v-if="data.profile.approval_status === 'pending'" class="alert alert-warning">
        Your company registration is pending admin approval. You'll be able to create drives once approved.
      </div>
      <div v-else-if="data.profile.approval_status === 'rejected'" class="alert alert-danger">
        Your company registration was rejected: {{ data.profile.rejection_reason }}
      </div>

      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3"><StatCard label="Total drives" :value="data.stats.total_drives" icon="bi-briefcase" /></div>
        <div class="col-6 col-md-3"><StatCard label="Approved" :value="data.stats.approved_drives" icon="bi-check-circle" color="linear-gradient(135deg,#198754,#146c43)" /></div>
        <div class="col-6 col-md-3"><StatCard label="Pending" :value="data.stats.pending_drives" icon="bi-hourglass-split" color="linear-gradient(135deg,#fd7e14,#dc6803)" /></div>
        <div class="col-6 col-md-3"><StatCard label="Total applicants" :value="data.stats.total_applicants" icon="bi-people" color="linear-gradient(135deg,#6f42c1,#59339d)" /></div>
      </div>

      <h5>Your drives</h5>
      <EmptyState v-if="!data.drives.length" message="No drives yet — create your first one." icon="bi-briefcase" />
      <div v-else class="table-responsive">
        <table class="table align-middle bg-white">
          <thead><tr><th>Job title</th><th>Deadline</th><th>Applicants</th><th>Status</th><th class="text-end">Actions</th></tr></thead>
          <tbody>
            <tr v-for="d in data.drives" :key="d.id">
              <td>{{ d.job_title }}</td>
              <td>{{ d.application_deadline }}</td>
              <td>{{ d.applicant_count }}</td>
              <td><StatusBadge :status="d.status" /></td>
              <td class="text-end">
                <router-link :to="`/company/drives/${d.id}/applications`" class="btn btn-sm btn-outline-primary">Applicants</router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import companyService from '@/services/companyService'
import StatCard from '@/components/shared/StatCard.vue'
import StatusBadge from '@/components/shared/StatusBadge.vue'
import EmptyState from '@/components/shared/EmptyState.vue'
import { downloadFromLink } from '@/services/download'

export default {
  name: 'CompanyDashboard',
  components: { StatCard, StatusBadge, EmptyState },
  data() { return { data: null, exporting: false, exportMsg: '', exportLink: '', dismissTimer: null } },
  async created() {
    const { data } = await companyService.dashboard()
    this.data = data
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
        const { data } = await companyService.exportCsv()
        this.exportMsg = 'Export started — hang on a moment...'
        this.poll(data.task_id)
      } finally {
        this.exporting = false
      }
    },
    poll(taskId, attempt = 0) {
      if (attempt > 15) return
      setTimeout(async () => {
        const { data } = await companyService.exportStatus(taskId)
        if (data.state === 'SUCCESS') {
          this.exportLink = `/api/exports/csv/${data.filename}`
          this.exportMsg = `Export ready: ${data.filename}`
          this.downloadExport()
          // Auto-dismiss the banner so it doesn't linger until the next manual refresh.
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
        console.error('[CompanyDashboard] download failed:', e)
        this.exportMsg = 'Download failed — click "Download CSV" to try again.'
      }
    }
  }
}
</script>
