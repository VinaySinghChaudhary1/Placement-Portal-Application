// frontend/src/store/index.js
import { createStore } from 'vuex'
import auth from './auth'
import notifications from './notifications'
import ui from './ui'

export default createStore({
  modules: { auth, notifications, ui }
})
