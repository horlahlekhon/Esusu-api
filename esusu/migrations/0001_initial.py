# Generated by Django 2.2.4 on 2019-09-18 12:26

from django.conf import settings
import django.contrib.auth.validators
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone', models.CharField(max_length=14)),
                ('gender', models.CharField(max_length=10)),
                ('ts_created', models.DateField(auto_now_add=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='unique uuid for a group', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('description', models.CharField(help_text='Tell people more about the group', max_length=255)),
                ('capacity', models.IntegerField(default=True, help_text='How many members will the group have')),
                ('is_searchable', models.BooleanField(default=False, help_text='Set to true if you want the group to be private and invincible to other users, default to False')),
                ('contrib_amount', models.IntegerField(default=0, help_text='The amount to be contributed every round ')),
                ('ts_created', models.DateField(auto_now_add=True)),
                ('round_type', models.CharField(default='W', help_text='The types of rounds, could be W(weekly), M(monthly), D(Daily) ', max_length=10)),
                ('admin', models.ForeignKey(help_text='The User who created the group', on_delete=django.db.models.deletion.PROTECT, related_name='groups_created', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tenure',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text="unique uuid for a Group's tenure", primary_key=True, serialize=False)),
                ('ts_from', models.DateField(auto_now_add=True, help_text='when the tenure starts')),
                ('ts_end_date', models.DateField(blank=True, help_text='When the tenure ends or shall end', null=True)),
                ('collection_sequence', django.contrib.postgres.fields.jsonb.JSONField(blank=True, help_text='This is a sequence of collection sorted randomly for every member when the tenure starts', null=True)),
                ('status', models.CharField(default='A', editable=False, help_text="When a tenure's value of `ts_end_date` the status will become inactive and cannot be changed", max_length=10)),
                ('group', models.OneToOneField(help_text='The group to create a tenure for, must be a valid group that isnt in an active tenure', on_delete=django.db.models.deletion.PROTECT, to='esusu.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='unique uuid for a a membership', primary_key=True, serialize=False)),
                ('ts_created', models.DateField(auto_now_add=True)),
                ('status', models.CharField(default='I', help_text='Used to place an embargo on a member, can be A(active) or I(inactive)', max_length=10)),
                ('group', models.ForeignKey(blank=True, help_text='The group you want to join, must be a valid and active existing group', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='members', to='esusu.Group')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groups_joined', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Contribution',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='unique uuid for a contribution', primary_key=True, serialize=False)),
                ('contrib_amount', models.IntegerField(default=0, help_text='The amount to be contributed , this is fixed by the group admin when creating the group')),
                ('ts_contributed', models.DateField(auto_now_add=True, help_text='When was the contribution made')),
                ('group', models.ForeignKey(blank=True, help_text='The group to contribute to', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contributions', to='esusu.Group')),
                ('member', models.ForeignKey(help_text='The member making the contribution, must be an already active member', on_delete=django.db.models.deletion.CASCADE, related_name='contributions', to='esusu.Membership')),
            ],
        ),
    ]
