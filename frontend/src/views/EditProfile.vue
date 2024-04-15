<!-- EditProfile.vue -->
<template>
  <div class="container mt-5">
    <h1 class="text-center">Edit Profile</h1>
    <hr class="left-align-hr" />

    <form @submit.prevent="updateProfile">
      <div class="form-group">
        <label for="first-name">First Name</label>
        <input type="text" id="first-name" v-model="form.firstName" class="form-control" />
      </div>

      <div class="form-group">
        <label for="last-name">Last Name</label>
        <input type="text" id="last-name" v-model="form.lastName" class="form-control" />
      </div>

      <div class="form-group">
        <label for="display-name">Display Name</label>
        <input type="text" id="display-name" v-model="form.displayName" class="form-control" />
      </div>

      <div class="form-group">
        <label for="city">City</label>
        <input type="text" id="city" v-model="form.city" class="form-control" />
      </div>

      <div class="form-group">
        <label for="state">State</label>
        <input type="text" id="state" v-model="form.state" class="form-control" />
      </div>

      <div class="form-group">
        <label for="zip">ZIP Code</label>
        <input type="text" id="zip" v-model="form.zip" class="form-control" />
      </div>

      <div class="form-group">
        <label for="about-me">About Me</label>
        <textarea id="about-me" v-model="form.aboutMe" class="form-control"></textarea>
      </div>

      <div class="form-group">
        <label for="profile-picture">Profile Picture</label>
        <input type="file" id="profile-picture" @change="onProfilePictureChange" class="form-control-file" />
      </div>

      <div class="form-group">
        <h3>Pets</h3>
        <ul>
          <li v-for="(pet, index) in form.pets" :key="index">
            <input type="text" v-model="pet.name" placeholder="Pet Name" />
            <button type="button" @click="removePet(index)">Remove</button>
          </li>
        </ul>
        <button type="button" @click="addPet">Add Pet</button>
      </div>

      <div class="row justify-content-center">
        <div class="col-auto">
          <button type="submit" class="btn btn-primary">Save Changes</button>
        </div>
        <div class="col-auto">
          <router-link :to="'/profile/' + user.slug" class="btn btn-primary">Cancel</router-link>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      form: {
        firstName: '',
        lastName: '',
        displayName: '',
        city: '',
        state: '',
        zip: '',
        aboutMe: '',
        profilePicture: null,
        pets: [],
      },
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
        this.form.firstName = this.user.firstName;
        this.form.lastName = this.user.lastName;
        this.form.displayName = this.user.displayName;
        this.form.city = this.user.city;
        this.form.state = this.user.state;
        this.form.zip = this.user.zip;
        this.form.aboutMe = this.user.aboutMe;
        this.form.pets = this.user.pets.map(pet => ({ name: pet.name }));
      } catch (error) {
        console.error(error);
      }
    },
    onProfilePictureChange(event) {
      this.form.profilePicture = event.target.files[0];
    },
    addPet() {
      this.form.pets.push({ name: '' });
    },
    removePet(index) {
      this.form.pets.splice(index, 1);
    },
    async updateProfile() {
      try {
        const formData = new FormData();
        formData.append('first_name', this.form.firstName);
        formData.append('last_name', this.form.lastName);
        formData.append('display_name', this.form.displayName);
        formData.append('city', this.form.city);
        formData.append('state', this.form.state);
        formData.append('zip', this.form.zip);
        formData.append('about_me', this.form.aboutMe);
        if (this.form.profilePicture) {
          formData.append('profile_picture', this.form.profilePicture);
        }
        formData.append('pets', JSON.stringify(this.form.pets));

        await axios.patch('/users/{id}/', formData);
        // Handle successful profile update
        this.$router.push('/profile/' + this.user.slug);
      } catch (error) {
        console.error(error);
      }
    },
  },
};
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