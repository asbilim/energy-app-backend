from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admin users to edit objects,
    but allow all authenticated users to read.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated user (GET, HEAD or OPTIONS requests).
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions are only allowed to admin users.
        return request.user and request.user.is_staff 