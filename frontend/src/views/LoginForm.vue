<template>
 <form @submit.prevent="submitLogin">
   <div>
     <label for="username">Username:</label>
     <input type="text" id="username" v-model="username" required>
   </div>
   <div>
     <label for="password">Password:</label>
     <input type="password" id="password" v-model="password" required>
   </div>
   <div v-if="error" class="alert alert-danger" role="alert">
     {{ error }}
   </div>
   <button type="submit" class="btn btn-primary">Login</button>
 </form>
</template>

<script>
import axios from 'axios';

export default {
 data() {
   return {
     username: '',
     password: '',
     error: '',
   };
 },
 methods: {
   async submitLogin() {
     try {
       const response = await axios.post('http://localhost:8000/api/login/', {
         username: this.username,
         password: this.password,
       });
       // Handle successful login response
       console.log('Login successful:', response.data);
       // TODO: Store the token, redirect to dashboard, etc.
     } catch (error) {
       // Handle login error
       console.error('Login failed:', error.response.data);
       this.error = 'Invalid username or password. Please try again.';
     }
   },
 },
};
</script>