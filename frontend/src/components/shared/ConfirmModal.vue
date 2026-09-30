<template>
  <div class="modal fade" tabindex="-1" ref="modalEl">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ title }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <p>{{ message }}</p>
          <div v-if="requireReason" class="mb-2">
            <label class="form-label small">Reason</label>
            <textarea v-model="reason" class="form-control" rows="2"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancel</button>
          <button class="btn" :class="confirmClass" @click="confirm">{{ confirmLabel }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap'

export default {
  name: 'ConfirmModal',
  props: {
    title: { type: String, default: 'Please confirm' },
    message: { type: String, default: 'Are you sure?' },
    confirmLabel: { type: String, default: 'Confirm' },
    confirmClass: { type: String, default: 'btn-primary' },
    requireReason: { type: Boolean, default: false }
  },
  emits: ['confirm'],
  data() {
    return { reason: '', modalInstance: null }
  },
  mounted() {
    this.modalInstance = new Modal(this.$refs.modalEl)
  },
  methods: {
    open() {
      this.reason = ''
      this.modalInstance.show()
    },
    confirm() {
      this.$emit('confirm', this.reason)
      this.modalInstance.hide()
    }
  }
}
</script>
