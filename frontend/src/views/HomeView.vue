<template>
  <div class="container mt-5">
    <div class="row">
      <div class="col-md-8">
        <h1 class="homepage-welcome">Welcome to PawsConnect</h1>
        <p class="homepage-description">
          Welcome to PawsConnect, the ultimate social network for pet lovers! This
          platform allows you to connect with a vibrant community of pet owners,
          share your cherished moments, explore valuable advice, and discover new
          friendships for both you and your beloved pets. Whether you're here to
          showcase your pet's latest adventures, seek tips on pet care, or just
          browse the delightful array of pet photos, PawsConnect is your go-to
          hub for all things pets. Join us and become part of this wonderful
          pet-loving family!
        </p>
      </div>
      <div class="col-md-4 homepage-aside">
        <img
          src="../assets/homepic.jpeg"
          alt="Owner and Dog"
          class="img-fluid"
        />
        <div class="mt-3">
          <router-link to="/login" class="homepage-button">Login</router-link>
          <router-link to="/register" class="homepage-button">Register</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "HomeView",
};
</script>

<style scoped>
/* Add your styles here if needed */
</style>