import pandas as pd
from faker import Faker
from geopy.geocoders import Nominatim

from UserManagement.forms import UserRegistrationForm  #


def get_lat_lon_from_address(city, state, zip_code):
    geolocator = Nominatim(user_agent="your_app_or_company_name")
    # Combine city, state, and zip for the query
    location = geolocator.geocode(f"{city}, {state}, {zip_code}")
    if location:
        return location.latitude, location.longitude
    else:
        return None, None


# Correctly load the DataFrame with appropriate headers

