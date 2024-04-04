from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import CustomLoginForm, UserRegistrationForm, \
    EditProfileForm, PetFormSet  # Make sure this import matches the location of your LoginForm


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
                return redirect('UserManagement:profile')  # Redirect to a home page or specified url
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
        user_form = UserRegistrationForm(request.POST, request.FILES)
        pet_formset = PetFormSet(request.POST, request.FILES)

        if user_form.is_valid() and pet_formset.is_valid():
            user = user_form.save(commit=False)
            user.save()  # Save the user to the database
            pet_formset.instance = user  # Associate the pets with the user
            pet_formset.save()  # Save the pet data to the database

            login(request, user)  # Log the user in
            return redirect('UserManagement:profile')  # Redirect to the user's profile page
    else:
        user_form = UserRegistrationForm()
        pet_formset = PetFormSet()

    return render(request, 'UserManagement/register.html', {
        'user_form': user_form,
        'pet_formset': pet_formset
    })


@login_required
def landing_page(request):
    return redirect('UserManagement:landing_page')


def home(request):
    return render(request, 'UserManagement/home_.html', {'user': request.user})


def logout(request):
    return redirect('UserManagement:logout')


@login_required
def profile(request):
    return render(request, 'UserManagement/profile.html', {'user': request.user})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('UserManagement:profile')  # Redirect to the profile view
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})
