import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from PetManagement.models import Pet
from PawsConnect.settings import MEDIA_ROOT
User = get_user_model()


class PetAJAXTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.client = Client()
        self.client.login(username='testuser', password='password')

    def test_add_pet(self):
        response = self.client.post(reverse('UserManagement:add_pet'), {
            'name': 'Buddy',
            'pet_type': 'dog',
            'age': 3,
            # Ensure all required fields are included and correctly formatted
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        if response.status_code != 200:
            print("Form errors:", response.json()['errors'])

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Pet.objects.filter(name='Buddy').exists())

    def test_delete_pet(self):
        pet = Pet.objects.create(owner=self.user, name='Buddy', pet_type='Dog', age=3)
        response = self.client.post(reverse('UserManagement:delete_pet'), {
            'pet_id': pet.id,
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Pet.objects.filter(id=pet.id).exists())

    def test_add_pet_with_image(self):

        # Setup URL and form data as before
        url = reverse('UserManagement:add_pet')
        data = {
            'name': 'Test Pet',
            'pet_type': 'dog',  # Assuming lowercase conversion is handled in the form/view
            'age': 5,
            'description': 'A friendly dog.'
        }

        # Add the image to the form data
        with open('media/test_images/test.jpg', 'rb') as img:
            data['profile_picture'] = img
            response = self.client.post(url, data, follow=True)

        # Assertions for status code and potentially response content here
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(response_json.get('message'), f"{data.get('name')} successfully added.")

        # Now check if the Pet instance has been created and has the image associated
        pet = Pet.objects.get(name='Test Pet')  # Adjust the query as necessary
        self.assertTrue(pet.profile_picture)  # Check if there's a profile picture

        # Optionally, check if the file physically exists at the location
        # Note: Django's default storage saves files under the MEDIA_ROOT setting
        file_path = os.path.join(MEDIA_ROOT, pet.profile_picture.name)
        self.assertTrue(os.path.exists(file_path))

        # Cleanup: Remove the uploaded file after the test (if necessary)
        if os.path.exists(file_path):
            os.remove(file_path)
