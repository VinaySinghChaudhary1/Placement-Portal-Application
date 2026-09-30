<template>
  <div class="container py-4">
    <h3 class="mb-3">Summary / Report</h3>
    <div v-if="loading" class="text-center py-5"><span class="spinner-border text-primary"></span></div>
    <div v-else-if="error" class="alert alert-warning d-flex justify-content-between align-items-center">
      <span><i class="bi bi-exclamation-triangle me-1"></i>Couldn't load your report: {{ error }}</span>
      <button class="btn btn-sm btn-outline-dark" @click="load">Retry</button>
    </div>
    <template v-else-if="report">
      <div class="row g-3 mb-3">
        <div class="col-md-6">
          <div class="card p-3">
            <h6>Drives created, by month</h6>
            <ChartCanvas
              type="bar"
              :labels="driveLabels"
              :datasets="[{ label: 'Drives created', data: driveCounts, backgroundColor: '#0d6efd' }]"
              :options="countAxisOptions"
            />
          </div>
        </div>
        <div class="col-md-6">
          <div class="card p-3">
            <h6>Applications received, by month</h6>
            <ChartCanvas
              type="bar"
              :labels="appLabels"
              :datasets="[{ label: 'Applications received', data: appCounts, backgroundColor: '#198754' }]"
              :options="countAxisOptions"
            />
          </div>
        </div>
      </div>
      <div class="row g-3">
        <div class="col-md-6">
          <div class="card p-3">
            <h6>Applications by status</h6>
            <ChartCanvas
              v-if="hasStatusData"
              type="pie"
              :labels="statusLabels"
              :datasets="[{ data: statusValues, backgroundColor: palette }]"
            />
            <p v-else class="text-muted small mb-0">No applications received yet.</p>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card p-3">
            <h6>Top 5 drives by applicants</h6>
            <ChartCanvas
              v-if="topDriveLabels.length"
              type="bar"
              :labels="topDriveLabels"
              :datasets="[{ label: 'Applicants', data: topDriveCounts, backgroundColor: '#fd7e14' }]"
              :options="horizontalCountOptions"
            />
            <p v-else class="text-muted small mb-0">No applications received yet.</p>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import ChartCanvas from '@/components/shared/ChartCanvas.vue'
import companyService from '@/services/companyService'

export default {
  name: 'CompanyReports',
  components: { ChartCanvas },
  data() {
    return {
      report: null,
      loading: false,
      error: '',
      palette: ['#0d6efd', '#fd7e14', '#6f42c1', '#198754', '#dc3545'],
      countAxisOptions: {
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, ticks: { precision: 0 } } }
      },
      horizontalCountOptions: {
        indexAxis: 'y',
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true, ticks: { precision: 0 } } }
      }
    }
  },
  computed: {
    driveLabels() {
      return (this.report?.monthly_drives || []).map((m) => m.label)
    },
    driveCounts() {
      return (this.report?.monthly_drives || []).map((m) => m.count)
    },
    appLabels() {
      return (this.report?.monthly_applications || []).map((m) => m.label)
    },
    appCounts() {
      return (this.report?.monthly_applications || []).map((m) => m.count)
    },
    statusLabels() {
      return Object.keys(this.report?.status_breakdown || {}).map((k) => k.replace(/_/g, ' '))
    },
    statusValues() {
      return Object.values(this.report?.status_breakdown || {})
    },
    hasStatusData() {
      return this.statusValues.length > 0
    },
    topDriveLabels() {
      return (this.report?.top_drives || []).map((d) => d.job_title)
    },
    topDriveCounts() {
      return (this.report?.top_drives || []).map((d) => d.count)
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
        const { data } = await companyService.reports()
        this.report = data
      } catch (e) {
        console.error('[CompanyReports] failed:', e)
        this.error = e?.response?.data?.message || e?.message || String(e)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
