from django.shortcuts import render,redirect
from django.views.generic import TemplateView
from django.http.response import JsonResponse
from django.core.mail import send_mail
from contact.models import Contact
from company.models import Job,CompanyInfo
from pages.models import User
# Contact Form
class ContactView(TemplateView):
    template_name = "contact.html"
    def post(self,request):
        if request.method == "POST":
            name = request.POST["name"]
            email = request.POST["email"]
            subject = request.POST["subject"]
            comment = request.POST["comments"]
            print("name :",name,"email :",email,"subject:",subject,"comment:",comment)
            # messages.success(request, name)
            c = Contact()
            c.name=name,
            c.email=email,
            c.subject=subject,
            c.comment=comment,
            c.save()
            if name and email and subject and comment != "":
                subject = "Thank You"
                from_mail = 'confirmation@webnike.com'
                message = "Thank you for contact us"
                send_mail(subject, message, from_mail, [email],fail_silently=False)
                return redirect("/contact")

class JobApproveView(TemplateView):
    def get(self, request):
        job_id = request.GET.get("job_id")
        if job_id:
            try:
                job = Job.objects.get(id=job_id)
                job.is_approved = True
                job.save()
                # Perform any additional logic related to job approval
                # ...
            except Job.DoesNotExist:
                pass
        return redirect("/admin/company/job/")
    
    
class JobDisApproveView(TemplateView):
    def get(self, request):
        job_id = request.GET.get("job_id")
        if job_id:
            try:
                job = Job.objects.get(id=job_id)
                job.is_approved = False
                job.save()
                # Perform any additional logic related to job approval
                # ...
            except Job.DoesNotExist:
                pass
        return redirect("/admin/company/job/")
    
    
    
class CoApproveView(TemplateView):
    def get(self, request):
        co = request.GET.get("job_id")
        if co:
            try:
                co = CompanyInfo.objects.get(id=co)
                print(co.user.username)
                co.user.is_active = True
                print(co.user.is_active)
                co.user.save()
            except CompanyInfo.DoesNotExist:
                pass
        return redirect("/admin/company/companyinfo")
    
    
class CoDisApproveView(TemplateView):
    def get(self, request):
        co = request.GET.get("job_id")
        print(co)
        if co:
                co = CompanyInfo.objects.get(id=co)
                print(co.user.username)
                co.user.is_active = False
                print(co.user.is_active)
                co.user.save()
                
        return redirect("/admin/company/companyinfo")