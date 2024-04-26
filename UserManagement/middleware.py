from django.shortcuts import redirect
from django.urls import reverse

class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Skip middleware for profile completion requests
        if request.path.startswith(reverse('UserManagement:user-completion', kwargs={'slug': 'default'})[:-8]):
            return response

        # If the user is authenticated and their profile is incomplete, redirect to profile completion
        if request.user.is_authenticated:
            if hasattr(request.user, 'customuser') and request.user.customuser.profile_incomplete:
                profile_completion_url = reverse('UserManagement:user-completion', kwargs={'slug': request.user.slug})
                return redirect(profile_completion_url)

        return response