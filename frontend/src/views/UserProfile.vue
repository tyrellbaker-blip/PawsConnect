<!-- UserProfile.vue -->
<template>
  <div>
    <div class="user-info">
      <img :src="user.profilePicture" alt="User Profile Picture" />
      <h2>{{ user.displayName }}</h2>
      <p>{{ user.aboutMe }}</p>
      <p>Location: {{ user.location }}</p>
      <p>Email: {{ user.email }}</p>
      <p>Join Date: {{ user.dateJoined }}</p>
      <router-link to="/edit-profile" class="btn btn-primary">Edit Profile</router-link>
    </div>

    <div class="pet-list">
      <h3>Pets</h3>
      <div v-for="pet in user.pets" :key="pet.id" class="pet-item">
        <router-link :to="'/pet-profile/' + pet.id">
          <img :src="pet.profilePicture" alt="Pet Profile Picture" />
          <p>{{ pet.name }}</p>
        </router-link>
      </div>
      <router-link to="/request-pet-transfer" class="btn btn-primary">Request Pet Transfer</router-link>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      user: {},
    };
  },
  mounted() {
    this.fetchUserProfile();
  },
  methods: {
    async fetchUserProfile() {
      try {
        const response = await axios.get('/users/{id}/');
        this.user = response.data;
      } catch (error) {
        console.error(error);
      }
    },
  },
};
</script>

<style scoped>
/* Add your styles here */
</style>