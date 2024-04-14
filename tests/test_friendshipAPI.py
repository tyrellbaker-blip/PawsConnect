from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from UserManagement.models import Friendship

class FriendshipAPITests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # Initial setup data that doesn't conflict with individual tests
        cls.user = get_user_model().objects.create_user(username='testuser', password='testpass123')
        cls.other_user = get_user_model().objects.create_user(username='otheruser', password='testpass123')

    def setUp(self):
        # Re-authenticate before each test
        self.client.force_authenticate(user=self.user)

    def create_unique_user(self, username):
        # Helper function to create unique users
        return get_user_model().objects.create_user(username=username, password='testpass123')

    def test_create_friendship_request(self):
        # Test the creation of a new friendship to ensure no duplication
        unique_user = self.create_unique_user('uniqueuser1')
        url = reverse('UserManagement:friendship-list')
        data = {'user_to': unique_user.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Friendship.objects.filter(user_from=self.user, user_to=unique_user).count(), 1)

    def test_retrieve_friendship_detail(self):
        friendship = Friendship.objects.create(user_from=self.user, user_to=self.other_user, status='pending')
        url = reverse('UserManagement:friendship-detail', args=[friendship.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_friendship(self):
        friendship = Friendship.objects.create(user_from=self.user, user_to=self.other_user, status='pending')
        url = reverse('UserManagement:friendship-detail', args=[friendship.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Friendship.objects.filter(id=friendship.id).count(), 0)

    def test_list_friendship_requests(self):
        Friendship.objects.create(user_from=self.user, user_to=self.other_user, status='pending')
        url = reverse('UserManagement:friendship-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_duplicate_friendship_request(self):
        Friendship.objects.create(user_from=self.user, user_to=self.other_user, status='pending')
        url = reverse('UserManagement:friendship-list')
        data = {'user_to': self.other_user.id}
        response = self.client.post(url, data)
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_friendship_unauthorized(self):
        friendship = Friendship.objects.create(user_from=self.user, user_to=self.other_user, status='pending')
        self.client.force_authenticate(user=self.create_unique_user('unauthorizeduser'))
        url = reverse('UserManagement:friendship-detail', args=[friendship.id])
        response = self.client.patch(url, {'status': 'accepted'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_friendship_requests_for_user(self):
        Friendship.objects.create(user_from=self.user, user_to=self.other_user, status='pending')
        url = reverse('UserManagement:friendship-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_friendship_with_nonexistent_user(self):
        url = reverse('UserManagement:friendship-list')
        data = {'user_to': 999999}  # Assuming no user with this ID exists
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accept_friendship_request(self):
        friendship = Friendship.objects.create(user_from=self.user, user_to=self.other_user, status='pending')
        self.client.force_authenticate(user=self.other_user)
        url = reverse('UserManagement:friendship-accept', args=[friendship.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        friendship.refresh_from_db()
        self.assertEqual(friendship.status, 'accepted')

    def test_reject_friendship_request(self):
        friendship = Friendship.objects.create(user_from=self.user, user_to=self.other_user, status='pending')
        self.client.force_authenticate(user=self.other_user)
        url = reverse('UserManagement:friendship-reject', args=[friendship.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        friendship.refresh_from_db()
        self.assertEqual(friendship.status, 'rejected')
