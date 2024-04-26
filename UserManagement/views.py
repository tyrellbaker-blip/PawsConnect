import logging

from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, mixins, serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from Content.models import Post
from Content.serializers import PostSerializer
from PetManagement.models import Pet, PetProfile
from PetManagement.serializers import PetSerializer
from UserManagement.models import CustomUser
from .forms import CustomLoginForm, EditProfileForm, PetForm, UserCompletionForm
from .models import Photo, Friendship
from .serializers import CustomUserSerializer, FriendshipSerializer, PhotoSerializer
from .utils import search_pets, search_users

logger = logging.getLogger(__name__)


class RegistrationViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        user.set_profile_incomplete()  # Set profile_incomplete based on required fields
        # Perform any additional actions after user creation
        # For example, creating pet profiles, setting default values, etc.


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class LoginViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = CustomLoginForm.get_serializer()
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        form = CustomLoginForm(request.data)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
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
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        logger.info(f"Logging out user: {request.user}")
        request.user.auth_token.delete()
        return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)


class AddPetViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = PetForm
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        form = PetForm(request.data, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user
            pet.save()
            PetProfile.objects.create(pet=pet)
            return Response({'success': True, 'message': f'{pet.name} successfully added.'},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProfileViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        posts = Post.objects.filter(user=user)

        pet_data = []
        for pet in user.pets.all():
            pet_info = {
                'profile_picture_url': pet.profile.profile_picture.url if pet.profile.profile_picture else None,
                'profile_url': f'/pet/{pet.slug}/',
                'name': pet.name,
                'age': pet.age,
                'breed': pet.breed,
                'about_me': pet.profile.description,
            }
            pet_data.append(pet_info)

        context = {
            'user': {
                'display_name': user.display_name,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'location': user.location,
                'about_me': user.profile.about_me,
            },
            'posts': PostSerializer(posts, many=True).data,
            'pet_data': pet_data,
        }
        return Response(context, status=status.HTTP_200_OK)


class EditProfileViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = EditProfileForm
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        form = EditProfileForm(request.data, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return Response({'message': 'Profile updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class EditPetProfileViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Pet.objects.all()
    serializer_class = PetForm
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    def update(self, request, *args, **kwargs):
        pet = self.get_object()
        if pet.owner != request.user:
            return Response({'error': 'You do not have permission to edit this pet profile'},
                            status=status.HTTP_403_FORBIDDEN)

        form = PetForm(request.data, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            return Response({'message': 'Pet profile updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCompletionViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserCompletionForm
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'  # Change this to 'slug'

    def update(self, request, *args, **kwargs):
        instance = self.get_object() # Retrieve the instance from the queryset
        form = UserCompletionForm(request.data, request.FILES, instance=instance)

        if form.is_valid():
            form.save()
            return Response({'message': 'User profile completed successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class SearchViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        form_data = request.query_params
        search_type = form_data.get('type')
        context = {
            'search_type': search_type,
            'results': None,
        }

        if search_type == 'user':
            users = search_users(
                query=form_data.get('query'),
                location_point=form_data.get('location_point', None),
                search_range=form_data.get('range', None)
            )
            context['results'] = CustomUserSerializer(users, many=True).data
        elif search_type == 'pet':
            pets = search_pets(
                pet_id=form_data.get('pet_id', None),
                name=form_data.get('pet_name', None)
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
        return self.request.user.profile.friends.all()


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
