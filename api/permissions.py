from rest_framework import permissions
from .logger import logger


class IsGroupCreatorOrReadOnly(permissions.BasePermission):
    """
    IsGroupCreatorOrReadOnly this is a permission for object level author
                             ization. if the user is the admin then he can edit
    """

    def has_object_permission(self, request, view, obj ):
        if request.method in permissions.SAFE_METHODS:
            return True
        isAdmin = obj.admin == request.user
        logger.debug("Checking user permission"
        + " to satify if the admin is the one modifying an objects")
        logger.debug( "logged in user : {}".format(request.user.username))
        logger.debug("group owner: {}".format(obj.admin.username) )
        return isAdmin


class IsGroupCreator(permissions.BasePermission):
    """
    IsGroupCreator : this is a permission for object level author
                             ization. The only person allowed to edit and view is 
                             the group creator
    """

    def has_object_permission(self, request, view, obj ):
        isAdmin = obj.admin == request.user
        logger.debug("Checking user permission"
        + " to satify if the admin is the one modifying an objects")
        logger.debug( "logged in user : {}".format(request.user.username))
        logger.debug("group owner: {}".format(obj.admin.username) )
        return isAdmin


class IsSuperEsusuAdmin(permissions.BasePermission):
    """
    IsSuperEsusuAdmin : this is a permission for object level author
                             ization. The only person allowed to edit and view is 
                             an admin user of the esusu platform
    """

    def has_object_permission(self, request, view, obj ):
        is_staff = obj.is_staff ==  True
        logger.debug("Checking user permission"
        + " to satify if the user in scope is a superadmin")
        logger.debug( "logged in user : {}".format(request.user.username))
        logger.debug("group owner: {}".format(obj.admin.username) )
        return is_staff


class IsMembershipOwnerOrGroupAdmin(permissions.BasePermission):
    """
    IsMembershipOwner : this is a permission for object level author
                             ization. The only person allowed to edit and view is 
                             the user that owned this membership
    """

    def has_object_permission(self, request, view, obj ):
        logger.debug("Checking user permission"
        + " to satify if the user in the owner of the membership or the group admin")
        logger.debug( "logged in user : {}".format(request.user.username))
        logger.debug("group owner: {}".format(obj.user.username) )
        return obj.user == request.user or obj.group.admin == request.user
