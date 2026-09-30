<template>
  <div class="container py-4">
    <div v-if="drive">
      <router-link to="/company/drives" class="small text-decoration-none"><i class="bi bi-arrow-left me-1"></i>Back to drives</router-link>
      <h3 class="mt-2">{{ drive.job_title }}</h3>
      <p class="text-muted">{{ drive.company_name }} · {{ drive.location }} · Deadline {{ drive.application_deadline }}</p>
    </div>

    <EmptyState v-if="!loading && !applications.length" message="No applications yet for this drive." icon="bi-people" />
    <div v-else class="table-responsive">
      <table class="table align-middle bg-white">
        <thead><tr><th>Student</th><th>Branch</th><th>CGPA</th><th>Resume</th><th>Status</th><th class="text-end">Actions</th></tr></thead>
        <tbody>
          <tr v-for="a in applications" :key="a.id">
            <td>{{ a.student.full_name }}<div class="small text-muted">{{ a.student.email }}</div></td>
            <td>{{ a.student.branch }} '{{ String(a.student.year).slice(-2) }}</td>
            <td>{{ a.student.cgpa }}</td>
            <td>
              <span v-if="a.student.has_resume" class="text-success small"><i class="bi bi-file-earmark-check"></i> On file</span>
              <span v-else class="text-muted small">Not uploaded</span>
            </td>
            <td style="min-width:180px;">
              <select class="form-select form-select-sm" :value="a.status" @change="updateStatus(a, $event.target.value)">
                <option value="applied">Applied / waiting</option>
                <option value="shortlisted">Shortlisted</option>
                <option value="interview_scheduled">Interview scheduled</option>
                <option value="selected">Selected</option>
                <option value="rejected">Rejected</option>
              </select>
            </td>
            <td class="text-end">
              <button class="btn btn-sm btn-outline-primary" @click="openInterview(a)"><i class="bi bi-calendar-event"></i> Schedule interview</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="modal fade" tabindex="-1" ref="interviewModalEl">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Schedule interview</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="interviewTarget">
            <p class="small text-muted">For {{ interviewTarget.student.full_name }}</p>
            <div class="mb-2">
              <label class="form-label small">Round name</label>
              <input v-model="interviewForm.round_name" class="form-control form-control-sm">
            </div>
            <div class="mb-2">
              <label class="form-label small">Date &amp; time</label>
              <input v-model="interviewForm.scheduled_at" type="datetime-local" class="form-control form-control-sm">
            </div>
            <div class="mb-2">
              <label class="form-label small">Mode</label>
              <select v-model="interviewForm.mode" class="form-select form-select-sm">
                <option value="online">Online</option>
                <option value="offline">Offline</option>
              </select>
            </div>
            <div class="mb-2">
              <label class="form-label small">Location / link</label>
              <input v-model="interviewForm.location_or_link" class="form-control form-control-sm">
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancel</button>
            <button class="btn btn-primary" @click="submitInterview">Schedule</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap'
import companyService from '@/services/companyService'
import EmptyState from '@/components/shared/EmptyState.vue'

export default {
  name: 'CompanyDriveApplications',
  components: { EmptyState },
  props: { id: { type: [String, Number], required: true } },
  data() {
    return {
      drive: null, applications: [], loading: false,
      interviewTarget: null, interviewModal: null,
      interviewForm: { round_name: 'Technical Round', scheduled_at: '', mode: 'online', location_or_link: '' }
    }
  },
  async created() {
    this.loading = true
    try {
      const { data } = await companyService.driveApplications(this.id)
      this.drive = data.drive
      this.applications = data.applications
    } finally { this.loading = false }
  },
  mounted() {
    this.interviewModal = new Modal(this.$refs.interviewModalEl)
  },
  methods: {
    async updateStatus(a, status) {
      await companyService.updateApplicationStatus(a.id, status)
      a.status = status
    },
    openInterview(a) {
      this.interviewTarget = a
      this.interviewForm = { round_name: 'Technical Round', scheduled_at: '', mode: 'online', location_or_link: '' }
      this.interviewModal.show()
    },
    async submitInterview() {
      await companyService.scheduleInterview(this.interviewTarget.id, this.interviewForm)
      this.interviewTarget.status = 'interview_scheduled'
      this.interviewModal.hide()
    }
  }
}
</script>
