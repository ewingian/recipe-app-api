from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import email


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """return User(model)
        Create and saves a new user
        """
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using.self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """return None
    Custome user model that supports using email instead of email
    """
    email = models.EmailField(max_length=225, unique=True)
    name = models.CharField(max_length=225)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'