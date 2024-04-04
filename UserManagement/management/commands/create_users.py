import json
import pandas as pd
from django.core.management.base import BaseCommand
from faker import Faker


class Command(BaseCommand):
    help = 'Creates dummy users from an Excel file'

    def handle(self, *args, **kwargs):
        from UserManagement.forms import UserRegistrationForm

        # Load the Excel file
        df = pd.read_excel('misc/DummyData.xlsx', header=1)

        fake = Faker()
        for _ in range(250):  # Adjust the range as needed
            row = df.sample(n=1).iloc[0]
            user_data = {
                'username': fake.user_name(),
                'email': fake.email(),
                'password1': 'TempPass!234',
                'password2': 'TempPass!234',
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'city': row['City'],
                'state': row['State'],
                'zip_code': str(row['Zip']),
                'preferred_language': 'en',
                'display_name': 'Display Name Placeholder',
                'profile_picture': None,
                'has_pets': False,
                'about_me': 'This is an autogenerated user.',
            }

            form = UserRegistrationForm(data=user_data)

            if form.is_valid():
                form.save()
                self.stdout.write(self.style.SUCCESS(
                    f"Successfully created user {user_data['first_name']} {user_data['last_name']}."))
            else:
                # Enhanced error logging
                errors = json.dumps(form.errors.as_json(), indent=4)
                self.stdout.write(self.style.ERROR(
                    f"Failed to create user {user_data['first_name']} {user_data['last_name']}: {errors}"))
