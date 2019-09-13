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
    
    def create_superuser(self, username, last_name, first_name, gender, phone, email, password):
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, null=False, blank=False)
    description = models.CharField(max_length=255, blank=False, null=False)
    admin = models.ForeignKey('User', on_delete=models.PROTECT, related_name='groups_created', null=False, blank=False)
    capacity = models.IntegerField(default=True, null=False, blank=False)
    is_searchable =  models.BooleanField(default=False, null=False, blank=False)
    contrib_amount = models.IntegerField(default=0, blank=False, null=False)
    ts_created = models.DateField(auto_now_add=True)
    round_type = models.CharField(max_length=10, default='W')

    def __str__(self):
        return "{} - {}".format(self.name, self.contrib_amount)

    ROUND_OPTIONS = (
        ('M', 'Monthly'),
        ('W', 'Weekly'),
        ('D', 'Daily'),
    )


class Membership(models.Model):
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='members', blank=True, null=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='groups_joined', blank=False, null=False)
    ts_created = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10,null=False, blank=False, default='I')

    STATUS_OPTIONS = (
        ('A', 'Active'),
        ('I', 'Inactive')
    )

    def __str__(self):
        return "{} - {}".format(self.group.name, self.user)


class Contribution(models.Model):
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='contributions', blank=True, null=True)
    member = models.ForeignKey('Membership', on_delete=models.CASCADE, related_name='contributions', blank=False, null=False )
    contrib_amount = models.IntegerField(default=0, blank=False, null=False)
    ts_contributed = models.DateField(auto_now_add=True)

    def __str__(self):
        return "{} - {}".format(self.member.user.username, self.contrib_amount)


class Tenure(models.Model):
    group = models.OneToOneField('Group', on_delete=models.PROTECT, blank=False, null=False)
    ts_from = models.DateField(auto_now_add=True)
    ts_end_date = models.DateField(null=True, blank=True)
    collection_sequence = JSONField(null=True, blank=True)


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
