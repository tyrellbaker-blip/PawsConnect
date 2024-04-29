import logging

from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, mixins, serializers
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from Content.models import Post
from Content.serializers import PostSerializer
from PetManagement.models import Pet
from PetManagement.serializers import PetSerializer
from UserManagement.models import CustomUser, Photo, Friendship
from .serializers import CustomUserSerializer, FriendshipSerializer, PhotoSerializer, CustomLoginSerializer
from .utils import search_users, search_pets, create_user

logger = logging.getLogger(__name__)


def check_profile_completeness(user):
    required_fields = ['first_name', 'last_name', 'profile_picture', 'location', 'city', 'state', 'zip_code',
                       'has_pets', 'about_me']
    for field in required_fields:
        if getattr(user, field, None) is None:
            return False
    return True


class RegistrationViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        pets = self.request.data.get('pets')
        user, slug = create_user(
            CustomUser,
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            pets=pets,
            **{k: v for k, v in serializer.validated_data.items() if k not in ['email', 'password']}
        )
        token, created = Token.objects.get_or_create(user=user)
        self.request.data['token'] = token.key
        self.request.data['slug'] = slug


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def perform_update(self, serializer):
        user = serializer.save()
        user.profile_incomplete = not check_profile_completeness(user)  # Use the global function
        user.save()

    def get_queryset(self):
        return CustomUser.objects.filter(is_active=True)


class LoginViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = CustomLoginSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                logger.info(f"User authenticated successfully: {user.username}")
                token, created = Token.objects.get_or_create(user=user)
                redirect_url = 'user_completion' if user.profile_incomplete else f'profile/{user.slug}'
                response_data = {
                    'redirect_url': redirect_url,
                    'token': token.key
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({'error': "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        logger.info(f"Logging out user: {request.user}")
        request.user.auth_token.delete()
        return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)


class AddPetViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = PetSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProfileViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        pets = user.pets.all()
        pet_serializer = PetSerializer(pets, many=True)
        posts = Post.objects.filter(user=user)

        user_data = {
            'display_name': user.display_name,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'location': user.location,
            'about_me': user.about_me,
            'city': user.city,
            'state': user.state,
            'zip_code': user.zip_code,
            'has_pets': user.has_pets,
            'preferred_language': user.preferred_language,
            'profile_picture': user.profile_picture.url if user.profile_picture else None,
        }

        post_serializer = PostSerializer(posts, many=True)

        context = {
            'user': user_data,
            'posts': post_serializer.data,
            'pets': pet_serializer.data,
        }

        return Response(context, status=status.HTTP_200_OK)


class EditProfileViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCompletionViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            instance.set_profile_incomplete()
            return Response({'message': 'User profile completed successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SearchViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        search_type = request.query_params.get('type')
        query = request.query_params.get('query')
        location_point = request.query_params.get('location_point')
        search_range = request.query_params.get('range')
        pet_id = request.query_params.get('pet_id')
        pet_name = request.query_params.get('pet_name')

        context = {
            'search_type': search_type,
            'results': None,
        }

        if search_type == 'user':
            users = search_users(
                query=query,
                location_point=location_point,
                search_range=search_range
            )
            context['results'] = CustomUserSerializer(users, many=True).data
        elif search_type == 'pet':
            pets = search_pets(
                pet_id=pet_id,
                name=pet_name
            )
            context['results'] = PetSerializer(pets, many=True).data

        return Response(context, status=status.HTTP_200_OK)


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Photo.objects.filter(user=self.request.user)


class FriendsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.friends.all()


class PetsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Pet.objects.filter(owner=self.request.user)


class FriendshipViewSet(viewsets.ModelViewSet):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user_from = self.request.user
        user_to = serializer.validated_data.get('user_to')
        if user_from == user_to:
            raise serializers.ValidationError("You cannot send a friendship request to yourself.")
        if Friendship.objects.filter(user_from=user_from, user_to=user_to).exists():
            raise serializers.ValidationError('A friendship request already exists between these users.')
        serializer.save(user_from=user_from)

    @action(detail=True, methods=['post'], name='Accept Friendship', permission_classes=[IsAuthenticated])
    def accept(self, request, pk=None):
        friendship = self.get_object()
        if friendship.user_to == request.user and friendship.status == 'pending':
            friendship.status = 'accepted'
            friendship.save(update_fields=['status'])
            return Response({'status': 'accepted'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Unauthorized or invalid state'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], name='Reject Friendship', permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        friendship = self.get_object()
        if friendship.user_to == request.user and friendship.status == 'pending':
            friendship.status = 'rejected'
            friendship.save(update_fields=['status'])
            return Response({'status': 'rejected'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Unauthorized or invalid state'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        friendship = self.get_object()
        if friendship.user_from == request.user or friendship.user_to == request.user:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({'error': 'You do not have permission to delete this friendship.'},
                            status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        friendship = self.get_object()
        if not (friendship.user_from == request.user or friendship.user_to == request.user):
            return Response({'error': 'You do not have permission to modify this friendship.'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)


class DeletePetViewSet(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Pet.objects.all()
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        pet = get_object_or_404(Pet, id=kwargs['pk'], owner=request.user)
        pet.delete()
        return Response({'success': True, 'message': 'Pet successfully deleted.'}, status=status.HTTP_200_OK)


class FeedPagination(PageNumberPagination):
    page_size = 10  # Number of posts per page
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProfileFeedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = FeedPagination

    def get_queryset(self):
        user = get_object_or_404(CustomUser, slug=self.kwargs['slug'])
        friends = Friendship.objects.filter(user_from=user, status='accepted').values_list('user_to', flat=True)
        feed = Post.objects.filter(user__in=friends, visibility=Post.VisibilityChoices.FRIENDS_ONLY)
        feed |= Post.objects.filter(user=user)
        feed |= Post.objects.filter(visibility=Post.VisibilityChoices.PUBLIC)
        return feed.distinct().order_by('-timestamp')
