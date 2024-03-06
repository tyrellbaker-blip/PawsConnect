from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from SocialInteraction.models import Friendship
from django.core.serializers import serialize
import json

def user_login(request):
    print("Login view function called")
    if request.method == 'POST':
        print("POST request on login")
        print("POST data:", request.POST)
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            print("Form is valid")
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            print('Authenticated user:', user)
            if user:
                login(request, user)
                print('Login successful')
                return redirect('UserManagement:home')  # Redirect to a home page or specified url
            else:
                print("User authentication failed")
                form.add_error(None, "Invalid username or password")
        else:
            print("Invalid form")
            print("Form errors:", form.errors)
    else:
        print("Non-POST request on login")
        form = CustomLoginForm()
    return render(request, 'UserManagement/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in
            return redirect('UserManagement:landing_page')  # Redirect to the home page
    else:
        form = UserRegistrationForm()
    return render(request, 'UserManagement/register.html', {'form': form})

def network(request):
    friendships_qs = Friendship.objects.filter(is_active=True).values('from_user_id', 'to_user_id')
    friendships_json = json.dumps(list(friendships_qs))
    return render(request, 'UserManagement/network.html', {'friendships_json': friendships_json})



@login_required
def landing_page(request):
    return redirect('UserManagement:landing_page')


def index(request):
    return render(request, 'UserManagement/index.html', {'user': request.user})


def home(request):
    return render(request, 'UserManagement/home.html', {'user': request.user})


def logout(request):
    return redirect('UserManagement:logout')

#login required
def profile(request):
    return render(request, 'UserManagement/profile.html', {'user': request.user})

#login required
def connections(request):
    return render(request, 'UserManagement/connections.html', {'user': request.user})

