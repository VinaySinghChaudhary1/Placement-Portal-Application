<template>
  <div class="text-center text-muted py-5">
    <i :class="['bi', icon, 'display-4 d-block mb-2 opacity-50']"></i>
    <p class="mb-0">{{ message }}</p>
  </div>
</template>

<script>
export default {
  name: 'EmptyState',
  props: {
    message: { type: String, default: 'Nothing here yet.' },
    icon: { type: String, default: 'bi-inbox' }
  }
}
</script>
