from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    is_company = models.BooleanField(default=False)
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        instance.profile.save()

class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    introduction = models.TextField(null=True, blank=True)
    languages = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    cv_file = models.FileField(upload_to='static/cv', null=True, blank=True)
    profile_pic = models.FileField(upload_to='static/profile', null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    whatsapp = models.CharField(max_length=255, null=True, blank=True)
    profession = models.CharField(max_length=255, null=True, blank=True)
    skills = models.CharField(max_length=255, null=True, blank=True)
    skype = models.URLField(null=True, blank=True)
    education_details = models.TextField(null=True, blank=True)
    experience_details = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    qualification = models.CharField(max_length=255, null=True, blank=True)
    categories = models.CharField(max_length=255, null=True, blank=True)
    salary = models.CharField(max_length=255, null=True, blank=True)
    experience_years = models.IntegerField(null=True, blank=True)
    purchased_package = models.ForeignKey('company.PricingPlan', null=True, on_delete=models.CASCADE)
    job_apply_count = models.IntegerField(null=True, blank=True)
    

    def __str__(self):
        return self.user.username

class UserProjects(models.Model):
    user_id = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    project_file =  models.FileField(upload_to='static/candidate_project', null=True, blank=True)
    