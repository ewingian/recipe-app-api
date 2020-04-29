from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from django.conf import settings
import email


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """return User(model)
        Create and saves a new user
        """
        if not email:
            raise ValueError('Users must have vaild email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """return User
        create a new super user
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
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
    

class Tag(models.Model):
    """Tag to be used for a recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    
    def __str__(self):
        """returns the name"""
        return self.name
    
class Ingredient(models.Model):
    """Ingredient to be used in a recipe"""
    
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE
    )
 

    def __str__(self):
        """returns the name"""
        return self.name
     