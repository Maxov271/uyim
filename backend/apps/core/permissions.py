from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrModerator(BasePermission):
    """Object-level: only the listing's owner/agency user or a moderator may write."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.role == "moderator" or user.is_staff:
            return True
        return getattr(obj, "owner_id", None) == user.id


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.role == "moderator" or user.is_staff))
