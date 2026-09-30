import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 8080,
    // Polling instead of native filesystem events: on WSL2 with the project
    // living on a Windows drive (/mnt/...), inotify events from edits made
    // outside the WSL VM are unreliable, which can make HMR/dev-server
    // updates silently stale. Polling is slightly heavier but always correct.
    watch: {
      usePolling: true,
      interval: 300
    }
  }
})
