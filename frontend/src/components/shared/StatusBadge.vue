<template>
  <span class="badge badge-status" :class="cls">{{ (status || '').replace('_', ' ') }}</span>
</template>

<script>
const MAP = {
  pending: 'bg-warning text-dark',
  approved: 'bg-success',
  rejected: 'bg-danger',
  closed: 'bg-secondary',
  applied: 'bg-info text-dark',
  shortlisted: 'bg-primary',
  interview_scheduled: 'bg-purple text-white',
  selected: 'bg-success',
  cleared: 'bg-success',
  not_cleared: 'bg-danger'
}
export default {
  name: 'StatusBadge',
  props: { status: { type: String, default: '' } },
  computed: {
    cls() { return MAP[this.status] || 'bg-secondary' }
  }
}
</script>

<style scoped>
.bg-purple { background-color: #6f42c1; }
</style>
