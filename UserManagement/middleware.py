# UserManagement/middleware.py
import logging

from django.shortcuts import redirect
from django.urls import reverse

logger = logging.getLogger(__name__)


class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        profile_completion_url = reverse('UserManagement:user_completion')

        # Skip middleware for profile completion requests
        if request.path == profile_completion_url:
            return response

        # If the user is authenticated and their profile is incomplete, redirect to profile completion
        if request.user.is_authenticated and hasattr(request.user, 'customuser'):
            if request.user.customuser.profile_incomplete:  # Replace with your actual condition
                logger.debug("Redirecting to profile completion page.")
                return redirect(profile_completion_url)

        return response
