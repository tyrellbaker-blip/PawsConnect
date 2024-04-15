<template>
  <div id="app">
    <!-- This will render the component based on the route -->
    <router-view></router-view>
  </div>
</template>

<script>
// No need to import LoginComponent or RegistrationForm here as they will be used by the router

export default {
  name: 'App'
}
</script>

<style>
/* Your global styles will go here */
</style>