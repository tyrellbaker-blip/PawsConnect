from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse


class CustomAccountAdapter(DefaultAccountAdapter):
    def login(self, request, user):
        """
        This method is called when a user successfully logs in.
        We update the session to reflect whether the user's profile is complete.
        """
        super().login(request, user)  # Call the base implementation first to handle session setup
        # Store the profile completion status in the session
        request.session['has_completed_profile'] = user.has_completed_profile

    def get_login_redirect_url(self, request):
        """
        Determine the URL to redirect to after the login process has completed.
        This decision is based on whether the user's profile is complete.
        """
        user = request.user  # You might also use request.user instead of handling in the session
        if user.has_completed_profile:
            return reverse('user_profile', kwargs={'slug': user.slug})  # Redirect to user profile page
        else:
            return reverse('complete_profile')  # Redirect to profile completion page
