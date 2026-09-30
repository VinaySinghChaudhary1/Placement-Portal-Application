<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
      <h3 class="mb-0">Placement drives</h3>
      <div class="d-flex gap-2 flex-wrap">
        <input v-model="search" @keyup.enter="load" class="form-control form-control-sm" placeholder="Search by title or company…" style="width:220px;">
        <div class="form-check form-switch d-flex align-items-center">
          <input class="form-check-input me-2" type="checkbox" id="eligibleOnly" v-model="eligibleOnly" @change="load">
          <label class="form-check-label small" for="eligibleOnly">Eligible only</label>
        </div>
        <button class="btn btn-sm btn-outline-primary" @click="load"><i class="bi bi-search"></i></button>
      </div>
    </div>
    <div v-if="loading" class="text-center py-5"><span class="spinner-border text-primary"></span></div>
    <EmptyState v-else-if="!items.length" message="No drives match your filters." icon="bi-briefcase" />
    <div v-else class="row g-3">
      <div class="col-md-6 col-lg-4" v-for="d in items" :key="d.id">
        <DriveCard :drive="d" />
      </div>
    </div>
  </div>
</template>

<script>
import studentService from '@/services/studentService'
import DriveCard from '@/components/student/DriveCard.vue'
import EmptyState from '@/components/shared/EmptyState.vue'

export default {
  name: 'StudentDrives',
  components: { DriveCard, EmptyState },
  data() { return { items: [], loading: false, search: '', eligibleOnly: false } },
  created() { this.load() },
  methods: {
    async load() {
      this.loading = true
      try {
        const { data } = await studentService.browseDrives({ search: this.search || undefined, eligible_only: this.eligibleOnly })
        this.items = data.items
      } finally { this.loading = false }
    }
  }
}
</script>
