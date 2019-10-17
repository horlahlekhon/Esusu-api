from django.urls import path, re_path
from rest_framework_jwt.views import obtain_jwt_token
from .views import (GroupCreateAPIView, CreateUserView, 
                    LoginUserView, GroupDetailView, 
                    GroupMembershipView, GroupInviteView,
                 GroupInviteAcceptanceView, UserAPIView,
                 ListUserView, ContributionCreateView,
                 MembershipAPIView, UserMembershipListView,
                 GroupListView)


urlpatterns = [
    path('token-auth/', obtain_jwt_token, name='create-token'),
    path("register/", CreateUserView.as_view(), name='register_user'),
    path("login/", LoginUserView.as_view(), name="login_user"),
    path("users/all/",ListUserView.as_view(), name="users" ),
    path("users/<int:pk>/",UserAPIView.as_view(), name="user_detail_view" ),
    path("user/memberships/<uuid:pk>/", MembershipAPIView.as_view(), name="membership_detail"),
    path("user/memberships/<uuid:pk>/all/", UserMembershipListView.as_view(), name="user_membership_list"),
    path("group/create/", GroupCreateAPIView.as_view(), name='new_group'),
    path("groups/", GroupListView.as_view(), name='groups'),
    path("group/<uuid:pk>/", GroupDetailView.as_view(), name='get_group'),
    path("group/<uuid:pk>/join-group/", GroupListView.as_view(), name="join_group"),
    path("group/<uuid:pk>/accept-join/", GroupListView.as_view(), name="accept_join_request"),
    path("group/<uuid:pk>/members/",GroupMembershipView.as_view(), name="get_members" ),
    path("group/<uuid:pk>/members/add/", GroupMembershipView.as_view(), name='add_member'),
    path("group/<uuid:pk>/members/invite/", GroupInviteView.as_view(), name="send_invite"), 
    re_path(r'^groups/members/invite/accept/(?P<token>[0-9A-Za-z_\-+=/]+)/$',
            GroupInviteAcceptanceView.as_view(), name='group_invite'),
    path("group/member/contribute/",
                ContributionCreateView.as_view(), name="make_contribution"),
    
    
]