import axios from 'axios';

// Configure Axios to send requests to the Django backend
axios.defaults.baseURL = 'http://localhost:8000';

const state = {
  user: null,
  token: localStorage.getItem('user-token') || '', // Get token from local storage or set to empty
};

const getters = {
  isAuthenticated: state => !!state.token, // Check if the token is present
  token: state => state.token, // Getter for the token
};

const mutations = {
  SET_TOKEN(state, token) {
    state.token = token;
    localStorage.setItem('user-token', token); // Store token in local storage
  },
  CLEAR_TOKEN(state) {
    state.token = '';
    localStorage.removeItem('user-token'); // Remove token from local storage
  },
  SET_USER(state, user) {
    state.user = user;
  }
};

const actions = {
  async login({ commit }, credentials) {
    try {
      const response = await axios.post('/users/login', credentials);
      commit('SET_TOKEN', response.data.token); // Assuming your backend sends back the token
      commit('SET_USER', response.data.user); // Optionally set user info if your backend sends it
      localStorage.setItem('user-token', response.data.token); // Optionally handle token storage in mutation
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  },
  logout({ commit }) {
    commit('CLEAR_TOKEN');
    commit('SET_USER', null); // Optionally clear user info on logout
  },
  async register({ commit }, userData) {
    try {
      const response = await axios.post('http://127.0.0.1:8000/user/register/', userData);
      commit('SET_TOKEN', response.data.token); // Save the token if registration logs the user in
      commit('SET_USER', response.data.user); // Set user data if included in the registration response
      localStorage.setItem('user-token', response.data.token); // Persist the token in local storage
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  },
  async fetchUser({ commit }, userId) {
    try {
      const response = await axios.get(`/users/${userId}/`);
      commit('SET_USER', response.data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
    }
  },
  initAuth({ commit }) {
    const token = localStorage.getItem('user-token');
    if (token) {
      commit('SET_TOKEN', token); // Assuming token is still valid
      // Optionally verify token validity with the backend here
      return axios.get('/verify-token', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      .then(response => {
        commit('SET_USER', response.data.user); // Set user data if token is verified
      })
      .catch(error => {
        console.error('Token verification failed:', error);
        commit('CLEAR_TOKEN'); // Clear token if verification fails
      });
    } else {
      return Promise.resolve(); // Resolve immediately if no token
    }
  }
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
};