<template>
  <div class="container py-4" style="max-width:700px;">
    <router-link to="/student/applications" class="small text-decoration-none"><i class="bi bi-arrow-left me-1"></i>Back</router-link>
    <div v-if="application" class="card p-4 mt-2">
      <div class="d-flex justify-content-between align-items-start">
        <div>
          <h4>{{ application.drive.job_title }}</h4>
          <h6 class="text-muted">{{ application.company_name }}</h6>
        </div>
        <StatusBadge :status="application.status" />
      </div>
      <p class="small text-muted">Applied on {{ application.applied_at }} · Last updated {{ application.updated_at }}</p>

      <h6 class="mt-3">Interview rounds</h6>
      <EmptyState v-if="!application.interviews.length" message="No interviews scheduled yet." icon="bi-calendar" />
      <ul class="list-group" v-else>
        <li class="list-group-item" v-for="i in application.interviews" :key="i.id">
          <div class="d-flex justify-content-between">
            <strong>{{ i.round_name }}</strong>
            <StatusBadge :status="i.result" />
          </div>
          <div class="small text-muted">{{ i.scheduled_at }} · {{ i.mode }}</div>
          <div class="small" v-if="i.location_or_link">{{ i.location_or_link }}</div>
          <div class="small text-muted" v-if="i.remarks">{{ i.remarks }}</div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import studentService from '@/services/studentService'
import StatusBadge from '@/components/shared/StatusBadge.vue'
import EmptyState from '@/components/shared/EmptyState.vue'

export default {
  name: 'StudentApplicationDetail',
  components: { StatusBadge, EmptyState },
  props: { id: { type: [String, Number], required: true } },
  data() { return { application: null } },
  async created() {
    const { data } = await studentService.applicationDetail(this.id)
    this.application = data.application
  }
}
</script>
