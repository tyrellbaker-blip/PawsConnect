<template>
  <div>
    <h2>Request Pet Transfer</h2>
    <div v-if="pets.length > 0">
      <label for="petSelect">Select a pet:</label>
      <select id="petSelect" v-model="selectedPetId" @change="populateTransferRequest">
        <option v-for="pet in pets" :key="pet.id" :value="pet.id">
          {{ pet.name }} ({{ pet.petId }})
        </option>
      </select>
    </div>
    <div v-else>
      No pets available for transfer.
    </div>
    <form v-if="transferRequest.petId" @submit.prevent="submitTransferRequest">
      <div>
        <label for="petId">Pet ID:</label>
        <input type="text" id="petId" v-model="transferRequest.petId" readonly>
      </div>
      <div>
        <label for="receiverUsername">Receiver Username:</label>
        <input type="text" id="receiverUsername" v-model="transferRequest.receiverUsername" required>
      </div>
      <button type="submit">Submit Request</button>
    </form>
    <div v-if="requestStatus" class="status">
      {{ requestStatus }}
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PetTransferRequest',
  data() {
    return {
      pets: [],
      selectedPetId: null,
      transferRequest: {
        petId: '',
        receiverUsername: '',
      },
      requestStatus: '',
    };
  },
  created() {
    this.fetchPets();
  },
  methods: {
    async fetchPets() {
      try {
        const response = await axios.get('/api/pets/');
        this.pets = response.data;
      } catch (error) {
        console.error(error);
      }
    },
    populateTransferRequest() {
      const selectedPet = this.pets.find(pet => pet.id === this.selectedPetId);
      if (selectedPet) {
        this.transferRequest.petId = selectedPet.petId;
      } else {
        this.transferRequest.petId = '';
      }
    },
    async submitTransferRequest() {
      try {
        await axios.post('/api/pet-transfer-requests/', this.transferRequest);
        this.requestStatus = 'Transfer request submitted successfully';
        // Clear the form fields after successful submission
        this.transferRequest.receiverUsername = '';
      } catch (error) {
        this.requestStatus = 'Error submitting transfer request';
        console.error(error);
      }
    },
  },
};
</script>