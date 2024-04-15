<template>
  <div>
    <h2>Search</h2>
    <form @submit.prevent="searchEntities">
      <div class="form-group">
        <label for="type">{{ form.type.label }}</label>
        <select id="type" v-model="form.type" @change="onTypeChange">
          <option value="user">User</option>
          <option value="pet">Pet</option>
        </select>
      </div>
      <div class="form-group">
        <label for="query">{{ form.query.label }}</label>
        <input id="query" type="text" v-model="form.query">
      </div>
      <div class="form-group" v-show="form.type === 'user'">
        <label for="city">{{ form.city.label }}</label>
        <input id="city" type="text" v-model="form.city">
        <label for="state">{{ form.state.label }}</label>
        <input id="state" type="text" v-model="form.state">
        <label for="zip_code">{{ form.zip_code.label }}</label>
        <input id="zip_code" type="text" v-model="form.zip_code">
        <label for="range">{{ form.range.label }}</label>
        <input id="range" type="number" v-model="form.range">
      </div>
      <div class="form-group" v-show="form.type === 'pet'">
        <label for="pet_id">{{ form.pet_id.label }}</label>
        <input id="pet_id" type="text" v-model="form.pet_id">
        <label for="pet_name">{{ form.pet_name.label }}</label>
        <input id="pet_name" type="text" v-model="form.pet_name">
      </div>
      <button type="submit" class="btn btn-primary">Search</button>
    </form>
    <div id="search-results">
      <div v-if="results.length > 0">
        <div v-if="form.type === 'user'">
          <h3>User Results</h3>
          <ul class="list-group">
            <li v-for="user in results" :key="user.id" class="list-group-item">
              Username: {{ user.username }}<br>
              Email: {{ user.email }}
            </li>
          </ul>
        </div>
        <div v-else-if="form.type === 'pet'">
          <h3>Pet Results</h3>
          <ul class="list-group">
            <li v-for="pet in results" :key="pet.id" class="list-group-item">
              Pet Name: {{ pet.name }}<br>
              Pet ID: {{ pet.id }}
            </li>
          </ul>
        </div>
      </div>
      <p v-else>No results found.</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      form: {
        type: 'user',
        query: '',
        city: '',
        state: '',
        zip_code: '',
        range: null,
        pet_id: '',
        pet_name: ''
      },
      results: []
    };
  },
  methods: {
    onTypeChange() {
      // Clear form fields when the search type changes
      this.form.query = '';
      this.form.city = '';
      this.form.state = '';
      this.form.zip_code = '';
      this.form.range = null;
      this.form.pet_id = '';
      this.form.pet_name = '';
    },
    async searchEntities() {
      try {
        const response = await axios.get('/search/', { params: this.form });
        this.results = response.data.results;
      } catch (error) {
        console.error('Error searching entities:', error);
      }
    }
  }
};
</script>