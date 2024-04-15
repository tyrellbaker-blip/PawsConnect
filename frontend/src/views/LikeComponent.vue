<template>
  <div class="like-component">
    <button @click="toggleLike" :class="{ 'liked': isLiked }">
      <i class="fas fa-heart"></i> {{ likeCount }}
    </button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    post: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      isLiked: false,
      likeCount: 0
    };
  },
  mounted() {
    this.fetchLikeStatus();
    this.fetchLikeCount();
  },
  methods: {
    async fetchLikeStatus() {
      try {
        const response = await axios.get(`/likes/?post=${this.post.id}&user=${this.$store.state.user.id}`);
        this.isLiked = response.data.length > 0;
      } catch (error) {
        console.error('Error fetching like status:', error);
      }
    },
    async fetchLikeCount() {
      try {
        const response = await axios.get(`/likes/count/?post=${this.post.id}`);
        this.likeCount = response.data.count;
      } catch (error) {
        console.error('Error fetching like count:', error);
      }
    },
    async toggleLike() {
      try {
        if (this.isLiked) {
          await axios.delete(`/likes/?post=${this.post.id}&user=${this.$store.state.user.id}`);
          this.isLiked = false;
          this.likeCount--;
        } else {
          await axios.post('/likes/', { post: this.post.id, user: this.$store.state.user.id });
          this.isLiked = true;
          this.likeCount++;
        }
      } catch (error) {
        console.error('Error toggling like:', error);
      }
    }
  }
};
</script>