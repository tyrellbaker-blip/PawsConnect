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
        <label for="firstName">First Name</label>
        <input id="firstName" v-model="form.firstName" type="text" placeholder="First Name" required>
        <span v-if="errors.firstName" class="error-message">{{ errors.firstName }}</span>
      </div>
      <div>
        <label for="lastName">Last Name</label>
        <input id="lastName" v-model="form.lastName" type="text" placeholder="Last Name" required>
        <span v-if="errors.lastName" class="error-message">{{ errors.lastName }}</span>
      </div>
      <div>
        <label for="displayName">Display Name</label>
        <input id="displayName" v-model="form.displayName" type="text" placeholder="Display Name" required>
        <span v-if="errors.displayName" class="error-message">{{ errors.displayName }}</span>
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
        <label for="zip">ZIP Code</label>
        <input id="zip" v-model="form.zip" type="text" placeholder="ZIP Code" required>
        <span v-if="errors.zip" class="error-message">{{ errors.zip }}</span>
      </div>
      <div>
        <label for="hasPets">Do you have pets?</label>
        <input id="hasPets" v-model="form.hasPets" type="checkbox">
      </div>
      <div v-if="form.hasPets">
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
        firstName: '',
        lastName: '',
        displayName: '',
        city: '',
        state: '',
        zip: '',
        hasPets: false,
        pets: [{ name: '', pet_type: '', age: null, breed: '', color: '' }]
      },
      errors: {},
      successMessage: '',
      errorMessage: ''
    }
  },
  methods: {
    addPet() {
      this.form.pets.push({ name: '', pet_type: '', age: null, breed: '', color: '' });
    },
    async registerUser() {
      this.errors = this.validateForm();
      if (Object.keys(this.errors).length === 0) {
        try {
         const response = await axios.post('/register/', this.form);
          this.successMessage = "Registration successful!";
          console.log("Response", response.data);
          this.resetForm();
          localStorage.setItem('user-token', response.data.token);
          await router.push(`/profile/${response.data.slug}`);
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
        email: '', password: '', firstName: '', lastName: '',
        displayName: '', city: '', state: '', zip: '',
        hasPets: false, pets: [{name: '', pet_type: '', age: null, breed: '', color: ''}]
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
      if (!this.form.firstName) {
        errors.firstName = "First Name is required.";
      }
      if (!this.form.lastName) {
        errors.lastName = "Last Name is required.";
      }
      if (!this.form.displayName) {
        errors.displayName = "Display Name is required.";
      }
      if (!this.form.city) {
        errors.city = "City is required.";
      }
      if (!this.form.state) {
        errors.state = "State is required.";
      }
      if (!this.form.zip) {
        errors.zip = "ZIP Code is required.";
      }

      // Validate pet information if hasPets is true
      if (this.form.hasPets) {
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