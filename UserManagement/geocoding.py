import requests
from django.contrib.gis.geos import Point

from PawsConnect import settings


def geocode_address(city, state, zip_code):
    address = f"{city}, {state}, {zip_code}"
    response = requests.get(
        f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={settings.GOOGLE_MAPS_API_KEY}"
    )
    location_data = response.json()
    latitude = location_data['results'][0]['geometry']['location']['lat']
    longitude = location_data['results'][0]['geometry']['location']['lng']
    return Point(longitude, latitude, srid=4326)
