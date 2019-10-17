from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid, random, json
from django.contrib.postgres.fields import JSONField
from dateutil.relativedelta import relativedelta
import datetime
from api.utils import DateTimeEncoder
from django.contrib.postgres.fields.jsonb import JsonAdapter
# Create your models here.

class UserManager(BaseUserManager):

    def create_user(self, username, phone, email,gender=None, last_name="",first_name="", password=None):
        user = self.create(
            username = username,
            last_name = last_name,
            first_name = first_name,
            gender = gender,
            phone = phone,
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_superuser(self, username, phone, email, gender, last_name, first_name, password):
        user = self.create_user(username, last_name, first_name, gender, phone, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractUser):
    GENDER_OPTIONS = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    phone = models.CharField(max_length=14, null=False, blank=False)
    gender = models.CharField(max_length=10)
    ts_created = models.DateField(auto_now_add=True)



    def __str__(self):
        return self.username

    objects = UserManager()
class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="unique uuid for a group")
    name = models.CharField(max_length=20, null=False, blank=False)
    description = models.CharField(max_length=255, blank=False, null=False, help_text="Tell people more about the group")
    admin = models.ForeignKey('User', on_delete=models.PROTECT, related_name='groups_created', null=False, blank=False, help_text="The User who created the group")
    capacity = models.IntegerField(default=True, null=False, blank=False, help_text="How many members will the group have")
    is_searchable =  models.BooleanField(default=False, null=False, blank=False, help_text="Set to true if you want the group to be private and invincible to other users, default to False")
    contrib_amount = models.IntegerField(default=0, blank=False, null=False, help_text="The amount to be contributed every round ")
    ts_created = models.DateField(auto_now_add=True)
    round_type = models.CharField(max_length=10, default='W', help_text="The types of rounds, could be W(weekly), M(monthly), D(Daily) ")

    def __str__(self):
        return "{} - {}".format(self.name, self.contrib_amount)

    ROUND_TYPE_OPTIONS = (
        ('M', 'Monthly'),
        ('W', 'Weekly'),
        ('D', 'Daily'),
    )


class Membership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="unique uuid for a a membership")
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='members', blank=True, null=True, help_text="The group you want to join, must be a valid and active existing group")
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='groups_joined', blank=False, null=False)
    ts_created = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10,null=False, blank=False, default='I', help_text="Used to place an embargo on a member, can be A(active) or I(inactive)")

    STATUS_OPTIONS = (
        ('A', 'Active'),
        ('I', 'Inactive')
    )

    def __str__(self):
        return "{} - {}".format(self.group.name, self.user)


class Contribution(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="unique uuid for a contribution")
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='contributions', blank=True, null=True, help_text="The group to contribute to")
    member = models.ForeignKey('Membership', on_delete=models.CASCADE, related_name='contributions', blank=False, null=False, help_text="The member making the contribution, must be an already active member" )
    contrib_amount = models.IntegerField(default=0, blank=False, null=False, help_text="The amount to be contributed , this is fixed by the group admin when creating the group")
    ts_contributed = models.DateField(auto_now_add=True, help_text="When was the contribution made")

    def __str__(self):
        return "{} - {}".format(self.member.user.username, self.contrib_amount)


class Tenure(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="unique uuid for a Group's tenure")
    group = models.OneToOneField('Group', on_delete=models.PROTECT, blank=False, null=False, help_text="The group to create a tenure for, must be a valid group that isnt in an active tenure")
    ts_from = models.DateField(auto_now_add=True, help_text="when the tenure starts")
    ts_end_date = models.DateField(null=True, blank=True, help_text="When the tenure ends or shall end")
    collection_sequence = JSONField(null=True, blank=True, help_text="This is a sequence of collection sorted randomly for every member when the tenure starts")
    status= models.CharField(max_length=10, editable=False, default="A", help_text="When a tenure's value of `ts_end_date` the status will become inactive and cannot be changed")


    STATUS_OPTIONS = (
        ('A', 'Active'),
        ('I', 'Inactive')
    )

    def __str__(self):
        return "{} - {}".format(self.group.name, self.ts_from)

    @property
    def collection_sequences(self):
        members = list(self.group.members.all())
        random.shuffle(members)
        members = [{"position":i[0], "collection_date": (self.ts_from.today() + relativedelta(months=i[0])).__str__(), "user" :i[1].id } for i in enumerate(members)]
        self.collection_sequence = json.dumps(members, cls=DateTimeEncoder)
        self.ts_end_date = datetime.datetime.now() + relativedelta(months=self.group.capacity)
        return members
