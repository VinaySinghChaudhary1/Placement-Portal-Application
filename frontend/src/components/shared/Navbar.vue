<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom sticky-top">
    <div class="container">
      <button v-if="isLoggedIn" class="btn btn-light me-2" title="Toggle sidebar" @click="toggleSidebar">
        <i class="bi bi-list fs-5"></i>
      </button>
      <router-link class="navbar-brand fw-bold" :to="homeLink">
        <i class="bi bi-mortarboard-fill me-2"></i>Placement Portal
      </router-link>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#nav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="nav">
        <ul class="navbar-nav ms-auto align-items-lg-center" v-if="isLoggedIn">
          <li class="nav-item dropdown me-2">
            <a class="nav-link position-relative" href="#" role="button" data-bs-toggle="dropdown" @click="loadNotifications">
              <i class="bi bi-bell fs-5"></i>
              <span v-if="unreadCount" class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" style="font-size:0.6rem;">
                {{ unreadCount }}
              </span>
            </a>
            <ul class="dropdown-menu dropdown-menu-end p-2" style="width:340px; max-height:400px; overflow:auto;">
              <li v-if="!notifications.length" class="text-center text-muted py-3 small">No notifications yet</li>
              <li v-for="n in notifications" :key="n.id" class="mb-1">
                <div class="p-2 rounded" :class="n.is_read ? '' : 'bg-light'" @click="handleNotificationClick(n)" role="button">
                  <div class="fw-semibold small">
                    {{ n.title }}
                    <i v-if="n.link" class="bi bi-download ms-1 text-primary" title="Click to download"></i>
                  </div>
                  <div class="small text-muted">{{ n.message }}</div>
                  <div v-if="downloadError === n.id" class="small text-danger">Download failed — try again.</div>
                  <div class="small text-muted">{{ n.created_at }}</div>
                </div>
              </li>
              <li v-if="notifications.length"><hr class="dropdown-divider"></li>
              <li v-if="notifications.length">
                <button class="btn btn-sm btn-link w-100" @click="markAll">Mark all as read</button>
              </li>
            </ul>
          </li>
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
              <i class="bi bi-person-circle me-1"></i>{{ displayName }}
              <span class="badge bg-secondary-subtle text-secondary text-capitalize ms-1">{{ role }}</span>
            </a>
            <ul class="dropdown-menu dropdown-menu-end">
              <li v-if="profileLink"><router-link class="dropdown-item" :to="profileLink"><i class="bi bi-person me-2"></i>My profile</router-link></li>
              <li><hr class="dropdown-divider"></li>
              <li><a class="dropdown-item text-danger" href="#" @click.prevent="logout"><i class="bi bi-box-arrow-right me-2"></i>Logout</a></li>
            </ul>
          </li>
        </ul>
        <ul class="navbar-nav ms-auto" v-else>
          <li class="nav-item"><router-link class="nav-link" to="/login">Login</router-link></li>
          <li class="nav-item"><router-link class="btn btn-primary btn-sm ms-2" to="/register/student">Get started</router-link></li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import { mapState, mapGetters } from 'vuex'
import { downloadFromLink } from '@/services/download'

export default {
  name: 'Navbar',
  data() {
    return { downloadError: null }
  },
  computed: {
    ...mapGetters('auth', ['isLoggedIn', 'role', 'displayName']),
    ...mapState('notifications', { notifications: 'items', unreadCount: 'unreadCount' }),
    homeLink() {
      // The brand/logo always goes to the public homepage — the "Dashboard" link
      // in the nav (see `links` below) is what takes a logged-in user to their dashboard.
      return '/home'
    },
    profileLink() {
      if (this.role === 'company') return '/company/profile'
      if (this.role === 'student') return '/student/profile'
      return null
    }
  },
  methods: {
    toggleSidebar() {
      this.$store.commit('ui/toggleSidebar')
    },
    loadNotifications() {
      this.$store.dispatch('notifications/fetch').catch(() => {})
    },
    markRead(n) {
      if (!n.is_read) this.$store.dispatch('notifications/markRead', n.id).catch(() => {})
    },
    async handleNotificationClick(n) {
      this.markRead(n)
      if (!n.link) return
      this.downloadError = null
      try {
        await downloadFromLink(n.link)
      } catch (e) {
        console.error('[Navbar] download failed:', e)
        this.downloadError = n.id
      }
    },
    markAll() {
      this.$store.dispatch('notifications/markAllRead').catch(() => {})
    },
    async logout() {
      await this.$store.dispatch('auth/logout')
      this.$router.push('/login')
    }
  }
}
</script>
