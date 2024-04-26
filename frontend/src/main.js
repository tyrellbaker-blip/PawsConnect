import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import axios from 'axios';

// Configure Axios to send requests to the Django backend
axios.defaults.baseURL = 'http://localhost:8000/api'; // Assuming your Django API is served at http://localhost:8000/api

// Axios Setup
axios.interceptors.request.use(
  (config) => {
    const token = store.getters['auth/token']; // Use the correct getter for the token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

const app = createApp(App);
app.use(router);
app.use(store);

if (process.env.NODE_ENV === 'development') {
  app.config.devtools = true;
}

// Dispatch initAuth and then mount the app
store.dispatch('auth/initAuth').then(() => {
  app.mount('#app');
}).catch(error => {
  console.error('Failed to initialize auth:', error);
});