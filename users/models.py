from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, phone, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        user_type = extra_fields.pop('user_type', 'visitor')
        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password, phone=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, phone or '0000000000', **extra_fields)

class CustomUser(AbstractBaseUser):
    phone = models.CharField(max_length=15)
    first_name = models.CharField(max_length=225)
    last_name = models.CharField(max_length=225)
    user_type = models.CharField(max_length=10, choices=[('admin', 'Admin'), ('visitor', 'Visitor')])
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    email = models.EmailField(max_length=80, unique=True)
    username = models.CharField(max_length=80, unique=False, blank=True, null=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', 'first_name', 'last_name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name