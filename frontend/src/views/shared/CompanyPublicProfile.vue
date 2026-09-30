<template>
  <div class="container py-4" style="max-width:800px;">
    <div v-if="company" class="card p-4">
      <h3>{{ company.company_name }}</h3>
      <p class="text-muted">{{ company.industry }} &middot; <a :href="company.website" target="_blank" rel="noopener">{{ company.website }}</a></p>
      <p>{{ company.description }}</p>
      <h6 class="mt-4">Open drives</h6>
      <EmptyState v-if="!drives.length" message="No open drives from this company right now." icon="bi-briefcase" />
      <ul class="list-group" v-else>
        <li class="list-group-item d-flex justify-content-between align-items-center" v-for="d in drives" :key="d.id">
          <div>
            <strong>{{ d.job_title }}</strong>
            <div class="small text-muted">{{ d.location }} · {{ d.salary_package }} LPA</div>
          </div>
          <router-link v-if="isStudent" :to="`/student/drives/${d.id}`" class="btn btn-sm btn-outline-primary">View</router-link>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import commonService from '@/services/commonService'
import EmptyState from '@/components/shared/EmptyState.vue'
import { mapGetters } from 'vuex'

export default {
  name: 'CompanyPublicProfile',
  components: { EmptyState },
  props: { id: { type: [String, Number], required: true } },
  data() { return { company: null, drives: [] } },
  computed: { ...mapGetters('auth', ['role']), isStudent() { return this.role === 'student' } },
  async created() {
    const { data } = await commonService.getCompany(this.id)
    this.company = data.company
    this.drives = data.drives
  }
}
</script>
