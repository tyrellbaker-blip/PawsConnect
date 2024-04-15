<template>
  <div>
    <div class="text-left mb-3">
      <a :href="editProfileUrl" class="btn btn-primary">
        <i class="fas fa-cog"></i> Edit Profile
      </a>
      <h1 style="text-align: center">{{ userProfile.displayName }}'s Profile</h1>
    </div>

    <p v-if="userProfile.aboutMe">Bio: {{ userProfile.aboutMe }}</p>
    <p v-if="userProfile.location">Location: {{ userProfile.location }}</p>

    <div v-if="userProfile.isAuthenticated">
      <p>Email: {{ userProfile.email }}</p>
      <p>Join date: {{ userProfile.dateJoined | formatDate }}</p>

      <div class="btn-group d-flex justify-content-center" role="group" aria-label="User actions">
        <a :href="petsUrl" class="btn btn-primary">Pets</a>
        <a :href="friendsUrl" class="btn btn-primary">Friends</a>
        <a :href="photosUrl" class="btn btn-primary">Photos</a>
      </div>
    </div>

    <br><hr class="left-align-hr">
  </div>
</template>

<script>
export default {

  name: 'ProfileComponent',
  data() {
    return {
      userProfile: {
        displayName: 'User Name',
        aboutMe: 'Some bio about the user...',
        location: 'Some location',
        email: 'user@example.com',
        dateJoined: new Date(),
        isAuthenticated: true
      },
      editProfileUrl: '/edit-profile',
      petsUrl: '/user-pets',
      friendsUrl: '/user-friends',
      photosUrl: '/user-photos'
    }
    },
  filters: {
    formatDate(value) {
      if (value) {
        return value.toLocaleDateString();
      }
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
