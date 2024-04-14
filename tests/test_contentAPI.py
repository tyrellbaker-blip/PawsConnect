from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from UserManagement.models import CustomUser
from PetManagement.models import Pet
from Content.models import Post, Comment

class PostAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.pet = Pet.objects.create(
            name='Buddy',
            owner=self.user,
            age=5
        )
        self.post = Post.objects.create(
            user=self.user,
            content='Initial post',
            visibility=Post.VisibilityChoices.PUBLIC
        )
        self.post.tagged_pets.add(self.pet)

    def test_create_post_with_pet_tags(self):
        url = reverse('content:post-list')
        data = {'content': 'New post', 'visibility': 'Public', 'tagged_pets': [self.pet.id]}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Post.objects.filter(tagged_pets__in=[self.pet]).exists())

    def test_list_posts(self):
        url = reverse('content:post-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if self.pet.id is in any of the 'tagged_pets' lists of the returned posts
        found = any(self.pet.id in post['tagged_pets'] for post in response.data)
        self.assertTrue(found, "Pet ID not found in any post's tagged pets.") # Adjust based on the initial data set up

    def test_retrieve_post(self):
        url = reverse('content:post-detail', args=[self.post.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.pet.id, [pet for pet in response.data['tagged_pets']])

    def test_update_post_add_pet_tags(self):
        url = reverse('content:post-detail', args=[self.post.id])
        data = {'tagged_pets': [self.pet.id]}  # Assuming adding tagged pets
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertTrue(self.pet in self.post.tagged_pets.all())

    def test_delete_post(self):
        url = reverse('content:post-detail', args=[self.post.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)
