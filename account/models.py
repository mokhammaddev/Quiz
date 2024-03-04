from django.db import models
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager
from django.conf import settings
from ckeditor.fields import RichTextField
from django.db.models.signals import pre_save
from django.utils.safestring import mark_safe
from rest_framework_simplejwt.tokens import RefreshToken


def file_path(instance, filename):
    return f"courses/{instance.title}/{instance.title}/{filename}"


class AccountManager(BaseUserManager):

    def create_user(self, username, password=None, **extra_fields):
        if username is None:
            raise TypeError('You should have an username!')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        if password is None:
            raise TypeError("Password should not be None!")
        user = self.create_user(
            username=username,
            password=password,
            **extra_fields
        )
        user.is_superuser = True
        user.is_active = True
        user.is_staff = True
        user.save(using=self._db)
        return user


# ROLES = (teacher, student)
class Account(AbstractBaseUser, PermissionsMixin):
    """ Custom Account Model """
    username = models.CharField(max_length=218, unique=True, verbose_name='Username', db_index=True)
    first_name = models.CharField(max_length=218)
    last_name = models.CharField(max_length=218)
    image = models.ImageField(upload_to=file_path, null=True, blank=True)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    bio = RichTextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    objects = AccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def image_tag(self):
        if self.image:
            return mark_safe(f'<a href="{self.image.url}"><img src="{self.image.url}" style="height:30px;"/></a>')
        else:
            return "-"

    @property
    def image_url(self):
        if self.image:
            if settings.DEBUG:
                return f'{settings.LOCAL_BASE_URL}{self.image.url}'
            return f'{settings.PROD_BASE_URL}{self.image.url}'
        return None

    @property
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
        return data


# def account_pre_save(instance, sender, *args, **kwargs):
#     if instance.is_superuser:
#         instance.is_superuser = True
#     else:
#         instance.is_superuser = False
#
#
# pre_save.connect(account_pre_save, sender=Account)
