<template>
  <div>

    <h1 style="text-align: center;">{{ username }}'s Pets</h1>
    <br><hr class="left-align-hr">

    <div class="container mt-5">
      <div class="row">
        <div v-if="pets.length">
          <div class="col-md-4 mb-4" v-for="pet in pets" :key="pet.id">
            <div class="card">
              <img v-if="pet.profilePicture" :src="pet.profilePicture" class="card-img-top" :alt="pet.name">
              <!-- Placeholder can be added here if no profile picture -->
              <div class="card-body">
                <h5 class="card-title">{{ pet.name }}</h5>
                <p class="card-text">Age: {{ pet.age }}</p>
                <p class="card-text">Owner: {{ username }}</p>
                <a :href="'/pet-profile/' + pet.slug" class="btn btn-primary">View Profile</a>
                <a :href="'/delete-pet/' + pet.id" class="btn btn-danger">Delete</a>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="container">
          <div class="row justify-content-center">
            <div class="col-md-6 text-center">
              <p>No pets found.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="container mt-3">
      <div class="row justify-content-center">
        <div class="col-md-4 text-center">
          <a href="/add-pet" class="btn btn-success">Add Pet</a>
          <a href="/user/profile/" class="btn btn-primary">Back to Profile</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PetsComponent',
  data() {
    return {
      username: 'User123',  // Placeholder for dynamic username
      pets: [
        { id: 1, name: 'Fluffy', age: 5, slug: 'fluffy', profilePicture: 'path/to/picture.jpg' },
        { id: 2, name: 'Spot', age: 3, slug: 'spot', profilePicture: null }  // No image for Spot
      ]
    }
  }
}
</script>

<style scoped>
  .left-align-hr {
        width: calc(500% + 200px);
        margin: 0 -50px 50px -500px;
        border: none;
        border-top: 3px dotted darkblue;
        border-radius: 5px;
      }
</style>
