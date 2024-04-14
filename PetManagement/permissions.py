from rest_framework import permissions


class IsOwnerPermission(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to interact with it.

    This permission ensures that only the owner of a specific resource (e.g., a pet)
    can view, edit, or delete that resource. Non-owners will be denied access,
    effectively protecting the resource from unauthorized modifications or visibility.
    """

    def has_permission(self, request, view):
        """
        Assuming that the list view should be visible to any authenticated user,
        we are not implementing list-level permissions here. If you need to restrict
        list views as well, you might consider implementing additional logic here.
        """
        # If method is safe (GET, HEAD, OPTIONS), allow it as it will be further checked in `has_object_permission`
        # This allows listing items but item-specific permissions checked at the object level.
        if request.method in permissions.SAFE_METHODS:
            return True
        # For destructive actions, ensure the user is authenticated first.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check to only allow owners of an object to interact with it.

        This method is called once a detailed view of a single resource is accessed. Here, we check
        if the user making the request is the owner of the resource in question.
        """
        # Check if the method is a safe method, permission should be allowed if it's safe
        # and the object should be viewable by anyone if it's part of the application requirements.
        if request.method in permissions.SAFE_METHODS:
            return obj.owner == request.user
        return obj.owner == request.user
class IsOwnerOrRecipient(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.from_user == request.user or obj.to_user == request.user