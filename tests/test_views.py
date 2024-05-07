import pytest
from UserManagement.views import get_tokens_for_user
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model


@pytest.fixture
def user():
    User = get_user_model()
    # Corrected line is here. 'test' is username, 'test@test.com' is email and 'testpassword' is password.
    return User.objects.create_user(username='test', email='test@test.com', password='testpassword')


def test_get_tokens_for_user(user):
    tokens = get_tokens_for_user(user)

    assert 'refresh' in tokens
    assert 'access' in tokens

    refresh = RefreshToken(tokens['refresh'])
    assert str(refresh) == tokens['refresh']
    assert str(refresh.access_token) == tokens['access']