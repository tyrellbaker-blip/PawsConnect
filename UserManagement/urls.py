from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    FriendshipViewSet,

    UserViewSet,

)
app_name = 'UserManagement'

# Initialize the default router
router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('friendships', FriendshipViewSet, basename='friendship')

urlpatterns = [
    path('api/', include(router.urls)),
    path('login/', UserViewSet.as_view({'post': 'login'}), name='login'),
    path('logout/', UserViewSet.as_view({'post': 'logout'}), name='logout'),
    path('check-session/', UserViewSet.as_view({'get': 'check_session'}), name='check_session'),
    path('update-profile/<int:pk>/', UserViewSet.as_view({'put': 'update_profile'}), name='update_profile'),
]
