// frontend/src/store/notifications.js
import commonService from '@/services/commonService'

export default {
  namespaced: true,
  state: () => ({
    items: [],
    unreadCount: 0
  }),
  mutations: {
    setNotifications(state, { items, unread_count }) {
      state.items = items
      state.unreadCount = unread_count
    },
    markReadLocal(state, id) {
      const n = state.items.find((i) => i.id === id)
      if (n && !n.is_read) {
        n.is_read = true
        state.unreadCount = Math.max(0, state.unreadCount - 1)
      }
    },
    markAllReadLocal(state) {
      state.items.forEach((i) => { i.is_read = true })
      state.unreadCount = 0
    }
  },
  actions: {
    async fetch({ commit }) {
      const { data } = await commonService.notifications()
      commit('setNotifications', data)
    },
    async markRead({ commit }, id) {
      await commonService.markNotificationRead(id)
      commit('markReadLocal', id)
    },
    async markAllRead({ commit }) {
      await commonService.markAllNotificationsRead()
      commit('markAllReadLocal')
    }
  }
}
