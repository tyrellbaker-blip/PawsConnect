from rest_framework import permissions

from UserManagement.models import Friendship


class IsFriendOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.visibility == 'Public':
            return True
        if request.user == obj.user:
            return True
        if obj.visibility == 'Friends Only':
            return Friendship.objects.filter(user_from=request.user, user_to=obj.user, status='accepted').exists()
        return False
