<template>
  <div>
    <div class="pet-profile mb-3">
      <a :href="editPetUrl" class="btn btn-primary">
        <i class="fas fa-cog"></i> Edit Profile
      </a>
      <h1 style="text-align: center">{{ petProfile.owner }}'s Pet Profile</h1>

      <p v-if="petProfile.name">Name: {{ petProfile.name }}</p>
      <p v-if="petProfile.species">Species: {{ petProfile.species }}</p>
      <p v-if="petProfile.breed">Breed: {{ petProfile.breed }}</p>
      <p v-if="petProfile.age">Age: {{ petProfile.age }}</p>
      <p v-if="isOwner">This is your pet!</p>

      <br><hr class="left-align-hr">
    </div>
  </div>
</template>

<script>
export default {
  name: 'PetProfileComponent',
  data() {
    return {
      petProfile: {
        owner: 'Username',
        name: 'Fluffy',
        species: 'Cat',
        breed: 'Maine Coon',
        age: 5
      },
      isOwner: true,
      editPetUrl: '/edit-pet-profile'
    }
  }
}
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
