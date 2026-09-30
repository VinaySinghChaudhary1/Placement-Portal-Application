<template>
  <footer class="border-top bg-white py-3 mt-5">
    <div class="container d-flex flex-wrap justify-content-between small text-muted">
      <span>&copy; {{ year }} Placement Portal — Institute Placement Cell</span>
      <span>Built with Flask, VueJS &amp; Bootstrap</span>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'Footer',
  computed: { year() { return new Date().getFullYear() } }
}
</script>
