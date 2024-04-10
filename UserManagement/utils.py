def set_profile_incomplete(user):  # No 'self' parameter
    required_fields = ['first_name', 'last_name', 'city', 'state', 'zip_code', 'profile_picture', 'has_pets']
    for field in required_fields:
        if not getattr(user, field):
            user.profile_incomplete = True
            user.save()
            return  # Exit the loop if any required field is missing

    user.profile_incomplete = False
    user.save()
