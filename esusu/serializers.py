from api.utils import ChoiceField
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Contribution, Group, Membership

User = get_user_model()

class GroupSerializer(serializers.ModelSerializer):
    admin = serializers.ReadOnlyField(read_only=True, required=False, source='admin.username')
    ts_created = serializers.DateField(required=False, read_only=True)
    id  = serializers.CharField(required=False, read_only=True)

    class Meta:
        fields = ('name', 'description', 'admin', 'capacity', 'id', 'round_type', 'is_searchable','contrib_amount', 'ts_created')
        model = Group

    def create(self, validated_data):
        user = User.objects.filter(pk=validated_data["admin"]).first()
        validated_data["admin"] = user
        group =  Group.objects.create(**validated_data)
        member = Membership.objects.create(group=group, user=user, status="A")
        member.save()
        group.members.add(member)        
        group.save()
        return group

class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required = False)
    last_name = serializers.CharField(required = False)
    gender = ChoiceField(choices=User.GENDER_OPTIONS)


    class Meta:
        fields = ('id', 'first_name', 'last_name', 'username', 'phone', 'email', 'gender')
        model = User

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class MembershipSerializer(serializers.Serializer):
    ts_created = serializers.DateField(read_only=True)
    group = serializers.ReadOnlyField(source='group.name')
    status = ChoiceField(choices=Membership.STATUS_OPTIONS)

    class Meta:
        fields = ('user', 'status','contribution', 'id', 'group', 'ts_created')
        model = Membership

class ContributionSerializer(serializers.Serializer):
    ts_contributed = serializers.DateField(read_only=True)

    class Meta:
        fields = ('ts_contributed', 'member', 'group', 'contrib_amount')
        model = Contribution
                

class TokenSerializer(serializers.Serializer):
    """
    This serializer serializes the token data
    """
    token = serializers.CharField(max_length=255)
