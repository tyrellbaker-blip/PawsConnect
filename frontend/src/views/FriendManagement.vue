<template>
  <div class="friend-management">
    <h2>Friend Management</h2>

    <!-- Friend Search -->
    <div class="friend-search">
      <h3>Search Users</h3>
      <search-bar @search-results="handleSearchResults"></search-bar>
      <div v-if="searchResults.length > 0">
        <ul>
          <li v-for="user in searchResults" :key="user.id">
            {{ user.username }}
            <button v-if="!isFriend(user.id)" @click="sendFriendRequest(user.id)">Add Friend</button>
            <button v-else @click="removeFriend(user.id)">Remove Friend</button>
          </li>
        </ul>
      </div>
    </div>

    <!-- Friend Requests -->
    <div class="friend-requests">
      <h3>Friend Requests</h3>
      <div v-if="incomingFriendRequests.length > 0">
        <ul>
          <li v-for="request in incomingFriendRequests" :key="request.id">
            {{ request.from.username }}
            <button @click="acceptFriendRequest(request.id)">Accept</button>
            <button @click="rejectFriendRequest(request.id)">Reject</button>
          </li>
        </ul>
      </div>
      <p v-else>No incoming friend requests.</p>
    </div>

    <!-- Friends List -->
    <div class="friends-list">
      <h3>Friends</h3>
      <div v-if="friends.length > 0">
        <ul>
          <li v-for="friend in friends" :key="friend.id">
            {{ friend.username }}
            <button @click="removeFriend(friend.id)">Remove Friend</button>
          </li>
        </ul>
      </div>
      <p v-else>You have no friends yet.</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import SearchBar from '@/views/SearchBar.vue';

export default {
  components: {
    SearchBar,
  },
  data() {
    return {
      searchResults: [],
      incomingFriendRequests: [],
      friends: [],
    };
  },
  created() {
    this.fetchFriendData();
  },
  methods: {
    async fetchFriendData() {
      try {
        const userId = this.$store.state.auth.user.id;
        const [friendsResponse, requestsResponse] = await Promise.all([
          axios.get(`/api/users/${userId}/friends/`),
          axios.get(`/api/users/${userId}/friend-requests/`),
        ]);
        this.friends = friendsResponse.data;
        this.incomingFriendRequests = requestsResponse.data;
      } catch (error) {
        console.error('Error fetching friend data:', error);
      }
    },
    handleSearchResults(results) {
      this.searchResults = results;
    },
    isFriend(userId) {
      return this.friends.some((friend) => friend.id === userId);
    },
    async sendFriendRequest(userId) {
      try {
        await axios.post('/api/friend-requests/', { to_user: userId });
        // Update friend data after successful request
        await this.fetchFriendData();
      } catch (error) {
        console.error('Error sending friend request:', error);
      }
    },
    async acceptFriendRequest(requestId) {
      try {
        await axios.post(`/api/friend-requests/${requestId}/accept/`);
        // Update friend data after accepting request
        await this.fetchFriendData();
      } catch (error) {
        console.error('Error accepting friend request:', error);
      }
    },
    async rejectFriendRequest(requestId) {
      try {
        await axios.post(`/api/friend-requests/${requestId}/reject/`);
        // Update friend data after rejecting request
        await this.fetchFriendData();
      } catch (error) {
        console.error('Error rejecting friend request:', error);
      }
    },
    async removeFriend(userId) {
      try {
        await axios.delete(`/api/users/${this.$store.state.auth.user.id}/friends/${userId}/`);
        // Update friend data after removing friend
        await this.fetchFriendData();
      } catch (error) {
        console.error('Error removing friend:', error);
      }
    },
  },
};
</script>