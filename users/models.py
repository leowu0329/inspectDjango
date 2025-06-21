from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUser(AbstractUser):
	age = models.PositiveIntegerField(default=0)

	@property
	def profile(self):
		try:
			return self._profile if hasattr(self, '_profile') else self._profile_cache
		except Profile.DoesNotExist:
			return Profile.objects.create(user=self)

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    
    # Personal Information
    personal_id = models.CharField(max_length=20, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    
    # Contact Information
    phone = models.CharField(max_length=20, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    
    # Work Information
    ROLE_CHOICES = [
        ('guest', '訪客'),
        ('user', '一般使用者'),
        ('admin', '管理者'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    
    WORK_AREA_CHOICES = [
        ('north', '雙北桃竹苗'),
        ('central', '中彰投'),
        ('south', '雲嘉南'),
        ('kaoping', '高高屏'),
    ]
    work_area = models.CharField(max_length=10, choices=WORK_AREA_CHOICES, blank=True, null=True)
    
    # Address Information
    city = models.CharField(max_length=20, blank=True, null=True)
    district = models.CharField(max_length=20, blank=True, null=True)
    village = models.CharField(max_length=20, blank=True, null=True)
    neighbor = models.CharField(max_length=10, blank=True, null=True)
    street = models.CharField(max_length=50, blank=True, null=True)
    section = models.CharField(max_length=10, blank=True, null=True)
    lane = models.CharField(max_length=10, blank=True, null=True)
    alley = models.CharField(max_length=10, blank=True, null=True)
    number = models.CharField(max_length=10, blank=True, null=True)
    floor = models.CharField(max_length=10, blank=True, null=True)
    
    IDENTITY_TYPE_CHOICES = [
        ('public', '公'),
        ('private', '私'),
    ]
    identity_type = models.CharField(max_length=10, choices=IDENTITY_TYPE_CHOICES, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Signal to create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
