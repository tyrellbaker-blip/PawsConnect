<template>
  <div class="profile-container">
    <div class="profile-header">
      <!-- Display user profile information (username, profile picture, etc.) -->
      <img :src="user.profile_picture" alt="Profile Picture" class="profile-picture" />
      <h2>{{ user.display_name }}</h2>
      <p>{{ user.location }}</p>
    </div>
    <div class="profile-tabs">
      <div class="tab-header">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :class="{ active: currentTab === tab.id }"
          @click="currentTab = tab.id"
        >
          {{ tab.title }}
        </button>
      </div>
      <div class="tab-content">
        <div v-if="currentTab === 'posts'" class="tab-posts">
          <user-posts :userId="user.id" :displayName="user.display_name"></user-posts>
        </div>
        <div v-if="currentTab === 'transfer'" class="tab-transfer">
          <transfer-pet></transfer-pet>
        </div>
        <div v-if="currentTab === 'create'" class="tab-create">
          <post-creation></post-creation>
        </div>
        <div v-if="currentTab === 'friends'" class="tab-friends">
          <friend-management></friend-management>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import UserPosts from '@/views/UserPosts.vue';
import TransferPet from 'src/components/TransferPet.vue';
import PostCreation from './PostCreate.vue';
import FriendManagement from './FriendManagement.vue';

export default {
  components: {
    UserPosts,
    TransferPet,
    PostCreation,
    FriendManagement,
  },
  data() {
    return {
      user: null,
      currentTab: 'posts', // Default tab
      tabs: [
        { id: 'posts', title: 'Posts' },
        { id: 'transfer', title: 'Pet Transfer' },
        { id: 'create', title: 'Create Post' },
        { id: 'friends', title: 'Friends' },
      ],
    };
  },
  created() {
    this.fetchUser();
  },
  methods: {
    async fetchUser() {
      try {
        // Fetch user information based on the current user or the user whose profile is being viewed
        const userId = this.$route.params.userId || this.$store.state.auth.user.id;
        const response = await axios.get(`/api/users/${userId}/`);
        this.user = response.data;
      } catch (error) {
        console.error(error);
      }
    },
  },
};
</script>