import pandas as pd
from django.core.management.base import BaseCommand
from faker import Faker

from UserManagement.forms import UserRegistrationForm  # Adjust the import path


class Command(BaseCommand):
    help = 'Creates dummy users from an Excel file'

    def handle(self, *args, **kwargs):
        # Load the Excel file
        df = pd.read_excel('misc/DummyData.xlsx', header=1)  # Use header=0 if the first row is indeed the header

        fake = Faker()
        for _ in range(250):  # Number of users to create
            # Select a random row for city, state, zip
            row = df.sample(n=1).iloc[0]
            first_name = fake.first_name()
            last_name = fake.last_name()
            user_data = {
                'username': fake.user_name(),
                'email': fake.email(),
                'password1': 'TempPass!234',  # Make sure to use a secure password
                'password2': 'TempPass!234',  # Make sure to use a secure password
                'first_name': first_name,
                'last_name': last_name,
                'city': row['City'],
                'state': row['State'],
                'zip_code': str(row['Zip']),
                'preferred_language': 'en',  # Assuming default to English
            }

            # Create a form instance with POST data
            form = UserRegistrationForm(user_data)

            # Check if the form is valid
            if form.is_valid():
                # Save the new user from the form's data
                form.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully created user {first_name} {last_name}.'))
            else:
                # Print form errors if the user couldn't be created
                self.stdout.write(self.style.ERROR(f"Failed to create user {first_name} {last_name}: {form.errors}"))
