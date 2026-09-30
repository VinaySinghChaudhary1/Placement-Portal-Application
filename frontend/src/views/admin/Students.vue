<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
      <h3 class="mb-0">Students</h3>
      <div class="d-flex gap-2">
        <input v-model="search" @keyup.enter="load" class="form-control form-control-sm" placeholder="Search by name or email…" style="width:260px;">
        <button class="btn btn-sm btn-outline-primary" @click="load"><i class="bi bi-search"></i></button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5"><span class="spinner-border text-primary"></span></div>
    <EmptyState v-else-if="!items.length" message="No students found." icon="bi-people" />
    <div v-else class="table-responsive">
      <table class="table align-middle bg-white">
        <thead><tr><th>Name</th><th>Email</th><th>Branch</th><th>Year</th><th>CGPA</th><th>Flags</th><th class="text-end">Actions</th></tr></thead>
        <tbody>
          <tr v-for="s in items" :key="s.id">
            <td>{{ s.full_name }}</td>
            <td>{{ s.email }}</td>
            <td>{{ s.branch }}</td>
            <td>{{ s.year }}</td>
            <td>{{ s.cgpa }}</td>
            <td>
              <span v-if="s.blacklisted">Blocked</span>
            </td>
            <td class="text-end">
              <div class="btn-group btn-group-sm">
                <router-link :to="`/admin/students/${s.id}/profile`" class="btn btn-outline-secondary" title="View / edit profile">
                  <i class="bi bi-person-vcard"></i>
                </router-link>
                <router-link :to="`/admin/students/${s.id}/reports`" class="btn btn-outline-primary" title="View report">
                  <i class="bi bi-bar-chart-line"></i>
                </router-link>
                <button v-if="!s.blacklisted" class="btn btn-warning" @click="openBlacklist(s)">
                  <i class="bi bi-shield-x me-1"></i>Block
                </button>
                <button v-else class="btn btn-success" @click="openBlacklist(s)">
                  <i class="bi bi-shield-check me-1"></i>Unblock
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <ConfirmModal ref="blacklistModal" :title="blacklistTarget && blacklistTarget.blacklisted ? 'Unblock student' : 'Block student'" :message="blacklistTarget && blacklistTarget.blacklisted ? 'This will restore the student\'s ability to apply to drives.' : 'Blocked students cannot apply to any drive. Provide a reason.'" :confirm-label="blacklistTarget && blacklistTarget.blacklisted ? 'Unblock' : 'Block'" :confirm-class="blacklistTarget && blacklistTarget.blacklisted ? 'btn-success' : 'btn-warning'" :require-reason="!(blacklistTarget && blacklistTarget.blacklisted)" @confirm="doBlacklist" />
  </div>
</template>

<script>
import adminService from '@/services/adminService'
import EmptyState from '@/components/shared/EmptyState.vue'
import ConfirmModal from '@/components/shared/ConfirmModal.vue'

export default {
  name: 'AdminStudents',
  components: { EmptyState, ConfirmModal },
  data() { return { items: [], loading: false, search: '', blacklistTarget: null } },
  created() { this.load() },
  methods: {
    async load() {
      this.loading = true
      try {
        const { data } = await adminService.listStudents({ search: this.search || undefined })
        this.items = data.items
      } finally { this.loading = false }
    },
    openBlacklist(s) { this.blacklistTarget = s; this.$refs.blacklistModal.open() },
    async doBlacklist(reason) {
      await adminService.blacklistStudent(this.blacklistTarget.id, !this.blacklistTarget.blacklisted, reason)
      this.load()
    }
  }
}
</script>
