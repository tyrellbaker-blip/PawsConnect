import logging

from django.contrib.auth import authenticate, get_user_model
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import viewsets, status, mixins, serializers, filters, generics
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from Content.serializers import PostSerializer
from PetManagement.models import Pet
from PetManagement.serializers import PetSerializer
from UserManagement.models import CustomUser, Photo, Friendship
from .serializers import CustomUserSerializer, FriendshipSerializer, PhotoSerializer
from .utils import search_users, search_pets

logger = logging.getLogger(__name__)

User = get_user_model()



    # views.py


class RegistrationAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token, created = Token.objects.get_or_create(user=user)  # Get tokens using the helper function
        redirect_url = reverse('UserManagement:profile-detail', kwargs={'slug': user.slug})

        response_data = {
            'user': CustomUserSerializer(user).data,
            'tokens': token.key,
            'redirect_url': redirect_url,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class LoginViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user = authenticate(request, username=request.data.get('username'), password=request.data.get('password'))
        if user:
            token, created = Token.objects.get_or_create(user=user)
            redirect_url = reverse('UserManagement:profile', kwargs={'slug': user.slug})
            response_data = {
                'user_id': user.pk,
                'username': user.username,
                'slug': user.slug,
                'redirect_url': redirect_url,
                'token': token.key
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            logger.warning("Authentication failed for user %s.", request.data.get('username'))
            return Response({'error': "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()  # Include all users by default
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']

    def get_queryset(self):
        """
        Filter on 'is_active' only if explicitly requested, otherwise include all.
        """
        queryset = super().get_queryset()

        # Check for is_active filter in the query params
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active = is_active.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(is_active=is_active)

        # Geospatial filtering based on location and range
        longitude = self.request.query_params.get('longitude')
        latitude = self.request.query_params.get('latitude')
        range = self.request.query_params.get('range')  # range in kilometers

        if longitude and latitude and range:
            # Ensure the coordinates and range are appropriately converted to float
            user_location = Point(float(longitude), float(latitude), srid=4326)
            queryset = queryset.annotate(
                distance=Distance('location', user_location)
            ).filter(distance__lte=D(km=float(range)))

        return queryset


class LogoutViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        logger.info(f"Logging out user: {request.user}")
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
        posts = user.posts.all().order_by('-timestamp')

        user_data = {
            'slug': user.slug,
            'username': user.username,
            'display_name': user.display_name,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'about_me': user.about_me,
            'city': user.city,
            'state': user.state,
            'zip_code': user.zip_code,
            'has_pets': user.has_pets,
            'preferred_language': user.preferred_language,
            'profile_picture': user.profile_picture.url if user.profile_picture else None,
        }

        post_serializer = PostSerializer(posts, many=True, context={'request': request})

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


from Content.models import Post


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


class MemberHomePageView(generics.ListAPIView):
    queryset = Post.objects.all().order_by('-timestamp')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]




