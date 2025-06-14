from rest_framework.permissions import BasePermission, IsAuthenticated
from users.models import User

class IsParent(BasePermission):
    """
    Allows access only to users with the 'parent' role.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == User.ROLE_PARENT
        )

class IsChild(BasePermission):
    """
    Allows access only to users with the 'child' role.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == User.ROLE_CHILD
        )

class IsOwnerOfWallet(BasePermission):
    """
    Custom permission to only allow the parent owner of a wallet to see it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.parent == request.user

class IsFamilyMemberForTransaction(BasePermission):
    """
    Permission to check if the user is part of the family that owns the transaction.
    - A parent can see any transaction in their family wallet.
    - A child can only see transactions they are directly involved in.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        # The parent who owns the family wallet is always allowed.
        if obj.family_wallet.parent == user:
            return True
        # The child involved in the transaction is allowed.
        if user.role == User.ROLE_CHILD and obj.child and obj.child.user == user:
            return True
        return False
