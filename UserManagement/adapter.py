from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import resolve_url
from django.urls import reverse


class CustomAccountAdapter(DefaultSocialAccountAdapter):
    def get_signup_redirect_url(self, request):
        user = request.user
        if user.profile_incomplete:
            return reverse('UserManagement:user_completion')
        else:
            return reverse('UserManagement:profile', kwargs={'slug': user.slug})

    def get_provider(self, request, provider):
        return super().get_provider(request, provider)