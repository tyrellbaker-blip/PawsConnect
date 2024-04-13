from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from UserManagement.models import CustomUser
from .models import Post  # Assuming you have a Post model


class PostAPITests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # Create a user for authentication purposes
        cls.user = CustomUser.objects.create_user(username='testuser', password='testpass123')

    def test_list_posts(self):
        """
        Ensure we can retrieve a list of posts.
        """
        url = reverse('post-list')  # 'post-list' should match the name used in your urls.py
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_post_authenticated(self):
        """
        Ensure we can create a new post when authenticated.
        """
        self.client.login(username='testuser', password='testpass123')
        url = reverse('post-list')
        data = {'title': 'New Post', 'content': 'Some content'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get().title, 'New Post')

    def test_create_post_unauthenticated(self):
        """
        Ensure unauthenticated users cannot create posts.
        """
        url = reverse('post-list')
        data = {'title': 'New Post', 'content': 'Some content'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


from django.test import TestCase

# Create your tests here.
