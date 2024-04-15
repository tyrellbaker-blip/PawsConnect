<template>
  <div class="user-posts">
    <h2>{{ displayName }}'s Posts</h2>
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="posts.length === 0" class="no-posts">No posts available.</div>
    <div v-else class="posts-container">
      <div v-for="post in visiblePosts" :key="post.id" class="post-item">
        <post-component :post="post"></post-component>
      </div>
      <div v-if="hasMorePosts" class="load-more" @click="loadMorePosts">
        Load More
      </div>
      <div v-if="currentPage > 1" class="show-less" @click="showLessPosts">
        Show Less
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import PostComponent from '@/views/PostComponent.vue';

export default {
  name: 'UserPosts',
  components: {
    PostComponent,
  },
  props: {
    userId: {
      type: Number,
      required: true,
    },
    displayName: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      posts: [],
      loading: true,
      currentPage: 1,
      pageSize: 10,
      hasMorePosts: true,
    };
  },
  computed: {
    visiblePosts() {
      const startIndex = (this.currentPage - 1) * this.pageSize;
      const endIndex = startIndex + this.pageSize;
      return this.posts.slice(startIndex, endIndex);
    },
  },
  created() {
    this.fetchPosts();
  },
  methods: {
    async fetchPosts() {
      this.loading = true;
      try {
        const response = await axios.get(`/api/users/${this.userId}/posts/`);
        this.posts = response.data;
        this.hasMorePosts = false;
      } catch (error) {
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
    loadMorePosts() {
      if (this.hasMorePosts) {
        this.currentPage += 1;
      }
    },
    showLessPosts() {
      if (this.currentPage > 1) {
        this.currentPage -= 1;
      }
    },
  },
};
</script>