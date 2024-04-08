from allauth.account.views import LogoutView
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.gis.measure import D  # 'D' is used for distance measurements
from django.db import DatabaseError, IntegrityError
from django.db.models import Q
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy

from PetManagement.models import Pet
from .forms import CustomLoginForm, UserRegistrationForm, \
    EditProfileForm, PetFormSet, logger  # Make sure this import matches the location of your LoginForm
from .forms import SearchForm
from .models import CustomUser, Photo


def user_login(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('UserManagement:profile')
            else:
                # Display error message for failed authentication
                form.add_error(None, "Invalid username or password.")
    else:
        form = CustomLoginForm()
    return render(request, 'UserManagement/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST, request.FILES)
        pet_formset = PetFormSet(request.POST, request.FILES)

        if user_form.is_valid() and pet_formset.is_valid():
            try:
                user = user_form.save(commit=False)
                user.save()  # Save the user to the database
                pet_formset.instance = user  # Associate the pets with the user
                pet_formset.save()  # Save the pet data to the database

                login(request, user)  # Log the user in
                return redirect('UserManagement:profile')  # Redirect to the user's profile page
            except Exception as e:
                # Handle potential database errors during user or pet creation
                logger.error("Error during registration:", exc_info=True)  # Log the error for debugging
                # Display a generic error message to the user
                messages.error(request, "An error occurred during registration. Please try again later.")
    else:
        user_form = UserRegistrationForm()
        pet_formset = PetFormSet()

    return render(request, 'UserManagement/register.html', {
        'user_form': user_form,
        'pet_formset': pet_formset
    })


def home(request):
    if request.user.is_authenticated:
        return redirect('UserManagement:profile')  # Redirect logged-in users to their profile
    else:
        return render(request, 'UserManagement/home.html')


@login_required
def profile(request):
    user: 'CustomUser' = request.user  # Get the currently logged-in user

    # Prepare context data for the template
    context = {
        'user': user,
        'username': user.username,
        'display_name': user.display_name,
        'profile_picture_url': user.get_profile_picture_url(),
        'location_string': user.get_full_location(),
        'about_me': user.about_me,
        'num_friends': user.num_friends,
        'pets': user.pets.all(),
        # ... add other context data as needed ...
    }
    return render(request, 'UserManagement/profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Your profile has been updated successfully.")
                return redirect('UserManagement:profile')
            except (DatabaseError, IntegrityError) as e:  # Catch specific database errors
                logger.error("Error updating profile:", exc_info=True)
                messages.error(request,
                               "A database error occurred while updating your profile. Please try again later.")
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'UserManagement/edit_profile.html', {'form': form})


def search(request):
    form = SearchForm(request.GET or None)
    context = {
        'form': form,
        'search_type': None,  # Default to None, will be updated if a search is performed
        'results': None,  # Default to None, will hold either user or pet results
    }

    if form.is_valid():
        search_type = form.cleaned_data['type']
        context['search_type'] = search_type  # Update context with the type of search

        if search_type == 'user':
            users = CustomUser.objects.all()

            if form.cleaned_data.get('query'):
                users = users.filter(Q(username__icontains=form.cleaned_data['query']) | Q(
                    display_name__icontains=form.cleaned_data['query']))

            if 'location_point' in form.cleaned_data and form.cleaned_data.get('range'):
                user_location = form.cleaned_data.get('location_point')
                search_distance = D(mi=int(form.cleaned_data['range']))
                users = users.filter(location__distance_lte=(user_location, search_distance))

            context['results'] = users  # Update context with the user results

        elif search_type == 'pet':
            pets_query = Pet.objects.all()

            if form.cleaned_data.get('pet_id'):
                pets_query = pets_query.filter(id__icontains=form.cleaned_data['pet_id'])

            if form.cleaned_data.get('pet_name'):
                pets_query = pets_query.filter(name__icontains=form.cleaned_data['pet_name'])

            if 'location_point' in form.cleaned_data and form.cleaned_data.get('range'):
                location_point = form.cleaned_data['location_point']
                search_distance = D(mi=int(form.cleaned_data['range']))
                pets_query = pets_query.filter(owner__location__distance_lte=(location_point, search_distance))

            context['results'] = pets_query  # Update context with the pet results

    return render(request, 'UserManagement/search.html', context)


@login_required
def photos(request):
    user_photos = Photo.objects.filter(user=request.user)  # Filter photos by the logged-in user
    return render(request, 'UserManagement/photos.html', {'user_photos': user_photos})


@login_required
def friends(request):
    user_friends = request.user.friends.all()  # Assuming a 'friends' many-to-many field on your user model
    return render(request, 'UserManagement/friends.html', {'user_friends': user_friends})


@login_required
def pets(request):
    user_pets = Pet.objects.filter(owner=request.user)  # Assuming a 'owner' ForeignKey to CustomUser on your Pet model
    return render(request, 'UserManagement/pets.html', {'user_pets': user_pets})


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('UserManagement:login')

    def dispatch(self, request, *args, **kwargs):
        print("CustomLogoutView: Logging out user:", request.user)
        response = super().dispatch(request, *args, **kwargs)
        print("CustomLogoutView: User logged out.")
        return response
