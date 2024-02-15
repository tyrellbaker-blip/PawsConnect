from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, UserRegistrationForm  # Make sure this import matches the location of your LoginForm


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('landing_page')  # Redirect to the landing page upon successful login
            else:
                # Add a non-field error to the form for login failure
                form.add_error(None, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, 'UserManagement/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in
            return redirect('UserManagement/landing_page.html')  # Redirect to the home page
    else:
        form = UserRegistrationForm()
    return render(request, 'UserManagement/register.html', {'form': form})


@login_required
def landing_page(request):
    return render(request, 'UserManagement/landing_page.html', {'user': request.user})


def home(request):
    return render(request, 'UserManagement/home.html', {'user': request.user})
