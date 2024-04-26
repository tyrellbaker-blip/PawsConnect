from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PostViewSet, CommentViewSet, LikeViewSet

router = DefaultRouter()
router.register('posts', PostViewSet, basename='post')
router.register('comments', CommentViewSet, basename='comment')
router.register('likes', LikeViewSet, basename='like')

app_name = 'content'

urlpatterns = [
    path('', include(router.urls)),
]
