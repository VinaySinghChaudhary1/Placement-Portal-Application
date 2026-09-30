<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3 class="mb-0">{{ data ? data.student.full_name : 'Student' }} — Report</h3>
      <router-link :to="`/admin/students/${id}/profile`" class="btn btn-outline-secondary btn-sm">
        <i class="bi bi-person-vcard me-1"></i>View profile
      </router-link>
    </div>

    <div v-if="loading" class="text-center py-5"><span class="spinner-border text-primary"></span></div>
    <div v-else-if="error" class="alert alert-warning d-flex justify-content-between align-items-center">
      <span><i class="bi bi-exclamation-triangle me-1"></i>Couldn't load this student's report: {{ error }}</span>
      <button class="btn btn-sm btn-outline-dark" @click="load">Retry</button>
    </div>
    <template v-else-if="data">
      <div class="row g-3">
        <div class="col-md-7">
          <div class="card p-3">
            <h6>Applications submitted, by month</h6>
            <ChartCanvas
              type="line"
              :labels="monthLabels"
              :datasets="[{
                label: 'Applications',
                data: monthCounts,
                borderColor: '#0d6efd',
                backgroundColor: 'rgba(13,110,253,0.15)',
                tension: 0.3,
                fill: true
              }]"
              :options="countAxisOptions"
            />
          </div>
        </div>
        <div class="col-md-5">
          <div class="card p-3">
            <h6>Applications by status</h6>
            <ChartCanvas
              v-if="hasStatusData"
              type="pie"
              :labels="statusLabels"
              :datasets="[{ data: statusValues, backgroundColor: palette }]"
            />
            <p v-else class="text-muted small mb-0">This student hasn't applied to any drives yet.</p>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import ChartCanvas from '@/components/shared/ChartCanvas.vue'
import adminService from '@/services/adminService'

export default {
  name: 'AdminStudentReport',
  components: { ChartCanvas },
  props: { id: { type: [String, Number], required: true } },
  data() {
    return {
      data: null,
      loading: false,
      error: '',
      palette: ['#0d6efd', '#fd7e14', '#6f42c1', '#198754', '#dc3545'],
      countAxisOptions: {
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, ticks: { precision: 0 } } }
      }
    }
  },
  computed: {
    monthLabels() {
      return (this.data?.monthly_applications || []).map((m) => m.label)
    },
    monthCounts() {
      return (this.data?.monthly_applications || []).map((m) => m.count)
    },
    statusLabels() {
      return Object.keys(this.data?.status_breakdown || {}).map((k) => k.replace(/_/g, ' '))
    },
    statusValues() {
      return Object.values(this.data?.status_breakdown || {})
    },
    hasStatusData() {
      return this.statusValues.length > 0
    }
  },
  created() {
    this.load()
  },
  methods: {
    async load() {
      this.loading = true
      this.error = ''
      try {
        const { data } = await adminService.studentReports(this.id)
        this.data = data
      } catch (e) {
        console.error('[AdminStudentReport] failed:', e)
        this.error = e?.response?.data?.message || e?.message || String(e)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
