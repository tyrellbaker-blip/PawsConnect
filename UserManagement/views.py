from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import CustomLoginForm, UserRegistrationForm  # Make sure this import matches the location of your LoginForm


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


@login_required
def landing_page(request):
    return redirect('UserManagement:landing_page')


def home(request):
    return render(request, 'UserManagement/home.html', {'user': request.user})


def logout(request):
    return redirect('UserManagement:logout')


@login_required
def profile(request):
    return render(request, 'UserManagement/profile.html', {'user': request.user})
