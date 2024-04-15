<template>
  <div class="post">
    <div class="post-header">
      <img :src="post.user.profile_picture" alt="User Profile Picture" class="user-avatar">
      <div class="user-info">
        <span class="username">{{ post.user.username }}</span>
        <span class="timestamp">{{ formatTimestamp(post.timestamp) }}</span>
      </div>
    </div>
    <div class="post-content">
      <p>{{ post.content }}</p>
      <img v-if="post.photo" :src="post.photo" alt="Post Photo" class="post-photo">
      <div v-if="post.tagged_pets.length > 0">
        <h4>Tagged Pets:</h4>
        <ul>
          <li v-for="pet in post.tagged_pets" :key="pet.id">{{ pet.name }}</li>
        </ul>
      </div>
    </div>
    <div class="post-footer">
      <span class="visibility">Visibility: {{ post.visibility }}</span>
      <like-component :post="post"></like-component>
      <comment-component :post="post"></comment-component>
    </div>
  </div>
</template>
<script>
import LikeComponent from './LikeComponent.vue';
import CommentComponent from './CommentComponent.vue';

export default {
  components: {
    LikeComponent,
    CommentComponent
  },
  props: {
    post: {
      type: Object,
      required: true,
      validator: (post) => {
        return (
          'user' in post &&
          'content' in post &&
          'timestamp' in post &&
          'photo' in post
        );
      }
    }
  },
  methods: {
    formatTimestamp(timestamp) {
      return new Date(timestamp).toLocaleString();
    }
  }
};
</script>