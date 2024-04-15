<template>
  <div class="post-create">
    <h2>Create Post</h2>
    <form @submit.prevent="createPost">
      <div>
        <label for="content">Content</label>
        <textarea id="content" v-model="postData.content" required></textarea>
      </div>
      <div>
        <label for="photo">Photo</label>
        <input type="file" id="photo" @change="handlePhotoUpload" />
      </div>
      <div>
        <label>Visibility</label>
        <div>
          <label>
            <input type="radio" v-model="postData.visibility" value="Public" />
            Public
          </label>
          <label>
            <input type="radio" v-model="postData.visibility" value="Friends Only" />
            Friends Only
          </label>
        </div>
      </div>
      <div>
        <label>Tag Pets</label>
        <div v-for="pet in user.pets" :key="pet.id">
          <label>
            <input type="checkbox" :value="pet.id" v-model="postData.tagged_pets" />
            {{ pet.name }}
          </label>
        </div>
      </div>
      <button type="submit">Create Post</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PostCreate',
  data() {
    return {
      postData: {
        content: '',
        photo: null,
        visibility: 'Public',
        tagged_pets: [],
      },
      user: null,
    };
  },
  created() {
    this.fetchUser();
  },
  methods: {
    async fetchUser() {
      try {
        const userId = this.$store.state.auth.user.id;
        const response = await axios.get(`/api/users/${userId}/`);
        this.user = response.data;
      } catch (error) {
        console.error(error);
      }
    },
    handlePhotoUpload(event) {
      this.postData.photo = event.target.files[0];
    },
    async createPost() {
      try {
        const formData = new FormData();
        formData.append('content', this.postData.content);
        formData.append('visibility', this.postData.visibility);
        formData.append('photo', this.postData.photo);
        this.postData.tagged_pets.forEach((petId) => {
          formData.append('tagged_pets', petId);
        });

        await axios.post('/api/posts/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        // Reset form fields after successful post creation
        this.postData.content = '';
        this.postData.photo = null;
        this.postData.tagged_pets = [];

        console.log('Post created successfully');
      } catch (error) {
        console.error(error);
      }
    },
  },
};
</script>