<template>
  <div>
    <h2>Send Friend Request</h2>
    <form @submit.prevent="sendFriendRequest">
      <div>
        <label for="username">Username:</label>
        <input type="text" id="username" v-model="username" required>
      </div>
      <button type="submit">Send Request</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      username: ''
    };
  },
  methods: {
    async sendFriendRequest() {
      try {
        const response = await axios.post('/friendships/', { user_to: this.username });
        console.log('Friend request sent successfully');
        this.username = '';
        // Handle success, e.g., show a success message
      } catch (error) {
        console.error('Error sending friend request:', error);
        // Handle error, e.g., show an error message
      }
    }
  }
};
</script>