from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import resolve_url
from django.urls import reverse


class MyAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request):
        """
        Redirect users to the profile completion page if their profile is incomplete.
        """
        if request.user.is_authenticated and request.user.profile_incomplete:
            return reverse('UserManagement:user_completion')
        return super().get_login_redirect_url(request)