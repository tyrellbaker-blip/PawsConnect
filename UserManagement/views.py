from django.contrib.auth import authenticate, logout
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, Friendship
from .serializers import CustomUserSerializer, FriendshipSerializer, CompleteProfileSerializer
from .utils import search_users


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action in ['create', 'login', 'logout', 'check_session']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)
        tokens = get_tokens_for_user(user)
        return Response({
            'user': serializer.data,
            'id': user.id,
            'tokens': tokens
        }, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['POST'], detail=False, url_path='login')
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            tokens = get_tokens_for_user(user)
            return Response({
                'id': user.id,
                'username': user.username,
                'tokens': tokens,
                'message': "Login successful."

            }, status=status.HTTP_200_OK)
        return Response({'error': "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=False, url_path='logout')
    def logout(self, request):
        logout(request)
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path='check-session')
    def check_session(self, request):
        return Response({'is_authenticated': request.user.is_authenticated}, status=status.HTTP_200_OK)

    @action(methods=['PUT'], detail=True, url_path='update-profile')
    def update_profile(self, request, pk=None):
        user = self.get_object()
        serializer = CompleteProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'], detail=False, url_path='search')
    def search(self, request):
        query = request.query_params.get('query')
        city = request.query_params.get('city')
        state = request.query_params.get('state')
        zip_code = request.query_params.get('zip_code')
        location = request.query_params.get('location')
        range = request.query_params.get('range')

        users = search_users(query=query, location_point=location, search_range=range)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)


class FriendshipViewSet(viewsets.ModelViewSet):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user_from=self.request.user)
