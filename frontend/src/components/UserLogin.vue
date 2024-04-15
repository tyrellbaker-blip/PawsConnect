<template>


  <div class="container mt-5">
    <div class="p-4 rounded">
      <div id="content">
        <h2 class="text-black">Login</h2>
        <div id="loginFormContainer">
          <form @submit.prevent="handleLogin" class="text-black" id="loginForm">
            <!-- Render form fields -->
            <p v-for="field in formFields" :key="field.id">
              <label :for="field.id">{{ field.label }}</label>
              <input :type="field.type" :id="field.id" :name="field.name" v-model="field.value">
            </p>

            <!-- Display non-field errors -->
            <div v-if="nonFieldErrors.length" class="alert alert-danger" role="alert">
              <p v-for="error in nonFieldErrors" :key="error">{{ error }}</p>
            </div>
            <button type="submit" class="btn btn-primary">Login</button>
          </form>
        </div>
        <!-- Google Login Button -->
        <button @click="loginWithGoogle" class="btn btn-danger" id="googleLoginBtn">Login with Google</button>

        <br>
        <!-- Registration Link -->
        <a href="/register" class="btn btn-primary">Don't have an Account? Register</a>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      nonFieldErrors: [],
      formFields: [
        { id: 'id_username', label: 'Username', type: 'text', name: 'username', value: '' },
        { id: 'id_password', label: 'Password', type: 'password', name: 'password', value: '' }
      ],
    };
  },
  methods: {
    handleLogin() {
      const { username, password } = this.formFields.reduce((acc, field) => {
        acc[field.name] = field.value.trim();
        return acc;
      }, {});

      if (!username || !password) {
        alert("Username and Password fields cannot be empty!");
      } else {
        // Implement login logic here
        console.log("Submitting form...");
      }
    },
    loginWithGoogle() {
      // Logic to handle Google login
      this.$refs.loginFormContainer.style.display = 'none';
      console.log("Google login process started...");
    }
  }
}
</script>
  <style scoped>
    body {
      background-image: url('../assets/background.jpg');
      background-size: cover;
      background-position: center;
      background-repeat: no-repeat;
      margin: 0;
      padding: 0;
    }
  </style>
