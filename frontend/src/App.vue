<template>
  <div id="app-root">
    <Navbar />
    <Sidebar v-if="isLoggedIn" />
    <div class="app-content" :class="{ 'with-sidebar': isLoggedIn && sidebarOpen }">
      <main>
        <router-view />
      </main>
      <Footer />
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex'
import Navbar from '@/components/shared/Navbar.vue'
import Sidebar from '@/components/shared/Sidebar.vue'
import Footer from '@/components/shared/Footer.vue'

export default {
  name: 'App',
  components: { Navbar, Sidebar, Footer },
  computed: {
    ...mapGetters('auth', ['isLoggedIn']),
    ...mapState('ui', ['sidebarOpen'])
  }
}
</script>

<style>
main { min-height: calc(100vh - 56px); }
.app-content { transition: margin-left 0.2s ease; }
@media (min-width: 768px) {
  .app-content.with-sidebar { margin-left: 240px; }
}
</style>
