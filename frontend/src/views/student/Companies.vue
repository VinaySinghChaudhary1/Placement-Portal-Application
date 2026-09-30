<template>
  <div class="container py-4">
    <h3 class="mb-3">Companies</h3>
    <div v-if="loading" class="text-center py-5"><span class="spinner-border text-primary"></span></div>
    <EmptyState v-else-if="!items.length" message="No approved companies yet." icon="bi-building" />
    <div v-else class="row g-3">
      <div class="col-md-6 col-lg-4" v-for="c in items" :key="c.id">
        <router-link :to="`/companies/${c.id}`" class="card p-3 h-100 text-decoration-none text-dark">
          <div class="d-flex align-items-center gap-2 mb-2">
            <i class="bi bi-building fs-3 text-primary"></i>
            <div>
              <div class="fw-semibold">{{ c.company_name }}</div>
              <div class="small text-muted">{{ c.industry || 'Industry not specified' }}</div>
            </div>
          </div>
          <p class="small text-muted mb-2">{{ c.description || 'No description provided.' }}</p>
          <span class="badge bg-success-subtle text-success">{{ c.open_drive_count }} open drive{{ c.open_drive_count === 1 ? '' : 's' }}</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import commonService from '@/services/commonService'
import EmptyState from '@/components/shared/EmptyState.vue'

export default {
  name: 'StudentCompanies',
  components: { EmptyState },
  data() { return { items: [], loading: false } },
  async created() {
    this.loading = true
    try {
      const { data } = await commonService.listCompanies()
      this.items = data.items
    } finally { this.loading = false }
  }
}
</script>
