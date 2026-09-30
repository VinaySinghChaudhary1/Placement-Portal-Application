// frontend/src/store/ui.js
// Sidebar open/closed state. Deliberately NOT auto-closed on route change or
// outside click — only the explicit close button (or the navbar toggle) changes it.
export default {
  namespaced: true,
  state: () => ({
    sidebarOpen: true
  }),
  mutations: {
    openSidebar(state) { state.sidebarOpen = true },
    closeSidebar(state) { state.sidebarOpen = false },
    toggleSidebar(state) { state.sidebarOpen = !state.sidebarOpen }
  }
}
