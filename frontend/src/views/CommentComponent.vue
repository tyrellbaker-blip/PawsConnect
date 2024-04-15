<template>
  <div class="comment-component">
    <div class="comment-form">
      <textarea v-model="newComment" placeholder="Write a comment..."></textarea>
      <button @click="addComment">Post</button>
    </div>
    <div class="comment-list">
      <div v-for="comment in comments" :key="comment.id" class="comment">
        <img :src="comment.user.profilePicture" alt="User Profile Picture" class="user-avatar">
        <div class="comment-content">
          <span class="username">{{ comment.user.username }}</span>
          <p>{{ comment.content }}</p>
        </div>
      </div>
    </div>
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
      comments: [],
      newComment: ''
    };
  },
  mounted() {
    this.fetchComments();
  },
  methods: {
    async fetchComments() {
      try {
        const response = await axios.get(`/comments/?post=${this.post.id}`);
        this.comments = response.data;
      } catch (error) {
        console.error('Error fetching comments:', error);
      }
    },
    async addComment() {
      try {
        const response = await axios.post('/comments/', {
          post: this.post.id,
          user: this.$store.state.user.id,
          content: this.newComment
        });
        this.comments.push(response.data);
        this.newComment = '';
      } catch (error) {
        console.error('Error adding comment:', error);
      }
    }
  }
};
</script>