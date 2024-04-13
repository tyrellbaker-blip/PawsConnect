import logging

from allauth.account.views import LogoutView
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory, inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse

from PetManagement.models import Pet, PetProfile
from UserManagement.models import CustomUser
from .decorators import profile_completion_required
from .forms import CustomLoginForm, EditProfileForm, UserCompletionForm, PetFormSet
from .forms import SearchForm
from .models import Photo

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
                    print("User authenticated successfully:", user.username)  # Print username
                    if user.is_profile_complete:
                        print("Redirecting to profile completion page")
                        return redirect('UserManagement:user_completion')
                    else:
                        print("Redirecting to profile page:", user.slug)  # Print slug
                        return redirect('UserManagement:profile', slug=user.slug)
                else:
                    form.add_error(None, "Invalid username or password.")
            except CustomUser.DoesNotExist:
                form.add_error(None, "User with that username does not exist.")
    else:
        form = CustomLoginForm()
    return render(request, 'UserManagement/login.html', {'form': form})


def home(request):
    if request.user.is_authenticated:
        return redirect('UserManagement:profile', slug=request.user.slug)
    else:
        return render(request, 'UserManagement/home.html')


from .forms import PetForm

from django.contrib import messages
from django.shortcuts import render, redirect
from django.db import IntegrityError, DatabaseError

from .forms import UserRegistrationForm


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST, request.FILES)
        pet_formset = PetFormSet(request.POST, request.FILES)
        if user_form.is_valid() and pet_formset.is_valid():
            try:
                user = user_form.save(commit=False)  # Create user object but don't save yet
                user.save()  # Now save the user (geocoding handled by the signal)

                # Save pet profiles and associate them with the user
                for form in pet_formset:
                    if form.is_valid():
                        pet = form.save(commit=False)
                        pet.owner = user
                        pet.save()
                        user.pets.add(pet)
                        # Create and associate the PetProfile
                        PetProfile.objects.create(pet=pet)

                # Login the newly registered user
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('UserManagement:profile', slug=user.slug)

            except IntegrityError as e:
                messages.error(request, "Username or email already exists. Please choose another.")
            except DatabaseError as e:
                messages.error(request, "A database error occurred. Please try again later.")
            # Add error handling for pet creation here if needed

    else:
        user_form = UserRegistrationForm()
        pet_formset = PetFormSet()

    return render(request, 'UserManagement/register.html', {
        'user_form': user_form,
        'pet_formset': pet_formset
    })


@login_required
def add_pet(request):
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner_id = request.user.id
            pet.save()
            request.user.pets.add(pet)

            # Create and associate the PetProfile
            PetProfile.objects.create(pet=pet)

            messages.success(request, "Pet added successfully!")
            return redirect('UserManagement:pets')
    else:
        form = PetForm()
    return render(request, 'add_pet.html', {'form': form})


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('UserManagement:login')

    def dispatch(self, request, *args, **kwargs):
        print("CustomLogoutView: Logging out user:", request.user)
        response = super().dispatch(request, *args, **kwargs)
        print("CustomLogoutView: User logged out.")
        return response


@login_required
@profile_completion_required
def profile(request, slug):
    from Content.models import Post  # Import locally
    user = get_object_or_404(CustomUser, slug=slug)
    posts = Post.objects.filter(user=user)

    pet_data = []
    for pet in user.pets.all():
        pet_info = {
            'profile_picture_url': pet.profile.profile_picture.url if pet.profile.profile_picture else None,
            'profile_url': reverse('PetManagement:pet_profile', kwargs={'slug': pet.slug}),
            'name': pet.name,
            'age': pet.age,
            'breed': pet.breed,
            'about_me': pet.profile.description,  # Assuming 'description' is the "about me" field
        }
        pet_data.append(pet_info)

    context = {
        'user': {
            'display_name': user.display_name,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'location': user.location,
            'about_me': user.profile.about_me,  # Include "about me" for user
        },
        'posts': [
            {
                'content': post.content,
                'timestamp': post.timestamp,
                # ... other post fields as needed ...
            } for post in posts
        ],
        'pet_data': pet_data,
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
                return redirect('UserManagement:profile', slug=request.user.slug)
            except (DatabaseError, IntegrityError) as e:
                logger.error("Error updating profile:", exc_info=True)
                messages.error(request,
                               "A database error occurred while updating your profile. Please try again later.")
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'UserManagement/edit_profile.html', {'form': form})


@login_required
def edit_pet_profile(request, pet_slug):
    pet = get_object_or_404(Pet, slug=pet_slug, owner=request.user)
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(request, "Pet profile updated successfully.")
            return redirect('UserManagement:pets')
    else:
        form = PetForm(instance=pet)
    return render(request, 'edit_pet_profile.html', {'form': form, 'pet': pet})


@login_required
def user_completion(request):
    if request.method == 'POST':
        form = UserCompletionForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile is now complete!")
            return redirect('UserManagement:profile', slug=request.user.slug)
    else:
        form = UserCompletionForm(instance=request.user)
    return render(request, 'UserManagement/user_completion.html', {'form': form})


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
            users = CustomUser.objects.search(
                query=form.cleaned_data['query'],
                location_point=form.cleaned_data.get('location_point', None),
                search_range=form.cleaned_data.get('range', None)
            )
            context['results'] = users
        elif search_type == 'pet':
            pets = Pet.objects.search(
                pet_id=form.cleaned_data.get('pet_id', None),
                name=form.cleaned_data.get('pet_name', None)
            )
            context['results'] = pets
    return render(request, 'UserManagement/search.html', context)


@login_required
def photos(request):
    user_photos = Photo.objects.filter(user=request.user)
    return render(request, 'UserManagement/photos.html', {'user_photos': user_photos})


@login_required
def friends(request):
    user_friends = request.friends.all()
    return render(request, 'UserManagement/friends.html', {'user_friends': user_friends})


@login_required
def pets(request):
    user_pets = Pet.objects.filter(owner=request.user)
    return render(request, 'UserManagement/pets.html', {'user_pets': user_pets})


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
            for obj in formset.deleted_objects:
                obj.delete()
            return redirect('UserManagement:pets')
        else:
            formset = PetFormSet(queryset=Pet.objects.filter(owner=request.user))
            return render(request, 'UserManagement/manage_pets.html', {'formset': formset})


def get_pet_formset():
    from UserManagement.models import CustomUser  # Import locally
    return inlineformset_factory(
        CustomUser, Pet, form=PetForm,
        fields=['name', 'pet_type', 'age', 'profile_picture'], extra=1, can_delete=True
    )


@login_required
def add_pet(request):
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            new_pet = form.save(commit=False)
            new_pet.owner = request.user
            new_pet.save()
            return JsonResponse({'success': True, 'message': f'{new_pet.name} successfully added.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
    else:
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


@login_required
def create_pet_profile(request):
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner_id = request.user.id  # Associate pet with the current user
            pet.save()
            request.user.pets.add(pet)  # Add pet to the user's pet list
            return redirect('UserManagement:pets')  # Redirect to the user's pet list
    else:
        form = PetForm()
    return render(request, 'create_pet_profile.html', {'form': form})
