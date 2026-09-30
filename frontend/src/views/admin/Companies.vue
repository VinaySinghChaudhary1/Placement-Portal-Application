<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
      <h3 class="mb-0">Companies</h3>
      <div class="d-flex gap-2">
        <select v-model="statusFilter" class="form-select form-select-sm" @change="load">
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
        </select>
        <input v-model="search" @keyup.enter="load" class="form-control form-control-sm" placeholder="Search companies…" style="width:220px;">
        <button class="btn btn-sm btn-outline-primary" @click="load"><i class="bi bi-search"></i></button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5"><span class="spinner-border text-primary"></span></div>
    <EmptyState v-else-if="!items.length" message="No companies found." icon="bi-building" />
    <div v-else class="table-responsive">
      <table class="table align-middle bg-white">
        <thead>
          <tr><th>Company</th><th>Email</th><th>Status</th><th>Drives</th><th>Flags</th><th class="text-end">Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="c in items" :key="c.id">
            <td>
              <div class="fw-semibold">{{ c.company_name }}</div>
              <div class="small text-muted">{{ c.industry }}</div>
            </td>
            <td>{{ c.email }}</td>
            <td><StatusBadge :status="c.approval_status" /></td>
            <td>{{ c.drive_count }}</td>
            <td>
              <span v-if="c.blacklisted">Blocked</span>
            </td>
            <td class="text-end">
              <div class="btn-group btn-group-sm">
                <button v-if="c.approval_status==='pending'" class="btn btn-outline-success" @click="approve(c)"><i class="bi bi-check-lg"></i></button>
                <button v-if="c.approval_status==='pending'" class="btn btn-outline-danger" @click="openReject(c)"><i class="bi bi-x-lg"></i></button>
                <router-link :to="`/admin/companies/${c.id}/profile`" class="btn btn-outline-secondary" title="View / edit profile">
                  <i class="bi bi-person-vcard"></i>
                </router-link>
                <router-link :to="`/admin/companies/${c.id}/reports`" class="btn btn-outline-primary" title="View report">
                  <i class="bi bi-bar-chart-line"></i>
                </router-link>
                <button v-if="!c.blacklisted" class="btn btn-warning" @click="openBlacklist(c)">
                  <i class="bi bi-shield-x me-1"></i>Block
                </button>
                <button v-else class="btn btn-success" @click="openBlacklist(c)">
                  <i class="bi bi-shield-check me-1"></i>Unblock
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <ConfirmModal ref="rejectModal" title="Reject company" message="Provide a reason for rejecting this registration." confirm-label="Reject" confirm-class="btn-danger" require-reason @confirm="doReject" />
    <ConfirmModal ref="blacklistModal" :title="blacklistTarget && blacklistTarget.blacklisted ? 'Unblock company' : 'Block company'" :message="blacklistTarget && blacklistTarget.blacklisted ? 'This will restore the company\'s ability to post drives.' : 'Blocked companies cannot post or manage drives. Provide a reason.'" :confirm-label="blacklistTarget && blacklistTarget.blacklisted ? 'Unblock' : 'Block'" :confirm-class="blacklistTarget && blacklistTarget.blacklisted ? 'btn-success' : 'btn-warning'" :require-reason="!(blacklistTarget && blacklistTarget.blacklisted)" @confirm="doBlacklist" />
  </div>
</template>

<script>
import adminService from '@/services/adminService'
import StatusBadge from '@/components/shared/StatusBadge.vue'
import EmptyState from '@/components/shared/EmptyState.vue'
import ConfirmModal from '@/components/shared/ConfirmModal.vue'

export default {
  name: 'AdminCompanies',
  components: { StatusBadge, EmptyState, ConfirmModal },
  data() {
    return { items: [], loading: false, search: '', statusFilter: this.$route.query.status || '', rejectTarget: null, blacklistTarget: null }
  },
  created() { this.load() },
  methods: {
    async load() {
      this.loading = true
      try {
        const { data } = await adminService.listCompanies({ status: this.statusFilter || undefined, search: this.search || undefined })
        this.items = data.items
      } finally { this.loading = false }
    },
    async approve(c) {
      await adminService.approveCompany(c.id)
      this.load()
    },
    openReject(c) { this.rejectTarget = c; this.$refs.rejectModal.open() },
    async doReject(reason) {
      await adminService.rejectCompany(this.rejectTarget.id, reason)
      this.load()
    },
    openBlacklist(c) { this.blacklistTarget = c; this.$refs.blacklistModal.open() },
    async doBlacklist(reason) {
      await adminService.blacklistCompany(this.blacklistTarget.id, !this.blacklistTarget.blacklisted, reason)
      this.load()
    }
  }
}
</script>
