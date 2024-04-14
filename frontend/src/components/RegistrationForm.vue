<template>
  <div>
    <h2>Register</h2>
    <form @submit.prevent="registerUser">
      <div>
        <label for="email">Email</label>
        <input id="email" v-model="form.email" type="email" placeholder="Email" required />
      </div>
      <div>
        <label for="password">Password</label>
        <input id="password" v-model="form.password" type="password" placeholder="Password" required />
      </div>
      <div>
        <label for="firstName">First Name</label>
        <input id="firstName" v-model="form.firstName" type="text" placeholder="First Name" required />
      </div>
      <div>
        <label for="lastName">Last Name</label>
        <input id="lastName" v-model="form.lastName" type="text" placeholder="Last Name" required />
      </div>
      <div>
        <label for="displayName">Display Name</label>
        <input id="displayName" v-model="form.displayName" type="text" placeholder="Display Name" required />
      </div>
      <div>
        <label for="city">City</label>
        <input id="city" v-model="form.city" type="text" placeholder="City" required />
      </div>
      <div>
        <label for="state">State</label>
        <input id="state" v-model="form.state" type="text" placeholder="State" required />
      </div>
      <div>
        <label for="zip">Zip Code</label>
        <input id="zip" v-model="form.zip" type="text" placeholder="Zip Code" required />
      </div>
      <div>
        <label>
          <input v-model="form.hasPets" type="checkbox" /> Do you have pets?
        </label>
      </div>
      <div v-if="form.hasPets">
        <h3>Pet Information</h3>
        <div v-for="(pet, index) in form.pets" :key="index">
          <div>
            <label for="petName">Pet Name</label>
            <input id="petName" v-model="pet.name" type="text" placeholder="Pet Name" required />
          </div>
          <div>
            <label for="petType">Pet Type</label>
            <input id="petType" v-model="pet.type" type="text" placeholder="Pet Type" required />
          </div>
          <div>
            <label for="petAge">Pet Age</label>
            <input id="petAge" v-model="pet.age" type="number" placeholder="Pet Age" required />
          </div>
          <!-- Add more pet fields as needed -->
        </div>
        <button type="button" @click="addPet">Add Pet</button>
      </div>
      <button type="submit">Register</button>
    </form>
  </div>
</template>
<script>
export default {
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
        pets: [{
          name: '',
          type: '',
          age: null
        }]
      }
    }
  },
  methods: {
    registerUser() {
      // Handle the user registration logic here
    },
    addPet() {
      this.form.pets.push({ name: '', type: '', age: null });
    }
  }
}
</script>
