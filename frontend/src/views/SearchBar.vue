<template>
  <div class="search-bar">
    <div class="form-group">
      <select v-model="searchType" @change="clearFilters">
        <option value="user">User</option>
        <option value="pet">Pet</option>
      </select>
    </div>
    <div class="form-group">
      <input type="text" v-model="searchQuery" placeholder="Search" />
    </div>
    <div class="form-group" v-if="searchType === 'user'">
      <input type="text" v-model="city" placeholder="City" />
      <input type="text" v-model="state" placeholder="State" />
      <input type="text" v-model="zipCode" placeholder="Zip Code" />
      <div>
        <label>
          <input type="radio" v-model="range" :value="5" /> 5 miles
        </label>
        <label>
          <input type="radio" v-model="range" :value="10" /> 10 miles
        </label>
        <label>
          <input type="radio" v-model="range" :value="20" /> 20 miles
        </label>
        <label>
          <input type="radio" v-model="range" :value="50" /> 50 miles
        </label>
      </div>
    </div>
    <div class="form-group" v-if="searchType === 'pet'">
      <input type="text" v-model="petId" placeholder="Pet ID" />
      <input type="text" v-model="petName" placeholder="Pet Name" />
    </div>
    <button @click="performSearch">Search</button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      searchType: 'user',
      searchQuery: '',
      city: '',
      state: '',
      zipCode: '',
      range: null,
      petId: '',
      petName: '',
    };
  },
  methods: {
    clearFilters() {
      this.searchQuery = '';
      this.city = '';
      this.state = '';
      this.zipCode = '';
      this.range = null;
      this.petId = '';
      this.petName = '';
    },
    async performSearch() {
      try {
        const response = await axios.get('/search/', {
          params: {
            type: this.searchType,
            query: this.searchQuery,
            city: this.city,
            state: this.state,
            zip_code: this.zipCode,
            range: this.range,
            pet_id: this.petId,
            pet_name: this.petName,
          },
        });
        // Emit an event with the search results
        this.$emit('search-results', response.data.results);
      } catch (error) {
        console.error('Error searching entities:', error);
      }
    },
  },
};
</script>