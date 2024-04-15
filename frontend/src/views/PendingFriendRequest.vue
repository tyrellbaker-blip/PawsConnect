<template>
  <div>
    <h2>Pending Friend Requests</h2>
    <ul>
      <li v-for="request in pendingRequests" :key="request.id">
        <p>From: {{ request.user_from.username }}</p>
        <button @click="acceptFriendRequest(request.id)">Accept</button>
        <button @click="rejectFriendRequest(request.id)">Reject</button>
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      pendingRequests: []
    };
  },
  mounted() {
    this.fetchPendingRequests();
  },
  methods: {
    async fetchPendingRequests() {
      try {
        const response = await axios.get('/friendships/', { params: { status: 'pending' } });
        this.pendingRequests = response.data;
      } catch (error) {
        console.error('Error fetching pending friend requests:', error);
      }
    },
    async acceptFriendRequest(requestId) {
      try {
        await axios.post(`/friendships/${requestId}/accept/`);
        console.log('Friend request accepted');
        await this.fetchPendingRequests();
      } catch (error) {
        console.error('Error accepting friend request:', error);
      }
    },
    async rejectFriendRequest(requestId) {
      try {
        await axios.post(`/friendships/${requestId}/reject/`);
        console.log('Friend request rejected');
        await this.fetchPendingRequests();
      } catch (error) {
        console.error('Error rejecting friend request:', error);
      }
    }
  }
};
</script>