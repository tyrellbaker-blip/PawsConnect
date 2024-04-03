import pandas as pd
from django.core.management.base import BaseCommand
from faker import Faker

from UserManagement.forms import UserRegistrationForm  # Adjust the import path


class Command(BaseCommand):
    help = 'Creates dummy users from an Excel file'

    def handle(self, *args, **kwargs):
        # Load the Excel file
        df = pd.read_excel('misc/DummyData.xlsx')

        fake = Faker()
        for _, row in df.iterrows():
            user_data = {
                'username': fake.user_name(),
                'email': fake.email(),
                'password1': 'TempPass!234',
                'password2': 'TempPass!234',
                'city': row['City'],
                'state': row['State'],
                'zip_code': str(row['Zip']),
                'preferred_language': 'en',
            }
            form = UserRegistrationForm(user_data)
            if form.is_valid():
                form.save()
            else:
                print(f"Failed to create user: {form.errors}")
