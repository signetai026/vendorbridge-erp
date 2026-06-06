
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
 
 
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
 
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)
 
 
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('procurement_officer', 'Procurement Officer'),
        ('vendor', 'Vendor'),
        ('manager', 'Manager'),
    ]
 
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='procurement_officer')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
 
    objects = UserManager()
 
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
 
    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
 
    def __str__(self):
        return f"{self.name} ({self.email})"
 
    def get_role_display_badge(self):
        badges = {
            'admin': 'danger',
            'procurement_officer': 'primary',
            'vendor': 'success',
            'manager': 'warning',
        }
        return badges.get(self.role, 'secondary')
 
    @property
    def is_admin(self):
        return self.role == 'admin'
 
    @property
    def is_manager(self):
        return self.role == 'manager'
 
    @property
    def is_procurement_officer(self):
        return self.role == 'procurement_officer'
 
    @property
    def is_vendor_user(self):
        return self.role == 'vendor'
 
 
class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
 
    class Meta:
        db_table = 'accounts_password_reset_token'
 
    def is_valid(self):
        from datetime import timedelta
        return not self.is_used and (timezone.now() - self.created_at) < timedelta(hours=24)