from django.test import TestCase

from PetManagement.models import Pet
from UserManagement.models import CustomUser


class SlugTest(TestCase):
    def setUp(self):
        # Create test users and pets
        self.user1 = CustomUser.objects.create_user(username='john_doe', first_name='John', last_name='Doe')
        self.user2 = CustomUser.objects.create_user(username='jane_doe', first_name='Jane', last_name='Doe')
        self.pet1 = Pet.objects.create(name='Rex', owner=self.user1)
        self.pet2 = Pet.objects.create(name='Buddy', owner=self.user2)


    def test_user_slug_generation(self):
        self.assertEqual(self.user1.slug, 'john_doe')
        self.assertEqual(self.user2.slug, 'jane_doe')


    def test_pet_slug_generation(self):
        self.assertEqual(self.pet1.slug, 'rex')
        self.assertEqual(self.pet2.slug, 'buddy')


    def test_user_slug_update(self):
        self.user1.username = 'john_d'
        self.user1.save()
        self.assertEqual(self.user1.slug, 'john_d')  # Slug should be updated


    def test_pet_slug_update(self):
        self.pet1.name = 'Max'
        self.pet1.save()
        self.assertEqual(self.pet1.slug, 'max')  # Slug should be updated


    def test_user_get_absolute_url(self):
        self.assertEqual(self.user1.get_absolute_url(), '/user/profile/john_doe/')


    def test_pet_get_absolute_url(self):
        self.assertEqual(self.pet1.get_absolute_url(), '/pet/pet/rex/')  # Assuming your URL pattern
