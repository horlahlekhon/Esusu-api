import json

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status

from .models import Group, Membership, Tenure
from .serializers import GroupSerializer

# make sure the user in scope is the one we extended
User = get_user_model()


class BaseViewTest(APITestCase):
    client = APIClient()

    @staticmethod
    def create_group(name="", description="",
                     admin='', capacity=0,
                     is_searchable=False, contrib_amount=0.0):
        Group.objects.create(
            name=name, description=description,
            admin=admin, capacity=capacity,
            is_searchable=is_searchable,
            contrib_amount=contrib_amount)

    def login_client(self, username="", password=""):
        data = json.dumps({
            "username": username,
            "password": password
        })
        response = self.client.post(
            reverse('create-token'),
            data=data,
            content_type='application/json'
        )
        self.token = response.data["token"]
        # set the token in the header
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.token
        )
        self.client.login(username=username, password=password)
        return self.token

    def login_a_user(self,  username="", password=""):
        data = json.dumps({
            "username": username,
            "password": password
        })
        response = self.client.post(
            reverse("login_user"),
            data=data,
            content_type="application/json"
        )
        return response

    def register_user(self):
        data = json.dumps({
            "username": "Olalekan",
            "email": "Olalekan@gmail.com",
            "password": "New passwor24t8o39210",
        })
        response = self.client.post(
            reverse("register_user"),
            data=data,
            content_type="application/json",
        )
        return response

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user",
            email="test@mail.com",
            password="testing",
            first_name="test",
            last_name="user",
            phone="09023788967",
            gender="M"
        )
        self.user2 = User.objects.create_user(
            username="test_user1",
            email="test1@mail.com",
            password="testing1",
            first_name="test1",
            last_name="user1",
            phone="09023788967",
            gender="M"
        )
        self.user3 = User.objects.create_user(
            username="test_user3",
            email="test3@mail.com",
            password="testing3",
            first_name="test3",
            last_name="user3",
            phone="09023788967",
            gender="M"
        )

        self.create_group(
            "Es_lag1", "This is a group",
            self.user, 4, True, 900.0)
        self.create_group(
            "ES-lag4", "Es group in lagos",
            self.user2, 7, False, 120.00)


class GroupTest(BaseViewTest):

    def test_create_group_with_valid_data(self):
        """
            Test a group creation
        """

        import random
        rand = random.randint(1, 100)
        usr = User.objects.create_user(
            username="test_user{}".format(rand),
            email="test{}@mail.com".format(rand),
            password="testing{}".format(rand),
            first_name="test{}".format(rand),
            last_name="user{}".format(rand),
            phone="09023788967",
            gender="M"
        )
        self.login_client("test_user{}".format(rand), "testing{}".format(rand))

        data = json.dumps({
            "name": "Esusu-OG78",
            "description": "A group",
            "capacity": 4,
            "is_searchable": False,
            "contrib_amount": 2000
        })

        response = self.client.post(
            reverse("new_group"),
            data=data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_all_groups(self):
        """
            this will test if all the groups 
            added during setup are available
        """
        self.login_client("test_user", "testing")
        response = self.client.get(
            reverse('groups'),
            content_type="application/json"
        )
        groups = Group.objects.all()
        serialized_data = GroupSerializer(groups, many=True)
        self.assertEqual(response.data, serialized_data.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_a_single_group(self):
        """
        test_get_a_single_group tests the endpoint api/group/{groupid}
                                which fetches a group based on its id
        """
        self.login_client("test_user", "testing")
        grp = Group.objects.get(name='Es_lag1')
        response = self.client.get(
            reverse("get_group", args=[str(grp.id)]),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("name"), "Es_lag1")

    def test_add_a_single_member_to_group(self):
        """
        test_add_a_single_member_to_group: tests the addition of members to a group
                                 the user adding must be the admin 
        """
        self.login_client("test_user", "testing")
        grp = Group.objects.get(name='Es_lag1')
        user = User.objects.get(username="test_user1")
        response = self.client.put(
            reverse("add_member", args=[str(grp.id)]),
            data=json.dumps({
                "user_id": str(user.id)
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_a_member_by_a_non_admin_of_a_group(self):
        """
        test_add_a_single_member_to_group tests the addition of a member 
                                          by a non admin user of a group.
        endpoint : api/groups/:id/members/add
        """
        self.login_client("test_user", "testing")
        grp = Group.objects.get(name='ES-lag4')
        usr = User.objects.get(username="test_user3")
        response = self.client.put(
            reverse("add_member", args=[str(grp.id)]),
            data=json.dumps({
                "user_id": str(usr.id)
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_all_members_of_a_group_by_admin_only(self):
        """
        test_get_all_members_of_a_group_by_admin_only :
             This tests the endpoint api/groups/:id/members/
        """
        self.login_client("test_user", "testing")
        usr = User.objects.get(username="test_user1")
        grp = Group.objects.get(name="Es_lag1")
        mbrship = Membership.objects.create(user=usr, group=grp)
        grp.members.add(mbrship)
        response = self.client.get(
            reverse("get_members", args=[str(grp.id)]),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list, type(response.data))

    def test_get_all_members_of_a_group_by_non_admin(self):
        """
        test_get_all_members_of_a_group_by_admin_only :
             This tests the endpoint api/groups/:id/members/ 
             when called by a non admin of the group should fail
        """
        self.login_client("test_user1", "testing1")
        grp = Group.objects.get(name="Es_lag1")
        response = self.client.get(
            reverse("get_members", args=[str(grp.id)]),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_send_group_invitation_to_a_user_by_admin(self):
        """
        test_send_group_invitation_to_a_user_by_admin : tests the endpoint that send 
                                                      group invitation to a user, must be an admin
        endpoint : api/groups/:id/members/invite/                                              
        """
        self.login_client("test_user", "testing")
        grp = Group.objects.get(name="Es_lag1")
        response = self.client.post(
            reverse("send_invite", args=[grp.id]),
            data=json.dumps({
                "username": self.user3.username
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(type(response.data.get("url")), str)

    def test_accept_invite_by_a_user(self):
        """
        test_accept_invite_by_a_user : tests the get endpoint for accepting invitation
                                       sent to the user.
        endpoint: api/groups/members/invite/accept/
        """
        self.login_client("test_user", "testing")
        grp = Group.objects.get(name="Es_lag1")
        response = self.client.post(
            reverse("send_invite", args=[grp.id]),
            data=json.dumps({
                "username": self.user3.username
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(type(response.data.get("url")), str)
        resp = self.client.get(
            response.data.get("url")
        )
        print("test_accept_invite_by_a_user : mmmmmmmmmmmmmmmmmmmmmmmmmmmmmm", resp.data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_accept_join_by_a_user(self):
        """
        test_accept_join_by_a_user : tests that an admin only can accept the invite of a user to join the group
        """
        user = User.objects.get(username="test_user3")
        grp = Group.objects.get(admin__username='test_user')
        mbrship = Membership.objects.create(user=user, group=grp, status="I")
        grp.members.add(mbrship)
        self.login_client("test_user", "testing")
        resp = self.client.post(
            reverse("accept_join_request", args=[str(grp.id)]),
                data = json.dumps({
                    "user" : user.id
            }),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)




class MembershipTests(BaseViewTest):
    """
    MembershipTests : tests for memberships
    """

    def test_contribute_amount(self):
        """
        test_contribute_amount : test the ability of a user to make
                                 contribution by only providing the group id
        endpoint : api/group/member/contribute/
        """
        grp = Group.objects.get(name='ES-lag4')
        usr = User.objects.get(username="test_user3")
        mbrship = Membership.objects.create(user=usr, group=grp, status="A")
        tenure = tenure = Tenure.objects.create(group=grp)
        self.login_client("test_user3", "testing3")
        response = self.client.post(
            reverse("make_contribution"),
            data=json.dumps({
                "group_id": grp.id.__str__()
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_contribute_amount_by_a_non_member_of_a_group(self):
        """
        test_contribute_amount : test the ability of a user to not be able make
                                 contribution if he isnt a prior member of the group
        endpoint : api/group/member/contribute/
        """
        grp = Group.objects.get(name='ES-lag4')
        tenure = tenure = Tenure.objects.create(group=grp)
        self.login_client("test_user1", "testing1")
        response = self.client.post(
            reverse("make_contribution"),
            data=json.dumps({
                "group_id": grp.id.__str__()
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_join_an_existing_group(self):
        """
        test_join_an_existing_group : this testst if a user can request to join a group
        """
        self.login_client("test_user3", "testing3")
        user = User.objects.get(username="test_user3")
        grp = Group.objects.get(name='ES-lag4')
        response = self.client.post(
            reverse("join_group", args=[str(grp.id)]),
            data = json.dumps({
                "group_id" : grp.id.__str__()
            }),
            content_type="application/json"
        )
        print("responseeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)




class RegisterUserTest(BaseViewTest):
    """
        tests for /api/register
    """

    def test_create_user_with_correct_data(self):
        data = json.dumps({
            "username": "Olalekan",
            "email": "Olalekan@gmail.com",
            "password": "New passwor24t8o39210",
            "gender": "M",
            "phone": "09021897763"
        })
        response = self.client.post(
            reverse("register_user"),
            data=data,
            content_type="application/json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_create_user_with_invalid_data(self):
        data = json.dumps({
            "username": "",
            "email": "",
            "password": "",
        })
        response = self.client.post(
            reverse("register_user"),
            data=data,
            content_type="application/json",
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )


class LoginUserTest(BaseViewTest):
    """
        Tests for users  api/login
    """

    def test_login_user_with_valid_credentials(self):
        response = self.login_a_user("test_user", "testing")
        self.assertIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.login_a_user("anonymous", "pass")
        # assert status code is 401 UNAUTHORIZED
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )
