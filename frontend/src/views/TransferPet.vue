<template>
  <div class="transfer-pet">
    <h2>Pet Transfer</h2>
    <div class="transfer-sections">
      <div class="transfer-request">
        <h3>Request Pet Transfer</h3>
        <pet-transfer-request @requestSubmitted="fetchTransferRequests"></pet-transfer-request>
      </div>
      <div class="transfer-response">
        <h3>Respond to Transfer Requests</h3>
        <div v-if="incomingTransferRequests.length === 0">
          No incoming transfer requests.
        </div>
        <div v-else>
          <div
            v-for="request in incomingTransferRequests"
            :key="request.id"
            class="transfer-request-item"
          >
            <pet-transfer-response
              :transferRequest="request"
              @requestAccepted="fetchTransferRequests"
              @requestRejected="fetchTransferRequests"
            ></pet-transfer-response>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { mapState, mapActions } from 'vuex'
import PetTransferRequest from '@/views/PetTransferRequest.vue'
import PetTransferResponse from '@/views/PetTransferResponse.vue'
import router from '@/router'; // Import your Vue Router instance

export default {
  name: 'TransferPet',
  components: {
    PetTransferRequest,
    PetTransferResponse
  },
  computed: {
    ...mapState('auth', ['user'])
  },
  created() {
    this.fetchUser(this.$route.params.userId || null) // Access $route.params
  },
  methods: {
    ...mapActions('auth', ['fetchUser']),
    async fetchTransferRequests() {
      try {
        const userId = this.user.id
        const response = await axios.get(`/api/users/${userId}/pet-transfer-requests/`)
        this.incomingTransferRequests = response.data
      } catch (error) {
        console.error(error)
      }
    }
  },
  data() {
    return {
      incomingTransferRequests: []
    }
  },
  router // Expose the router instance to the component
}
</script>