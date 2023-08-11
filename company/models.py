from django.db import models
from pages.models import User
from django.contrib.humanize.templatetags.humanize import naturaltime



class PricingPlan(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    jobs_count = models.IntegerField(null=True)
    for_company = models.BooleanField(null=True)
    
    customizable_field1 = models.CharField(max_length=255, blank=True)
    customizable_field2 = models.CharField(max_length=255, blank=True)
    customizable_field3 = models.CharField(max_length=255, blank=True)
    customizable_field4 = models.CharField(max_length=255, blank=True)
    customizable_field5 = models.CharField(max_length=255, blank=True)
    customizable_field6 = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

class CompanyInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    profile_pic = models.FileField(upload_to='static/profile', null=True, blank=True)
    introduction = models.TextField(null=True, blank=True)
    established = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    total_employees = models.CharField(max_length=255, null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    whatsapp = models.URLField(max_length=255, null=True, blank=True)
    skype = models.URLField(null=True, blank=True)
    location_url = models.URLField(null=True, blank=True)
    company_website = models.URLField(max_length=255, null=True, blank=True)
    working_days = models.TextField(null=True, blank=True)
    company_gallery = models.FileField(upload_to='static/company_gallery', null=True, blank=True)
    owner_name = models.CharField(max_length=255, null=True, blank=True)
    purchased_package = models.ForeignKey(PricingPlan, null=True, on_delete=models.CASCADE)
    job_post_count = models.IntegerField(null=True, blank=True)

class CompanyGallery(models.Model):
    user_id = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE)
    companies_gallery =  models.FileField(upload_to='static/companies_gallery', null=True, blank=True)

class Job(models.Model):
    job_title = models.CharField(max_length=100)
    job_description = models.TextField()
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    categories = models.CharField(max_length=100)
    job_type = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    job_skills = models.CharField(max_length=100)
    last_date = models.DateField()
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)
    posted_date = models.DateTimeField(auto_now_add=True)
    job_image = models.FileField(upload_to='static/job_images', blank=True, null=True)
    qualification = models.TextField(null=True, blank=True)
    responsibilities = models.TextField(null=True, blank=True)
    skillsandxperience = models.TextField(null=True, blank=True)
    experience_req = models.CharField(max_length=100, null=True)
    basic_qualification = models.CharField(max_length=150, null=True)
    industry_type = models.CharField(max_length=100, null=True)
    is_approved = models.BooleanField(default=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE)

    def __str__(self):
        return self.job_title

    @property
    def time_ago(self):
        return naturaltime(self.posted_date)

class SubscriptionModel(models.Model):
    invoice_no = models.TextField(null=True, blank=True)
    paid = models.BooleanField(null=True, blank=True)

class JobCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class JobType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Location(models.Model):
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.location