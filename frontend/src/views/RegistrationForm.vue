<template>
  <div>
    <h2>Register</h2>
    <form @submit.prevent="registerUser">
      <div>
        <label for="email">Email</label>
        <input id="email" v-model="form.email" type="email" placeholder="Email" required>
        <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
      </div>
      <div>
        <label for="password">Password</label>
        <input id="password" v-model="form.password" type="password" placeholder="Password" required>
        <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
      </div>
      <div>
        <label for="first_name">First Name</label>
        <input id="first_name" v-model="form.first_name" type="text" placeholder="First Name" required>
        <span v-if="errors.first_name" class="error-message">{{ errors.first_name }}</span>
      </div>
      <div>
        <label for="lastName">Last Name</label>
        <input id="lastName" v-model="form.last_name" type="text" placeholder="Last Name" required>
        <span v-if="errors.last_name" class="error-message">{{ errors.last_name }}</span>
      </div>
      <div>
        <label for="display_name">Display Name</label>
        <input id="display_name" v-model="form.display_name" type="text" placeholder="Display Name" required>
        <span v-if="errors.display_name" class="error-message">{{ errors.display_name }}</span>
      </div>
      <div>
        <label for="city">City</label>
        <input id="city" v-model="form.city" type="text" placeholder="City" required>
        <span v-if="errors.city" class="error-message">{{ errors.city }}</span>
      </div>
      <div>
        <label for="state">State</label>
        <input id="state" v-model="form.state" type="text" placeholder="State" required>
        <span v-if="errors.state" class="error-message">{{ errors.state }}</span>
      </div>
      <div>
        <label for="zip_code">ZIP Code</label>
        <input id="zip_code" v-model="form.zip_code" type="text" placeholder="ZIP Code" required>
        <span v-if="errors.zip_code" class="error-message">{{ errors.zip_code }}</span>
      </div>
      <div>
        <label for="preferred_language">Preferred Language</label>
        <select id="preferred_language" v-model="form.preferred_language" required>
          <option value="">Select Language</option>
          <option value="en">English</option>
          <option value="es">Spanish</option>
          <option value="fr">French</option>
          <option value="de">German</option>
          <option value="it">Italian</option>
        </select>
        <span v-if="errors.preferred_language" class="error-message">{{ errors.preferred_language }}</span>
      </div>
      <div>
        <label for="has_pets">Do you have pets?</label>
        <input id="has_pets" v-model="form.has_pets" type="checkbox">
      </div>
      <div v-if="form.has_pets">
        <h3>Pet Information</h3>
        <div v-for="(pet, index) in form.pets" :key="index">
          <label :for="'petName' + index">Pet Name</label>
          <input :id="'petName' + index" v-model="pet.name" type="text" placeholder="Pet Name" required>
          <label :for="'petType' + index">Pet Type</label>
          <select :id="'petType' + index" v-model="pet.pet_type" required>
            <option value="">Select Pet Type</option>
            <option value="dog">Dog</option>
            <option value="cat">Cat</option>
            <option value="bird">Bird</option>
            <option value="reptile">Reptile</option>
            <option value="other">Other</option>
          </select>
          <label :for="'petAge' + index">Pet Age</label>
          <input :id="'petAge' + index" v-model="pet.age" type="number" placeholder="Pet Age" required>
          <label :for="'petBreed' + index">Pet Breed</label>
          <input :id="'petBreed' + index" v-model="pet.breed" type="text" placeholder="Pet Breed" required>
          <label :for="'petColor' + index">Pet Color</label>
          <input :id="'petColor' + index" v-model="pet.color" type="text" placeholder="Pet Color" required>
        </div>
        <button type="button" @click="addPet">Add Another Pet</button>
      </div>
      <div>
        <label for="profile_picture">Profile Picture</label>
        <input id="profile_picture" type="file" @change="onProfilePictureChange">
      </div>
      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
      </div>
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
      <button type="submit">Register</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';
import router from "@/router";

export default {
  name: "RegistrationForm",
  data() {
    return {
      form: {
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        display_name: '',
        city: '',
        state: '',
        zip_code: '',
        has_pets: false,
        preferred_language: '',
        pets: [{name: '', pet_type: '', age: null, breed: '', color: ''}],
        profile_picture: null,
      },
      errors: {},
      successMessage: '',
      errorMessage: ''
    }
  },
  methods: {
    addPet() {
      this.form.pets.push({name: '', pet_type: '', age: null, breed: '', color: ''});
    },
    onProfilePictureChange(event) {
      this.form.profile_picture = event.target.files[0];
    },
    async registerUser() {
      this.errors = this.validateForm();
      if (Object.keys(this.errors).length === 0) {
        try {
          const formData = new FormData();
          formData.append('email', this.form.email);
          formData.append('password', this.form.password);
          formData.append('first_name', this.form.first_name);
          formData.append('last_name', this.form.last_name);
          formData.append('display_name', this.form.display_name);
          formData.append('city', this.form.city);
          formData.append('state', this.form.state);
          formData.append('zip_code', this.form.zip_code);
          formData.append('has_pets', this.form.has_pets);
          formData.append('preferred_language', this.form.preferred_language);
          if (this.form.profile_picture) {
            formData.append('profile_picture', this.form.profile_picture);
          }
          this.form.pets.forEach((pet, index) => {
            formData.append(`pets-${index}-name`, pet.name);
            formData.append(`pets-${index}-pet_type`, pet.pet_type);
            formData.append(`pets-${index}-age`, pet.age);
            formData.append(`pets-${index}-breed`, pet.breed);
            formData.append(`pets-${index}-color`, pet.color);
          });

          const response = await axios.post('http://127.0.0.1:8000/user/register/', formData);
          this.successMessage = "Registration successful!";
          console.log("Response", response.data);
          this.resetForm();
          localStorage.setItem('user-token', response.data.token);

          // Navigate to the user's profile page
          await router.push(`/user/${response.data.id}`);
        } catch (error) {
          console.error('Registration failed. Please try again.', error);
          if (error.response && error.response.status === 401) {
            this.errorMessage = "Unauthorized. Please log in again.";
            localStorage.removeItem('user-token');
            await router.push('/login');
          } else {
            this.errorMessage = "Registration failed. Please check your inputs and try again.";
          }
        }
      }
    },
    resetForm() {
      this.form = {
        email: '', password: '', first_name: '', last_name: '',
        display_name: '', city: '', state: '', zip_code: '',
        has_pets: false, pets: [{name: '', pet_type: '', age: null, breed: '', color: ''}],
        preferred_language: '',
        profile_picture: null,
      };
      this.errors = {};
    },
    validateForm() {
      let errors = {};
      if (!this.form.email) {
        errors.email = "Email is required.";
      } else if (!this.validEmail(this.form.email)) {
        errors.email = "Please enter a valid email address.";
      }
      if (!this.form.password) {
        errors.password = "Password is required.";
      }
      if (!this.form.first_name) {
        errors.first_name = "First Name is required.";
      }
      if (!this.form.last_name) {
        errors.lastName = "Last Name is required.";
      }
      if (!this.form.display_name) {
        errors.display_name = "Display Name is required.";
      }
      if (!this.form.city) {
        errors.city = "City is required.";
      }
      if (!this.form.state) {
        errors.state = "State is required.";
      }
      if (!this.form.zip_code) {
        errors.zip_code = "ZIP Code is required.";
      }
      if(!this.form.preferred_language)
      {
        errors.form.preferred_language = "Preferred Language is required.";
      }

      // Validate pet information if hasPets is true
      if (this.form.has_pets) {
        this.form.pets.forEach((pet, index) => {
          if (!pet.name) {
            errors[`petName${index}`] = "Pet name is required.";
          }
          if (!pet.pet_type) {
            errors[`petType${index}`] = "Pet type is required.";
          }
          if (pet.age === null || pet.age < 0) {
            errors[`petAge${index}`] = "Pet age must be a positive number.";
          }
          if (!pet.breed) {
            errors[`petBreed${index}`] = "Pet breed is required.";
          }
          if (!pet.color) {
            errors[`petColor${index}`] = "Pet color is required.";
          }
        });
      }

      return errors;
    },
    validEmail(email) {
      let re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
      return re.test(email);
    }
  },
  created() {
    // Set up Axios interceptors
    axios.defaults.baseURL = 'http://localhost:8000/api';
    axios.interceptors.request.use(config => {
      const token = localStorage.getItem('user-token');
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }
      return config;
    });

    axios.interceptors.response.use(
        response => response,
        error => {
          if (error.response && error.response.status === 401) {
            localStorage.removeItem('user-token');
            router.push('/login');
          }
          return Promise.reject(error);
        }
    );
  }
}
</script>

<style scoped>
.error-message {
  color: red;
}

.success-message {
  color: green;
}
</style>