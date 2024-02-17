from django.shortcuts import render
from django.views.generic import ListView, CreateView, DetailView
from .models import Post, Comment

class PostListView(ListView):
    model = Post
    template_name = 'SocialInteraction/home.html'  # Adjust if you're using a different name
    context_object_name = 'posts'
    ordering = ['-timestamp']

class PostDetailView(DetailView):
    model = Post
    template_name = 'SocialInteraction/post_detail.html'  # replace with your template

class PostCreateView(CreateView):
    model = Post
    fields = ['content', 'photo', 'visibility', 'tagged_pets']
    template_name = 'SocialInteraction/post_create.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class CommentCreateView(CreateView):
    model = Comment
    fields = ['content']
    template_name = 'SocialInteraction/comment_create.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.post = Post.objects.get(pk=self.kwargs['pk'])  # Adjust to fit your URL parameter if not 'pk'
        return super().form_valid(form)