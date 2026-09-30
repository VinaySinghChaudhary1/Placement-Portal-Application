<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
      <h3 class="mb-0">My drives</h3>
      <div class="d-flex gap-2">
        <select v-model="statusFilter" class="form-select form-select-sm" @change="load">
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="closed">Closed</option>
        </select>
        <router-link to="/company/drives/new" class="btn btn-sm btn-primary"><i class="bi bi-plus-lg me-1"></i>Create drive</router-link>
      </div>
    </div>
    <div v-if="loading" class="text-center py-5"><span class="spinner-border text-primary"></span></div>
    <EmptyState v-else-if="!items.length" message="No drives yet." icon="bi-briefcase" />
    <div v-else class="table-responsive">
      <table class="table align-middle bg-white">
        <thead><tr><th>Job title</th><th>Deadline</th><th>Package</th><th>Applicants</th><th>Status</th><th class="text-end">Actions</th></tr></thead>
        <tbody>
          <tr v-for="d in items" :key="d.id">
            <td>{{ d.job_title }}</td>
            <td>{{ d.application_deadline }}</td>
            <td>{{ d.salary_package ? d.salary_package + ' LPA' : '—' }}</td>
            <td>{{ d.applicant_count }}</td>
            <td>
              <StatusBadge :status="d.status" />
              <div v-if="d.status==='rejected'" class="small text-danger mt-1">{{ d.rejection_reason }}</div>
            </td>
            <td class="text-end">
              <div class="btn-group btn-group-sm">
                <router-link :to="`/company/drives/${d.id}/applications`" class="btn btn-outline-primary">Applicants</router-link>
                <router-link v-if="d.status!=='closed'" :to="`/company/drives/${d.id}/edit`" class="btn btn-outline-secondary"><i class="bi bi-pencil"></i></router-link>
                <button v-if="d.status==='approved'" class="btn btn-outline-dark" @click="close(d)"><i class="bi bi-check2-circle"></i> Close</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import companyService from '@/services/companyService'
import StatusBadge from '@/components/shared/StatusBadge.vue'
import EmptyState from '@/components/shared/EmptyState.vue'

export default {
  name: 'CompanyDrives',
  components: { StatusBadge, EmptyState },
  data() { return { items: [], loading: false, statusFilter: '' } },
  created() { this.load() },
  methods: {
    async load() {
      this.loading = true
      try {
        const { data } = await companyService.listDrives({ status: this.statusFilter || undefined })
        this.items = data.items
      } finally { this.loading = false }
    },
    async close(d) {
      await companyService.closeDrive(d.id)
      this.load()
    }
  }
}
</script>
