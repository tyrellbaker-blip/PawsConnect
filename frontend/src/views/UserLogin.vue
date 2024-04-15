<template>
  <div class="container mt-5">
    <div class="p-4 rounded">
      <div id="content">
        <h2 class="text-black">Login</h2>
        <div id="loginFormContainer">
          <form @submit.prevent="loginUser" class="text-black" id="loginForm">
            <div>
              <label for="username">Username:</label>
              <input type="text" id="username" v-model="form.username" required>
            </div>
            <div>
              <label for="password">Password:</label>
              <input type="password" id="password" v-model="form.password" required>
            </div>
            <div v-if="nonFieldErrors" class="alert alert-danger" role="alert">
              {{ nonFieldErrors }}
            </div>
            <button type="submit" class="btn btn-primary">Login</button>
          </form>
        </div>
        <button @click="loginWithGoogle" class="btn btn-danger" id="googleLoginBtn">Login with Google</button>
        <br>
        <router-link to="/register" class="btn btn-primary">Don't have an Account? Register</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      form: {
        username: '',
        password: ''
      },
      nonFieldErrors: ''
    };
  },
  methods: {
  async loginUser() {
  try {
    const response = await axios.post('/api/login/', this.form);  // Ensure endpoint matches your Django settings

    // Handle successful login
    console.log("Response:", response);
    if (response.data.token) {
      // Store the token in localStorage
      localStorage.setItem('authToken', response.data.token);

      // Optionally set the header for all requests
      axios.defaults.headers.common['Authorization'] = `Token ${response.data.token}`;

      // Clear form fields and error messages
      this.form.username = '';
      this.form.password = '';
      this.nonFieldErrors = '';

      // Redirect to home page or desired route
      this.$router.push('/');  // Modify the path as needed, e.g., to a user dashboard
    } else {
      this.nonFieldErrors = 'Login successful but no token received.';
    }
  } catch (error) {
    this.handleLoginError(error);
  }
},

handleLoginError(error) {
  // Handle login error
  if (error.response) {
    if (error.response.status === 400) {
      // Bad Request - Handle validation errors
      const errors = error.response.data;
      if (errors.non_field_errors) {
        this.nonFieldErrors = errors.non_field_errors.join(', ');
      } else {
        // Handle individual field errors if needed
        console.error('Validation errors:', errors);
      }
    } else if (error.response.status === 401) {
      // Unauthorized - Handle invalid credentials
      this.nonFieldErrors = 'Invalid username or password.';
    } else {
      // Handle other error status codes
      console.error('Login failed:', error.response.status, error.response.data);
      this.nonFieldErrors = 'An error occurred. Please try again later.';
    }
  } else if (error.request) {
    // No response received from the server
    console.error('No response from the server:', error.request);
    this.nonFieldErrors = 'Unable to reach the server. Please check your internet connection.';
  } else {
    // Other errors
    console.error('Login failed:', error.message);
    this.nonFieldErrors = 'An error occurred. Please try again later.';
  }
}
,
   loginWithGoogle() {
    const googleLoginUrl = 'https://accounts.google.com/o/oauth2/auth';
    const clientId = process.env.VUE_APP_OAUTH_CLIENT_ID;
    const redirectUri = process.env.VUE_APP_GOOGLE_AUTH_REDIRECT_URI ;
    const scope = 'profile email';
    const responseType = 'code';

    window.location.href = `${googleLoginUrl}?client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}&scope=${scope}&response_type=${responseType}`;
  }
}
};
</script>

<style scoped>
body {
  background-image: url('@/assets/background.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  margin: 0;
  padding: 0;
}
</style>