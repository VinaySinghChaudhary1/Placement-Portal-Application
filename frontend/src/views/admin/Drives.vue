<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
      <h3 class="mb-0">Placement drives</h3>
      <div class="d-flex gap-2">
        <select v-model="statusFilter" class="form-select form-select-sm" @change="load">
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="closed">Closed</option>
        </select>
        <input v-model="search" @keyup.enter="load" class="form-control form-control-sm" placeholder="Search drives…" style="width:220px;">
        <button class="btn btn-sm btn-outline-primary" @click="load"><i class="bi bi-search"></i></button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5"><span class="spinner-border text-primary"></span></div>
    <EmptyState v-else-if="!items.length" message="No drives found." icon="bi-briefcase" />
    <div v-else class="table-responsive">
      <table class="table align-middle bg-white">
        <thead><tr><th>Job title</th><th>Company</th><th>Deadline</th><th>Applicants</th><th>Status</th><th class="text-end">Actions</th></tr></thead>
        <tbody>
          <tr v-for="d in items" :key="d.id">
            <td>{{ d.job_title }}</td>
            <td>{{ d.company_name }}</td>
            <td>{{ d.application_deadline }}</td>
            <td>{{ d.applicant_count }}</td>
            <td><StatusBadge :status="d.status" /></td>
            <td class="text-end">
              <div class="btn-group btn-group-sm" v-if="d.status==='pending'">
                <button class="btn btn-outline-success" @click="approve(d)"><i class="bi bi-check-lg"></i> Approve</button>
                <button class="btn btn-outline-danger" @click="openReject(d)"><i class="bi bi-x-lg"></i> Reject</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <ConfirmModal ref="rejectModal" title="Reject drive" message="Provide a reason for rejecting this drive." confirm-label="Reject" confirm-class="btn-danger" require-reason @confirm="doReject" />
  </div>
</template>

<script>
import adminService from '@/services/adminService'
import StatusBadge from '@/components/shared/StatusBadge.vue'
import EmptyState from '@/components/shared/EmptyState.vue'
import ConfirmModal from '@/components/shared/ConfirmModal.vue'

export default {
  name: 'AdminDrives',
  components: { StatusBadge, EmptyState, ConfirmModal },
  data() { return { items: [], loading: false, search: '', statusFilter: this.$route.query.status || '', rejectTarget: null } },
  created() { this.load() },
  methods: {
    async load() {
      this.loading = true
      try {
        const { data } = await adminService.listDrives({ status: this.statusFilter || undefined, search: this.search || undefined })
        this.items = data.items
      } finally { this.loading = false }
    },
    async approve(d) { await adminService.approveDrive(d.id); this.load() },
    openReject(d) { this.rejectTarget = d; this.$refs.rejectModal.open() },
    async doReject(reason) { await adminService.rejectDrive(this.rejectTarget.id, reason); this.load() }
  }
}
</script>
