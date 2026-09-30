<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
      <h3 class="mb-0">Monthly activity report</h3>
      <div class="d-flex gap-2">
        <input type="month" v-model="monthInput" class="form-control form-control-sm" @change="load()">
        <button class="btn btn-sm btn-outline-primary" @click="triggerMonthly" :disabled="triggering">
          <span v-if="triggering" class="spinner-border spinner-border-sm me-1"></span>Email this report now
        </button>
        <button class="btn btn-sm btn-outline-secondary" @click="triggerReminders" :disabled="triggeringReminders">
          Trigger deadline reminders
        </button>
      </div>
    </div>
    <div v-if="toast" class="alert alert-success py-2">{{ toast }}</div>

    <div v-if="loading" class="text-center py-5"><span class="spinner-border text-primary"></span></div>
    <div v-else-if="reportError" class="alert alert-warning d-flex justify-content-between align-items-center">
      <span><i class="bi bi-exclamation-triangle me-1"></i>Couldn't load the monthly report: {{ reportError }}</span>
      <button class="btn btn-sm btn-outline-dark" @click="load()">Retry</button>
    </div>
    <template v-else-if="report">
      <div v-if="!report.is_current_month" class="alert alert-info py-2 small">
        <i class="bi bi-info-circle me-1"></i>
        No portal activity recorded yet for {{ currentMonthLabel }}. Showing
        <strong>{{ report.period }}</strong> — the most recent month with activity.
        Use the month picker above to view any other month.
      </div>
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3"><StatCard label="Drives conducted" :value="report.drives_conducted" icon="bi-briefcase" /></div>
        <div class="col-6 col-md-3"><StatCard label="Applications" :value="report.applications_count" icon="bi-file-earmark-text" color="linear-gradient(135deg,#198754,#146c43)" /></div>
        <div class="col-6 col-md-3"><StatCard label="Students applied" :value="report.students_applied" icon="bi-people" color="linear-gradient(135deg,#fd7e14,#dc6803)" /></div>
        <div class="col-6 col-md-3"><StatCard label="Students selected" :value="report.students_selected" icon="bi-trophy" color="linear-gradient(135deg,#6f42c1,#59339d)" /></div>
      </div>

      <div class="row g-3">
        <div class="col-md-7">
          <div class="card p-3">
            <h6>Applications by status — {{ report.period }}</h6>
            <ChartCanvas
              v-if="monthStatusLabels.length"
              type="bar"
              :labels="monthStatusLabels"
              :datasets="[{ label: 'Applications', data: monthStatusValues, backgroundColor: '#0d6efd' }]"
              :options="countAxisOptions"
            />
            <p v-else class="text-muted small mb-0">No applications recorded in this month.</p>
          </div>
        </div>
        <div class="col-md-5">
          <div class="card p-3">
            <h6>Top companies this month</h6>
            <table class="table table-sm mb-0" v-if="report.top_companies.length">
              <thead><tr><th>Company</th><th>Drives</th><th>Applications</th></tr></thead>
              <tbody>
                <tr v-for="row in report.top_companies" :key="row[0]"><td>{{ row[0] }}</td><td>{{ row[1] }}</td><td>{{ row[2] }}</td></tr>
              </tbody>
            </table>
            <p v-else class="text-muted small mb-0">No applications recorded this month yet.</p>
          </div>
        </div>
      </div>
    </template>

    <hr class="my-4">

    <h4 class="mb-3">Portal-wide trends</h4>
    <div v-if="overviewLoading" class="text-center py-5"><span class="spinner-border text-primary"></span></div>
    <div v-else-if="overviewError" class="alert alert-warning d-flex justify-content-between align-items-center">
      <span><i class="bi bi-exclamation-triangle me-1"></i>Couldn't load portal-wide trends: {{ overviewError }}</span>
      <button class="btn btn-sm btn-outline-dark" @click="loadOverview">Retry</button>
    </div>
    <template v-else-if="overview">
      <div class="row g-3 mb-3">
        <div class="col-md-6">
          <div class="card p-3">
            <h6>Applications received, by month (all companies)</h6>
            <ChartCanvas
              type="line"
              :labels="appTrendLabels"
              :datasets="[{
                label: 'Applications',
                data: appTrendCounts,
                borderColor: '#0d6efd',
                backgroundColor: 'rgba(13,110,253,0.15)',
                tension: 0.3,
                fill: true
              }]"
              :options="countAxisOptions"
            />
          </div>
        </div>
        <div class="col-md-6">
          <div class="card p-3">
            <h6>Student visits, by month</h6>
            <ChartCanvas
              type="line"
              :labels="visitTrendLabels"
              :datasets="[{
                label: 'Student visits',
                data: visitTrendCounts,
                borderColor: '#198754',
                backgroundColor: 'rgba(25,135,84,0.15)',
                tension: 0.3,
                fill: true
              }]"
              :options="countAxisOptions"
            />
          </div>
        </div>
      </div>
      <div class="row g-3">
        <div class="col-md-8">
          <div class="card p-3">
            <h6>Top 5 companies by applications received</h6>
            <ChartCanvas
              v-if="topCompanyLabels.length"
              type="bar"
              :labels="topCompanyLabels"
              :datasets="[{ label: 'Applications', data: topCompanyCounts, backgroundColor: '#fd7e14' }]"
              :options="horizontalCountOptions"
            />
            <p v-else class="text-muted small mb-0">No applications recorded yet.</p>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import ChartCanvas from '@/components/shared/ChartCanvas.vue'
import adminService from '@/services/adminService'
import StatCard from '@/components/shared/StatCard.vue'

export default {
  name: 'AdminReports',
  components: { StatCard, ChartCanvas },
  data() {
    return {
      report: null,
      loading: false,
      triggering: false,
      triggeringReminders: false,
      toast: '',
      // Left blank on purpose: the first load asks the backend which month to
      // open on (the newest one with activity) and fills this in from the
      // response, so the panel never opens on an empty month.
      monthInput: '',
      reportError: '',
      overviewError: '',
      overview: null,
      overviewLoading: false,
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
    currentMonthLabel() {
      return new Date().toLocaleString(undefined, { month: 'long', year: 'numeric' })
    },
    monthStatusLabels() {
      return Object.keys(this.report?.status_breakdown || {}).map((k) => k.replace(/_/g, ' '))
    },
    monthStatusValues() {
      return Object.values(this.report?.status_breakdown || {})
    },
    appTrendLabels() {
      return (this.overview?.monthly_applications || []).map((m) => m.label)
    },
    appTrendCounts() {
      return (this.overview?.monthly_applications || []).map((m) => m.count)
    },
    visitTrendLabels() {
      return (this.overview?.monthly_visits || []).map((m) => m.label)
    },
    visitTrendCounts() {
      return (this.overview?.monthly_visits || []).map((m) => m.count)
    },
    topCompanyLabels() {
      return (this.overview?.top_companies || []).map((c) => c.company_name)
    },
    topCompanyCounts() {
      return (this.overview?.top_companies || []).map((c) => c.count)
    }
  },
  created() {
    this.load()
    this.loadOverview()
  },
  methods: {
    errorText(e) {
      return e?.response?.data?.message || e?.message || String(e)
    },
    async load() {
      this.loading = true
      this.reportError = ''
      try {
        // Omitting year/month lets the backend choose the newest month that has
        // activity; once it answers we sync the picker to whatever it picked.
        let params
        if (this.monthInput) {
          const [year, month] = this.monthInput.split('-').map(Number)
          params = { year, month }
        }
        const { data } = await adminService.monthlyReportPreview(params)
        this.report = data.report
        this.monthInput = `${data.report.year}-${String(data.report.month).padStart(2, '0')}`
      } catch (e) {
        console.error('[AdminReports] monthly report failed:', e)
        this.reportError = this.errorText(e)
      } finally {
        this.loading = false
      }
    },
    async loadOverview() {
      this.overviewLoading = true
      this.overviewError = ''
      try {
        const { data } = await adminService.reportsOverview()
        this.overview = data
      } catch (e) {
        console.error('[AdminReports] overview failed:', e)
        this.overviewError = this.errorText(e)
      } finally {
        this.overviewLoading = false
      }
    },
    async triggerMonthly() {
      this.triggering = true
      try {
        await adminService.triggerMonthlyReport()
        this.toast = 'Monthly report generation started — check the admin inbox shortly.'
        setTimeout(() => { this.toast = '' }, 4000)
      } finally {
        this.triggering = false
      }
    },
    async triggerReminders() {
      this.triggeringReminders = true
      try {
        await adminService.triggerReminders()
        this.toast = 'Deadline reminder job started.'
        setTimeout(() => { this.toast = '' }, 4000)
      } finally {
        this.triggeringReminders = false
      }
    }
  }
}
</script>
