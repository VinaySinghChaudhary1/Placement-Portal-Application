<template>
  <div class="container py-4">
    <h3 class="mb-3">My applications &amp; placement history</h3>
    <div v-if="loading" class="text-center py-5"><span class="spinner-border text-primary"></span></div>
    <EmptyState v-else-if="!items.length" message="You haven't applied to any drives yet." icon="bi-file-earmark-text" />
    <div v-else class="table-responsive">
      <table class="table align-middle bg-white">
        <thead><tr><th>Job title</th><th>Company</th><th>Applied on</th><th>Status</th><th></th></tr></thead>
        <tbody>
          <tr v-for="a in items" :key="a.id">
            <td>{{ a.drive.job_title }}</td>
            <td>{{ a.drive.company_name }}</td>
            <td>{{ a.applied_at }}</td>
            <td><StatusBadge :status="a.status" /></td>
            <td class="text-end">
              <router-link :to="`/student/applications/${a.id}`" class="btn btn-sm btn-outline-primary">Details</router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import studentService from '@/services/studentService'
import StatusBadge from '@/components/shared/StatusBadge.vue'
import EmptyState from '@/components/shared/EmptyState.vue'

export default {
  name: 'StudentApplications',
  components: { StatusBadge, EmptyState },
  data() { return { items: [], loading: false } },
  async created() {
    this.loading = true
    try {
      const { data } = await studentService.myApplications()
      this.items = data.items
    } finally { this.loading = false }
  }
}
</script>
