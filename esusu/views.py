import json

from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework_jwt.settings import api_settings

from api.logger import logger
from api.permissions import (IsGroupCreator, IsGroupCreatorOrReadOnly,
                             IsMembershipOwnerOrGroupAdmin, IsSuperEsusuAdmin)
from api.settings import DOMAIN, SECRET_KEY
from api.utils import decrypt, encrypt, send_mail

from .models import Contribution, Group, Membership, Tenure
from .serializers import (ContributionSerializer, GroupSerializer,
                          MembershipSerializer, TokenSerializer,
                          UserSerializer)
from drf_yasg.utils import no_body, swagger_auto_schema
from drf_yasg import openapi
from drf_yasg.app_settings import swagger_settings



User = get_user_model()

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class CreateUserView(generics.CreateAPIView):
    """
        description : Endpoint to register a new user on the platform
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class =  UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        logger.debug(request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)


class LoginUserView(generics.CreateAPIView):
    """
        endpoint for logging in a user  api/login
        
    """
    permission_classes = (permissions.AllowAny, )
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        """
        post: function to process the log in request
        """
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        logger.debug("log in credentials", extra={
                     "username": username, "password": password})
        user = authenticate(
            request=request, username=username, password=password)
        if user is not None:
            login(request, user)
            serializer = TokenSerializer(
                data={
                    "token": jwt_encode_handler(
                        jwt_payload_handler(user)
                    )
                }
            )
            serializer.is_valid()
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class UserAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    UserAPIView handles GET, PATCH, DELETE requests of a user


    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, )


class ListUserView(generics.GenericAPIView):

    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_user_groups_joined(self, user):
        return [{
            "name": i.group.name,
            "id": str(i.group.id),
            "joined": str(i.ts_created),
            "is_admin": user.username == i.group.admin.username
        } for i in user.groups_joined.all()]

    def get(self, request, *args, **kwargs):
        """
        description: This returns all the users.
        endpoint : api/users/
        """
        user = self.request.user
        if not user.is_staff:
            return Response(
                data={
                    "message": "you are not authorized"
                },
                content_type="application/json",
                status=status.HTTP_401_UNAUTHORIZED
            )
        users = [{
            "first_name": i.first_name,
            "last_name": i.last_name,
            "user_name": i.username,
            "phone": i.phone,
            "email": i.email,
            "gender": i.gender,
            "id" : i.id,
            "groups_joined": self.get_user_groups_joined(i)
        } for i in self.get_queryset()]
        return Response(
            data=users,
            content_type="application/json"
        )

class MembershipAPIView(generics.RetrieveUpdateDestroyAPIView, generics.GenericAPIView):
    """
    MembershipAPIView : handles get and delete methods for the 
                        group membership, it allow a user the ability to
                        revoke their membership and also get their membership status.


    """
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    http_method_names = ['get', 'delete']
    permission_classes = (permissions.IsAuthenticated, IsMembershipOwnerOrGroupAdmin)

    def contributions(self, member):
        mbr = member.contributions.all()
        return [{"amount": i.contrib_amount, "date": str(i.ts_contributed)} for i in mbr]

    def get(self, request, *args, **kwargs):
        membership = self.get_object()
        return Response(
            data = {
                "group": membership.group.name,
                "date_joined": membership.ts_created,
                "status" : membership.status,
                "contributions" : self.contributions(membership)
            },
            status=status.HTTP_200_OK
        )

class UserMembershipListView(ListModelMixin,
                         generics.GenericAPIView):
    """
    MembershipListView : list all the membership of a particular user
    """
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = (permissions.IsAuthenticated, IsMembershipOwnerOrGroupAdmin)

    def get(self, request, *args, **kwargs):
        mbr = self.get_object()
        data = self.queryset.filter(user = mbr.user)
        serializer = MembershipSerializer(data, many=True)
        return Response(
            data = serializer.data,
            status= status.HTTP_200_OK
        )

class ContributionCreateView(generics.GenericAPIView):
    """
    ContributionApiView : create a contribution. this will allow
                            a user to make a contribution to an esusu group    
    """
        
    queryset = Membership.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = MembershipSerializer

    def get_contribution(self, member):
        amt = 0
        for i in member.contributions.all():
            amt = amt + i.contrib_amount
        return amt
        

    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            group = Group.objects.get(id=request.data.get("group_id"))
        except Group.DoesNotExist:
            return Response(
                data={
                    "message": "The requested group does not exist"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        tenure = Tenure.objects.get(id=group.tenure.id)
        if not tenure or tenure.status in ("I", "Inactive"):
            return Response(
                data = {
                    "message" : "You cannot make contributions when the Esusu have not kicked off"
                },
                status = status.HTTP_403_FORBIDDEN
            )
        try:
            membership = group.members.get(user__id=user.id)
        except  Membership.DoesNotExist:
            return Response(
                data={
                    "message": "The logged in user  does not have a membership with this group"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        print("status :{}, user : {}".format(membership.status, membership.user.username))
        if membership.status in ("I", "Inactive"):
            return Response(
                data={
                    "message": "Your membership on this group is inactive, and you cannot make contributions. please contact the group admin"
                },
                status=status.HTTP_403_FORBIDDEN
            )
        contribution = Contribution.objects.create(group=group, member=membership, contrib_amount=group.contrib_amount)
        return Response(
            status=status.HTTP_201_CREATED,
            data={
                "total contributions" : self.get_contribution(membership)
            }
        )

class GroupListView(ListModelMixin, generics.GenericAPIView):

    """
     This endpoint returns all Esusu groups on the platform that is searchable
    """

    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    permision_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(operation_description="This endpoint returns all "
        + "Esusu groups on the platform that is searchable", responses={200: GroupSerializer(many=True)})
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class GroupCreateAPIView(CreateModelMixin,
                         generics.GenericAPIView):
                         
    queryset = Group.objects.filter(is_searchable = True)
    serializer_class = GroupSerializer
    permision_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(operation_description="Create a group on the platform."
    +" This will automatically make the currently logged in user the group admin and a member")
    def post(self, request, *args, **kwargs):
        serializer = GroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(admin=request.user.id)
        return Response(status=status.HTTP_201_CREATED)


class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):

    """
     Do basic operations on a singe instance of a group, calling the endpoints must be  a group admin of the group
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsGroupCreatorOrReadOnly, )


class GroupMembershipView(generics.GenericAPIView):
    """
     insert members into a group
    """
    queryset = Group.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsGroupCreator, )
    serializer_class = MembershipSerializer

    def contributions(self, member):
        mbr = member.contributions.all()
        return [{"amount": i.contrib_amount, "date": str( i.ts_contributed)} for i in mbr]

    @swagger_auto_schema(operationa_description="get all the  members of a group")
    def get(self, request, *args, **kwargs):
        """
        get This endpoint handles the returning of members of a group

        """

        grp = self.get_object()
        mbrs = [
            {
                "membership_id" : mbr.id,
                "username": mbr.user.username,
                "joined": mbr.ts_created,
                "contributions": self.contributions(mbr),
                "status": mbr.status
            } for mbr in grp.members.all()]
        logger.info("members : {}".format(mbrs))
        return Response(
            data=mbrs,
            status=status.HTTP_200_OK
        )

    def check_group_is_ready(self):
        grp = self.get_object()
        mbr_statuses = grp.members.filter(status="I")
        if len(mbr_statuses) < 1 and len((grp.members.all())) == grp.capacity:
            return True
        return False

    def put(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        if user_id is None:
            return Response(
                data={
                    "message": "a user is required to be added"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            grp = self.get_object()
        except Group.DoesNotExist:
            return Response(
                data={
                    "message": "The requested group does not exist"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            usr = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                data={
                    "message": "The User you wanted to add as member doesnt exist"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        mbr = grp.members.all().filter(user__id=usr.id)

        if len(mbr) > 0:
            return Response(
                data={
                    "message": "The User is already a member of this group"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        membership = Membership.objects.create(group=grp, user=usr, status="A")
        membership.save()
        logger.debug(membership)
        grp.members.add(membership)
        mbr = [i.user.username for i in grp.members.all()]
        if self.check_group_is_ready():
            tenure = Tenure.objects.create(group=grp)
            return Response(
                data={
                    "message" : "The amount of active "
                    + "members are complete and the tenure"
                    +" should start now, below is the sequence of collection",
                    "collections": tenure.collection_sequences
                },
                status=status.HTTP_200_OK
            )

        return Response(
            data={
                "members": mbr
            },
            status=status.HTTP_201_CREATED
        )


class GroupInviteView(generics.GenericAPIView):

    queryset = Group.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsGroupCreator, )
    serializer_class = GroupSerializer

    @swagger_auto_schema(operationa_description="A user who is a group admin can send an invitation " 
    + "to join his/her group to user. this endpoint allow an admin to do that, the invitation will be sent to the user's mail.")
    def post(self, request, *args, **kwargs):
        """
        post will handle the endpoint that allow a group admin to
              create and send an invite to a user to join his group

        endpoint : api/groups/:id/members/invite/
        """
        group = self.get_object()
        to_be_member = request.data.get("username")
        try:
            user = User.objects.get(username=to_be_member)
        except User.DoesNotExist:
            return Response(
                data={
                    "message": "The User you wanted to add as member doesnt exist"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        membership = Membership.objects.create(
            group=group, user=user, status='I')
        encrypted_details = encrypt(str(membership.id), SECRET_KEY)
        url = "{}/api/groups/members/invite/accept/{}/".format(
            DOMAIN, encrypted_details.decode())
        group_invite = "<h3>Dear {}, you have been invited by {}, to join the esusu group {} on Esusu confam<a href='{}'>Esusu confam</a>!</h3><br />Please kindly click on the url  to accept and activate your membership.{} May the force be with you!".format(
            user.username, group.admin.username,
            group.name, DOMAIN, url)
        logger.info("invite details: {}".format(
            {"invite url": url, "user": user.username, "email": user.email}))
        mail_subject = "Esusu Group Invite"
        text_heading = "Hello, Dear"
        mail_resp = send_mail(mail_subject, user, text_heading, group_invite)
        logger.debug("email response : {}".format(mail_resp.json()))
        return Response(
            data={
                "url": url
            },
            status=status.HTTP_201_CREATED
        )


class GroupInviteAcceptanceView(generics.GenericAPIView):
    """
    GroupInviteAcceptanceView will handle the endpoint where user click on invite url from mail
    endpoint : api/group/members/invite/<token>

    """
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer

    def get(self, request, token):

        try:
            data = int(decrypt(token, SECRET_KEY).decode())
            membership = Membership.objects.get(id=int(data))
        except (ValueError, Membership.DoesNotExist) as e:
            logger.debug("something went wrong: {}".format(e.__str__()))
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )
        membership.status = 'A'
        membership.save()
        return Response(
            status=status.HTTP_200_OK
        )
