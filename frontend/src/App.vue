<template>
  <div id="app">
    <div id="loginContent">
      <h2 class="text-black">Login</h2>
      <LoginComponent/>
    </div>
    <div id="registerContent">
      <h2 class="text-black">Register</h2>
      <RegistrationForm />
    </div>
  </div>
</template>

<script>
import LoginComponent from './components/UserLogin.vue'
import RegistrationForm from './components/RegistrationForm.vue'

export default {
  name: 'App',
  components: {
    LoginComponent,
    RegistrationForm
  }
}
</script>

<style>
/* Styles will be added later */
</style>