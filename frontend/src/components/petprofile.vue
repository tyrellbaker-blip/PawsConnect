<template>
  <div>
    <div class="pet-profile mb-3">
      <router-link :to="editPetUrl" class="btn btn-primary">
        <i class="fas fa-cog"></i> Edit Profile
      </router-link>
      <h1 style="text-align: center">{{ petProfile.pet.owner.username }}'s Pet Profile</h1>
      <p v-if="petProfile.pet.name">Name: {{ petProfile.pet.name }}</p>
      <p v-if="petProfile.pet.breed">Breed: {{ petProfile.pet.breed }}</p>
      <p v-if="petProfile.pet.color">Color: {{ petProfile.pet.color }}</p>
      <p v-if="petProfile.pet.age">Age: {{ petProfile.pet.age }}</p>
      <p v-if="petProfile.pet.get_display_pet_type">Pet Type: {{ petProfile.pet.get_display_pet_type }}</p>
      <p v-if="petProfile.description">Description: {{ petProfile.description }}</p>
      <p v-if="isOwner">This is your pet!</p>
      <br>
      <hr class="left-align-hr">
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PetProfileComponent',
  data() {
    return {
      petProfile: {
        pet: {},
        description: ''
      },
      isOwner: false,
      editPetUrl: '/edit-pet-profile'
    };
  },
  mounted() {
    this.fetchPetProfile();
  },
  methods: {
    async fetchPetProfile() {
      try {
        const petSlug = this.$route.params.slug;
        const response = await axios.get(`/pet-profiles/${petSlug}/`);
        this.petProfile = response.data;

        // Check if the logged-in user is the owner of the pet
        const userId = localStorage.getItem('userId');
        this.isOwner = (this.petProfile.pet.owner === userId);
      } catch (error) {
        console.error(error);
      }
    }
  }
};
</script>

<style scoped>
.pet-profile {
  margin-top: 20px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.left-align-hr {
  width: calc(500% + 200px);
  margin: 0 -50px 50px -500px;
  border: none;
  border-top: 3px dotted darkblue;
  border-radius: 5px;
}
</style>