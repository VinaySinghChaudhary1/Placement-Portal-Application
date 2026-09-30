<template>
  <div class="chart-box">
    <canvas ref="canvas"></canvas>
    <div v-if="error" class="small text-danger mt-1">Chart error: {{ error }}</div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto'

/*
 * Reusable Chart.js wrapper.
 *
 * Three things here are deliberate and easy to regress:
 *
 * 1. The Chart.js instance is stored on a NON-REACTIVE property (assigned in
 *    created(), never declared in data()). Putting it in data() makes Vue wrap
 *    it in a deep reactive Proxy; Chart.js compares internal object identities
 *    (ctx, scales, dataset metadata) and misbehaves when it gets proxies back
 *    instead of the raw objects it stored — typically rendering nothing at all.
 *
 * 2. Callers pass inline literals like :datasets="[{ ... }]", which produce a
 *    brand-new array on every parent re-render. Watching those directly would
 *    destroy and rebuild the chart constantly. Instead we watch `renderKey`, a
 *    serialised snapshot, so we only rebuild when the values actually change.
 *
 * 3. Before creating a chart we explicitly adopt-and-destroy any instance
 *    already attached to this canvas (Chart.getChart). Chart.js throws
 *    "Canvas is already in use" if a stale instance is still bound, which would
 *    otherwise surface as a silently blank box.
 */
export default {
  name: 'ChartCanvas',
  props: {
    type: { type: String, required: true },
    labels: { type: Array, default: () => [] },
    datasets: { type: Array, default: () => [] },
    options: { type: Object, default: () => ({}) }
  },
  data() {
    return { error: '' }
  },
  computed: {
    renderKey() {
      try {
        return JSON.stringify([this.type, this.labels, this.datasets, this.options])
      } catch {
        // Circular/non-serialisable payload: fall back to always redrawing.
        return String(Date.now())
      }
    }
  },
  created() {
    // Intentionally not in data() — see note 1 above.
    this.chart = null
  },
  mounted() {
    this.sync()
  },
  beforeUnmount() {
    this.destroyChart()
  },
  watch: {
    renderKey() {
      this.sync()
    }
  },
  methods: {
    destroyChart() {
      if (this.chart) {
        this.chart.destroy()
        this.chart = null
      }
    },
    sync() {
      this.error = ''
      try {
        this.destroyChart()

        const el = this.$refs.canvas
        if (!el) return

        // Adopt any orphaned instance still bound to this canvas.
        const existing = Chart.getChart(el)
        if (existing) existing.destroy()

        this.chart = new Chart(el, {
          type: this.type,
          data: {
            labels: this.labels,
            // Clone so Chart.js owns plain arrays rather than Vue proxies.
            datasets: this.datasets.map((d) => ({ ...d, data: [...(d.data || [])] }))
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            ...this.options
          }
        })
      } catch (e) {
        console.error('[ChartCanvas] render failed:', e)
        this.error = e?.message || String(e)
      }
    }
  }
}
</script>
