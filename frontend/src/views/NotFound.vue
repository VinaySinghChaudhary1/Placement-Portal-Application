<template>
  <div class="text-center py-5">
    <h1 class="display-3 fw-bold text-primary">404</h1>
    <p class="text-muted">The page you're looking for doesn't exist.</p>
    <router-link to="/home" class="btn btn-primary">Go home</router-link>
  </div>
</template>
<script>
export default { name: 'NotFound' }
</script>
