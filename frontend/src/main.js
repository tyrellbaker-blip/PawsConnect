import { createApp } from 'vue'
import App from './App.vue'
import './assets/styles.css'
import router from './router';

const app = createApp(App);

// Use the router with the Vue application
app.use(router);

// Mount the Vue application to the DOM
app.mount('#app');