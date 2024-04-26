from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegistrationViewSet,
    CustomUserViewSet,
    LoginViewSet,
    AddPetViewSet,
    LogoutViewSet,
    ProfileViewSet,
    EditProfileViewSet,
    EditPetProfileViewSet,
    UserCompletionViewSet,
    SearchViewSet,
    PhotoViewSet,
    FriendsViewSet,
    PetsViewSet,
    FriendshipViewSet,
    DeletePetViewSet,
    ProfileFeedViewSet,
)

router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='user')
router.register('register', RegistrationViewSet, basename='register')
router.register('logout', LogoutViewSet, basename='logout')
router.register('add-pet', AddPetViewSet, basename='add-pet')
router.register('profile', ProfileViewSet, basename='profile')
router.register('edit-profile', EditProfileViewSet, basename='edit-profile')
router.register('edit-pet', EditPetProfileViewSet, basename='edit-pet')
router.register('search', SearchViewSet, basename='search')
router.register('photos', PhotoViewSet, basename='photo')
router.register('friends', FriendsViewSet, basename='friend')
router.register('pets', PetsViewSet, basename='pet')
router.register('friendships', FriendshipViewSet, basename='friendship')
router.register('delete-pet', DeletePetViewSet, basename='delete-pet')
router.register('feed', ProfileFeedViewSet, basename='feed')

app_name = 'UserManagement'
urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginViewSet.as_view({'post': 'create'}), name='login'),
    path('user-completion/<slug:slug>/', UserCompletionViewSet.as_view({'put': 'update'}), name='user-completion'),
]