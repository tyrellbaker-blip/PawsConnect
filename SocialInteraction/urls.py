from django.urls import path
from . import views

urlpatterns = [
    # Posts
    path('posts/', views.PostListView.as_view(), name='post-list'),
    path('post/new/', views.PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    # Comments
    path('post/<int:pk>/comment/', views.CommentCreateView.as_view(), name='comment-create'),
]