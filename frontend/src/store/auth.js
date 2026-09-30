// frontend/src/store/auth.js
import authService from '@/services/authService'
import { setAuthToken } from '@/services/api'

export default {
  namespaced: true,
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    token: localStorage.getItem('token') || null,
    ready: false
  }),
  mutations: {
    setSession(state, { user, token }) {
      state.user = user
      state.token = token
      localStorage.setItem('user', JSON.stringify(user))
      localStorage.setItem('token', token)
      setAuthToken(token)
    },
    setUser(state, user) {
      state.user = user
      localStorage.setItem('user', JSON.stringify(user))
    },
    clear(state) {
      state.user = null
      state.token = null
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      setAuthToken(null)
    },
    setReady(state, val) {
      state.ready = val
    }
  },
  actions: {
    async login({ commit }, payload) {
      const { data } = await authService.login(payload)
      commit('setSession', { user: data.user, token: data.token })
      return data.user
    },
    async registerStudent(_, payload) {
      return (await authService.registerStudent(payload)).data
    },
    async registerCompany(_, payload) {
      return (await authService.registerCompany(payload)).data
    },
    async fetchUser({ commit, state }) {
      if (!state.token) { commit('setReady', true); return }
      try {
        const { data } = await authService.getCurrentUser()
        commit('setUser', data.user)
      } catch (e) {
        commit('clear')
      } finally {
        commit('setReady', true)
      }
    },
    async logout({ commit }) {
      try { await authService.logout() } catch (e) { /* ignore */ }
      commit('clear')
    }
  },
  getters: {
    isLoggedIn: (state) => !!state.user && !!state.token,
    role: (state) => state.user?.role || null,
    profile: (state) => state.user?.profile || null,
    displayName: (state) => state.user?.profile?.full_name || state.user?.profile?.company_name || state.user?.username || ''
  }
}
