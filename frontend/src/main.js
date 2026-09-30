// frontend/src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'bootstrap'
import './assets/styles/global.css'
import './assets/styles/motion.css'
import revealDirective from './directives/reveal'

const token = localStorage.getItem('token')
if (token) {
  store.dispatch('auth/fetchUser')
}

const app = createApp(App)
app.use(store)
app.use(router)
app.directive('reveal', revealDirective)
app.mount('#app')
