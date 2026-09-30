<template>
  <aside class="app-sidebar bg-white border-end" :class="{ open: sidebarOpen }">
    <div class="d-flex justify-content-between align-items-center px-3 py-2 border-bottom">
      <span class="small fw-semibold text-muted text-uppercase">Menu</span>
      <button class="btn btn-sm btn-light" title="Close sidebar" @click="closeSidebar">
        <i class="bi bi-x-lg"></i>
      </button>
    </div>
    <ul class="nav flex-column py-2">
      <li class="nav-item" v-for="link in links" :key="link.to">
        <router-link :to="link.to" class="nav-link d-flex align-items-center gap-2 px-3 py-2">
          <i class="bi" :class="link.icon"></i>
          <span>{{ link.label }}</span>
        </router-link>
      </li>
    </ul>
  </aside>
</template>

<script>
import { mapState, mapGetters, mapMutations } from 'vuex'

export default {
  name: 'Sidebar',
  computed: {
    ...mapState('ui', ['sidebarOpen']),
    ...mapGetters('auth', ['role']),
    links() {
      if (this.role === 'admin') {
        return [
          { to: '/admin', label: 'Dashboard', icon: 'bi-speedometer2' },
          { to: '/admin/companies', label: 'Companies', icon: 'bi-building' },
          { to: '/admin/students', label: 'Students', icon: 'bi-people' },
          { to: '/admin/drives', label: 'Drives', icon: 'bi-briefcase' },
          { to: '/admin/applications', label: 'Applications', icon: 'bi-file-earmark-text' },
          { to: '/admin/settings', label: 'Settings', icon: 'bi-gear' },
          { to: '/admin/reports', label: 'Summary / Reports', icon: 'bi-bar-chart-line' }
        ]
      }
      if (this.role === 'company') {
        return [
          { to: '/company', label: 'Dashboard', icon: 'bi-speedometer2' },
          { to: '/company/drives', label: 'My drives', icon: 'bi-briefcase' },
          { to: '/company/drives/new', label: 'Create drive', icon: 'bi-plus-circle' },
          { to: '/company/reports', label: 'Summary / Report', icon: 'bi-bar-chart-line' }
        ]
      }
      if (this.role === 'student') {
        return [
          { to: '/student', label: 'Dashboard', icon: 'bi-speedometer2' },
          { to: '/student/companies', label: 'Company list', icon: 'bi-building' },
          { to: '/student/drives', label: 'Browse drives', icon: 'bi-search' },
          { to: '/student/applications', label: 'My applications', icon: 'bi-file-earmark-text' },
          { to: '/student/reports', label: 'Summary / Report', icon: 'bi-bar-chart-line' }
        ]
      }
      return []
    }
  },
  methods: {
    ...mapMutations('ui', { closeSidebar: 'closeSidebar' })
  }
}
</script>

<style scoped>
.app-sidebar {
  position: fixed;
  top: 56px;
  left: 0;
  bottom: 0;
  width: 240px;
  z-index: 1020;
  overflow-y: auto;
  transform: translateX(-100%);
  transition: transform 0.2s ease;
}
.app-sidebar.open {
  transform: translateX(0);
}
.nav-link {
  color: #495057;
  border-radius: 0.375rem;
  margin: 0 0.5rem;
}
.nav-link.router-link-active {
  background: #e7f1ff;
  color: #0d6efd;
  font-weight: 600;
}
.nav-link:hover {
  background: #f1f3f5;
}
</style>
