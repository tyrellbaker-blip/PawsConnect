from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RegistrationAPIView,
    CustomUserViewSet,
    LoginViewSet,
    AddPetViewSet,
    LogoutViewSet,
    ProfileViewSet,
    EditProfileViewSet,
    SearchViewSet,
    PhotoViewSet,
    FriendsViewSet,
    PetsViewSet,
    FriendshipViewSet,
    DeletePetViewSet,
    ProfileFeedViewSet,
    MemberHomePageView,
)

# Initialize the default router
router = DefaultRouter()

# Registering viewsets with the router
router.register('users', CustomUserViewSet, basename='user')
router.register('profile', ProfileViewSet, basename='profile')
router.register('login', LoginViewSet, basename='login')
router.register('logout', LogoutViewSet, basename='logout')
router.register('add-pet', AddPetViewSet, basename='add-pet')
router.register('edit-profile', EditProfileViewSet, basename='edit-profile')
router.register('search', SearchViewSet, basename='search')
router.register('photos', PhotoViewSet, basename='photo')
router.register('friends', FriendsViewSet, basename='friend')
router.register('pets', PetsViewSet, basename='pet')
router.register('friendships', FriendshipViewSet, basename='friendship')
router.register('delete-pet', DeletePetViewSet, basename='delete-pet')
router.register('feed', ProfileFeedViewSet, basename='feed')

# Application namespace
app_name = 'UserManagement'

# URL patterns
urlpatterns = [
    # Including all URLs from the router
    path('', include(router.urls)),

    # Direct path registration for the registration view
    path('register/', RegistrationAPIView.as_view(), name='register'),
    path('profile/<slug:slug>/', ProfileViewSet.as_view({'get': 'retrieve'}), name='profile'),
    # Direct path registration for the member home page view
    path('api/member-home-page/', MemberHomePageView.as_view(), name='member_home_page'),
]
