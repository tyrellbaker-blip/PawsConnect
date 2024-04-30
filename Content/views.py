# Content/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from Content.models import Post, Comment, Like
from Content.serializers import PostSerializer, CommentSerializer, LikeSerializer

from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from Content.models import Post, Comment, Like
from Content.serializers import PostSerializer, CommentSerializer, LikeSerializer
from UserManagement.models import Friendship
from Content.permissions import IsFriendOrOwner


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsFriendOrOwner]

    def get_queryset(self):
        user = self.request.user
        queryset = Post.objects.filter(visibility=Post.VisibilityChoices.PUBLIC)
        if user.is_authenticated:
            friends = Friendship.objects.filter(user_from=user, status='accepted').values_list('user_to', flat=True)
            queryset |= Post.objects.filter(user__in=friends, visibility=Post.VisibilityChoices.FRIENDS_ONLY)
            queryset |= Post.objects.filter(user=user)
        return queryset.distinct().order_by('-timestamp')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsFriendOrOwner]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
