<template>
  <div class="stat-card" :style="{ background: color }">
    <div class="d-flex justify-content-between align-items-start">
      <div>
        <div class="small opacity-75">{{ label }}</div>
        <h3>{{ value }}</h3>
      </div>
      <i :class="['bi', icon, 'fs-2', 'opacity-75']"></i>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatCard',
  props: {
    label: { type: String, required: true },
    value: { type: [Number, String], required: true },
    icon: { type: String, default: 'bi-bar-chart' },
    color: { type: String, default: 'linear-gradient(135deg,#0d6efd,#0b5ed7)' }
  }
}
</script>
