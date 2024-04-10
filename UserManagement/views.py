import logging

from allauth.account.views import LogoutView
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.gis.measure import D  # 'D' is used for distance measurements
from django.db import DatabaseError, IntegrityError
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.urls import reverse_lazy
from PetManagement.forms import PetForm
from PetManagement.models import Pet
from UserManagement.models import CustomUser
from .decorators import profile_completion_required
from .forms import CustomLoginForm, UserRegistrationForm, EditProfileForm, PetFormSet, UserCompletionForm
from .forms import PetForm  # Ensure this is correctly imported from your forms.py
from .forms import SearchForm
from .models import Photo
from .utils import set_profile_incomplete

# Authentication Views
logger = logging.getLogger(__name__)


def user_login(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            try:
                user = authenticate(request, username=username, password=password)
                if user:
                    login(request, user)
                    if user.profile_incomplete:
                        logger.debug("Redirecting user with incomplete profile to completion page")
                        return redirect('UserManagement:user_completion')
                    else:
                        logger.debug("Redirecting user with complete profile to profile page")
                        return redirect('UserManagement:profile')
                else:
                    form.add_error(None, "Invalid username or password.")
            except CustomUser.DoesNotExist:
                form.add_error(None, "User with that username does not exist.")
    else:
        form = CustomLoginForm()
    return render(request, 'UserManagement/login.html', {'form': form})


def home(request):
    if request.user.is_authenticated:
        return redirect('UserManagement:profile')  # Redirect to profile if logged in
    else:
        return render(request, 'UserManagement/home.html')


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST, request.FILES)
        pet_formset = PetFormSet(request.POST, request.FILES)

        if user_form.is_valid() and pet_formset.is_valid():
            try:
                user = user_form.save(commit=False)
                user.save()  # Geocoding handled by the signal
                pet_formset.instance = user
                pet_formset.save()
                set_profile_incomplete(user)
                login(request, user)
                return redirect('UserManagement:profile')
            except IntegrityError as e:
                logger.error("Integrity error during registration:", exc_info=True)
                messages.error(request, "Username or email already exists. Please choose another.")
            except DatabaseError as e:
                logger.error("Database error during registration:", exc_info=True)
                messages.error(request, "A database error occurred. Please try again later.")
            # Add error handling for pet creation here if needed
    else:
        user_form = UserRegistrationForm()
        pet_formset = PetFormSet()

    return render(request, 'UserManagement/register.html', {
        'user_form': user_form,
        'pet_formset': pet_formset
    })


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('UserManagement:login')

    def dispatch(self, request, *args, **kwargs):
        print("CustomLogoutView: Logging out user:", request.user)
        response = super().dispatch(request, *args, **kwargs)
        print("CustomLogoutView: User logged out.")
        return response


# Profile Management Views

@login_required
@profile_completion_required
def profile(request, slug):
    user = get_object_or_404(CustomUser, slug=slug)
    context = {
        'user': user,
        'username': user.username,
        'display_name': user.display_name,
        'profile_picture_url': user.get_profile_picture_url(),
        'location_string': user.get_full_location(),
        'about_me': user.about_me,
        'num_friends': user.num_friends,
        'pets': user.pets.all(),
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
            except (DatabaseError, IntegrityError) as e:
                logger.error("Error updating profile:", exc_info=True)
                messages.error(request,
                               "A database error occurred while updating your profile. Please try again later.")
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'UserManagement/edit_profile.html', {'form': form})


@login_required
def user_completion(request):
    if request.method == 'POST':
        form = UserCompletionForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.profile_incomplete = False
            user.save()
            messages.success(request, "Your profile is now complete!")
            return redirect('UserManagement:profile')
    else:
        # Initialize form with empty values for missing fields
        form = UserCompletionForm(instance=request.user)
    return render(request, 'UserManagement/user_completion.html', {'form': form})


# Search Views

def search(request):
    form = SearchForm(request.GET or None)
    context = {
        'form': form,
        'search_type': None,
        'results': None,
    }

    if form.is_valid():
        search_type = form.cleaned_data['type']
        context['search_type'] = search_type

        if search_type == 'user':
            try:
                users = CustomUser.objects.all()

                if form.cleaned_data.get('query'):
                    users = users.filter(Q(username__icontains=form.cleaned_data['query']) | Q(
                        display_name__icontains=form.cleaned_data['query']))

                if 'location_point' in form.cleaned_data and form.cleaned_data.get('range'):
                    user_location = form.cleaned_data.get('location_point')
                    search_distance = D(mi=int(form.cleaned_data['range']))
                    users = users.filter(location__distance_lte=(user_location, search_distance))

                context['results'] = users
            except Exception as e:
                logger.error("Error during user search:", exc_info=True)
                messages.error(request, "An error occurred during the search. Please try again later.")

        elif search_type == 'pet':
            try:
                pets_query = Pet.objects.all()

                if form.cleaned_data.get('pet_id'):
                    pets_query = pets_query.filter(id__icontains=form.cleaned_data['pet_id'])

                if form.cleaned_data.get('pet_name'):
                    pets_query = pets_query.filter(name__icontains=form.cleaned_data['pet_name'])

                if 'location_point' in form.cleaned_data and form.cleaned_data.get('range'):
                    location_point = form.cleaned_data['location_point']
                    search_distance = D(mi=int(form.cleaned_data['range']))
                    pets_query = pets_query.filter(owner__location__distance_lte=(location_point, search_distance))

                context['results'] = pets_query
            except Exception as e:
                logger.error("Error during pet search:", exc_info=True)
                messages.error(request, "An error occurred during the search. Please try again later.")

    return render(request, 'UserManagement/search.html', context)


# Additional Views (photos, friends, pets)

@login_required
def photos(request):
    user_photos = Photo.objects.filter(user=request.user)
    return render(request, 'UserManagement/photos.html', {'user_photos': user_photos})


@login_required
def friends(request):
    user_friends = request.user.friends.all()
    return render(request, 'UserManagement/friends.html', {'user_friends': user_friends})


@login_required
def pets(request):
    user_pets = Pet.objects.filter(owner=request.user)
    return render(request, 'UserManagement/pets.html', {'user_pets': user_pets})


# UserManagement/views.py


@login_required
def manage_pets(request):
    PetFormSet = modelformset_factory(Pet, form=PetForm, extra=1, can_delete=True)
    if request.method == 'POST':
        formset = PetFormSet(request.POST, request.FILES, queryset=Pet.objects.filter(owner=request.user))
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.owner = request.user
                instance.save()
            # Handle deletions
            for obj in formset.deleted_objects:
                obj.delete()
            return redirect('your_redirect_url')
    else:
        formset = PetFormSet(queryset=Pet.objects.filter(owner=request.user))
    return render(request, 'your_template.html', {'formset': formset})


@login_required
def add_pet(request):
    if request.method == 'POST':
        # Include request.FILES to handle file uploads correctly
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            new_pet = form.save(commit=False)
            new_pet.owner = request.user
            new_pet.save()
            # This message format dynamically inserts the pet's name
            return JsonResponse({'success': True, 'message': f'{new_pet.name} successfully added.'})
        else:
            # If the form is not valid, return the form errors
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
    else:
        # If the request method is not POST, indicate an invalid request
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=405)


@login_required
def delete_pet(request):
    if request.method == 'POST' and 'pet_id' in request.POST:
        try:
            pet = Pet.objects.get(id=request.POST['pet_id'], owner=request.user)
            pet_name = pet.name
            pet.delete()
            return JsonResponse({'success': True, 'message': f'{pet_name} successfully deleted.'})
        except Pet.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Pet not found'}, status=404)
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=405)

def pet_profile(request, slug):  # Use slug as parameter
    pet = get_object_or_404(Pet, slug=slug)