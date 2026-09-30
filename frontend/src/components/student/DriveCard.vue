<template>
  <div class="card drive-card h-100">
    <div class="card-body d-flex flex-column">
      <div class="d-flex justify-content-between align-items-start mb-2">
        <h5 class="card-title mb-0">{{ drive.job_title }}</h5>
        <span v-if="drive.already_applied" class="badge bg-success">Applied</span>
        <span v-else-if="!drive.eligible" class="badge bg-secondary">Not eligible</span>
      </div>
      <h6 class="card-subtitle text-muted mb-2">{{ drive.company_name }}</h6>
      <p class="card-text small text-truncate-3">{{ drive.job_description }}</p>
      <ul class="list-unstyled small text-muted mb-3">
        <li><i class="bi bi-geo-alt me-1"></i>{{ drive.location || 'Location not specified' }}</li>
        <li><i class="bi bi-cash-stack me-1"></i>{{ drive.salary_package ? drive.salary_package + ' LPA' : 'Not disclosed' }}</li>
        <li><i class="bi bi-mortarboard me-1"></i>Min CGPA {{ drive.min_cgpa }}</li>
        <li><i class="bi bi-clock-history me-1"></i>Closes {{ drive.application_deadline }}</li>
      </ul>
      <div v-if="!drive.eligible && drive.ineligible_reason" class="alert alert-warning py-1 px-2 small mb-3">
        {{ drive.ineligible_reason }}
      </div>
      <div class="mt-auto">
        <router-link :to="`/student/drives/${drive.id}`" class="btn btn-outline-primary btn-sm w-100">View details</router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DriveCard',
  props: { drive: { type: Object, required: true } }
}
</script>

<style scoped>
.text-truncate-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
