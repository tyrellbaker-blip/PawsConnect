<template>
  <div>
    <h2>Respond to Pet Transfer Request</h2>
    <div v-if="transferRequests.length > 0">
      <label for="transferRequestSelect">Select a transfer request:</label>
      <select id="transferRequestSelect" v-model="selectedTransferRequestId" @change="fetchTransferRequest">
        <option v-for="request in transferRequests" :key="request.id" :value="request.id">
          Pet ID: {{ request.petId }}, Sender: {{ request.user.username }}
        </option>
      </select>
    </div>
    <div v-else>
      No transfer requests to respond to.
    </div>
    <div v-if="transferRequest">
      <p>Pet ID: {{ transferRequest.petId }}</p>
      <p>Sender Username: {{ transferRequest.user.username }}</p>
      <button @click="acceptTransfer">Accept</button>
      <button @click="rejectTransfer">Reject</button>
    </div>
    <div v-if="responseStatus" class="status">
      {{ responseStatus }}
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PetTransferResponse',
  data() {
    return {
      transferRequests: [],
      selectedTransferRequestId: null,
      transferRequest: null,
      responseStatus: '',
    };
  },
  created() {
    this.fetchTransferRequests();
  },
  methods: {
    async fetchTransferRequests() {
      try {
        const response = await axios.get('/api/pet-transfer-requests/');
        this.transferRequests = response.data;
      } catch (error) {
        console.error(error);
      }
    },
    async fetchTransferRequest() {
      if (this.selectedTransferRequestId) {
        try {
          const response = await axios.get(`/api/pet-transfer-requests/${this.selectedTransferRequestId}/`);
          this.transferRequest = response.data;
        } catch (error) {
          console.error(error);
        }
      } else {
        this.transferRequest = null;
      }
    },
    async acceptTransfer() {
      try {
        await axios.post(`/api/pet-transfer-requests/${this.transferRequest.id}/accept/`);
        this.responseStatus = 'Transfer request accepted';
        // Perform any additional actions after accepting the transfer
      } catch (error) {
        this.responseStatus = 'Error accepting transfer request';
        console.error(error);
      }
    },
    async rejectTransfer() {
      try {
        await axios.post(`/api/pet-transfer-requests/${this.transferRequest.id}/reject/`);
        this.responseStatus = 'Transfer request rejected';
        // Perform any additional actions after rejecting the transfer
      } catch (error) {
        this.responseStatus = 'Error rejecting transfer request';
        console.error(error);
      }
    },
  },
};
</script>