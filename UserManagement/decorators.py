from django.shortcuts import redirect

def profile_completion_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.profile_incomplete:
            return redirect('UserManagement:user_completion')
        return view_func(request, *args, **kwargs)
    return _wrapped_view