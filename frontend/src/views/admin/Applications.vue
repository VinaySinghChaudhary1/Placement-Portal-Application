<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
      <h3 class="mb-0">All applications</h3>
      <select v-model="statusFilter" class="form-select form-select-sm" style="width:200px;" @change="load">
        <option value="">All statuses</option>
        <option value="applied">Applied</option>
        <option value="shortlisted">Shortlisted</option>
        <option value="interview_scheduled">Interview scheduled</option>
        <option value="selected">Selected</option>
        <option value="rejected">Rejected</option>
      </select>
    </div>
    <div v-if="loading" class="text-center py-5"><span class="spinner-border text-primary"></span></div>
    <EmptyState v-else-if="!items.length" message="No applications found." icon="bi-file-earmark-text" />
    <div v-else class="table-responsive">
      <table class="table align-middle bg-white">
        <thead><tr><th>Student</th><th>Drive</th><th>Company</th><th>Applied on</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="a in items" :key="a.id">
            <td>{{ a.student.full_name }} <span class="text-muted small">({{ a.student.branch }})</span></td>
            <td>{{ a.drive.job_title }}</td>
            <td>{{ a.drive.company_name }}</td>
            <td>{{ a.applied_at }}</td>
            <td><StatusBadge :status="a.status" /></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import adminService from '@/services/adminService'
import StatusBadge from '@/components/shared/StatusBadge.vue'
import EmptyState from '@/components/shared/EmptyState.vue'

export default {
  name: 'AdminApplications',
  components: { StatusBadge, EmptyState },
  data() { return { items: [], loading: false, statusFilter: '' } },
  created() { this.load() },
  methods: {
    async load() {
      this.loading = true
      try {
        const { data } = await adminService.listApplications({ status: this.statusFilter || undefined })
        this.items = data.items
      } finally { this.loading = false }
    }
  }
}
</script>
