from typing import Any, Dict
from django.views.generic import TemplateView
from pages.models import UserInfo, User, UserProjects
from company.models import CompanyInfo, CompanyGallery, Job, JobCategory, JobType, Location
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages
from django.contrib.auth import get_user
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.core.paginator import Paginator


class MainIndex(TemplateView):
    template_name = "index/main-index.html"
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        recent_jobs = Job.objects.all().order_by("id").reverse()
        locations = Location.objects.all()
        context["locations"] = locations
        
        if len(recent_jobs)>4:
            recent_jobs = list(recent_jobs)[:4]
        context["recent_jobs"] = recent_jobs

        featured_jobs = Job.objects.filter(company_id__in=CompanyInfo.objects.filter(~Q(purchased_package_id=4))).all()
        if len(featured_jobs)>4:
            featured_jobs = list(featured_jobs)[:4]
        context["featured_jobs"] = featured_jobs

        full_time_jobs = Job.objects.filter(job_type="Full Time").all()
        if len(full_time_jobs)>4:
            full_time_jobs = list(full_time_jobs)[:4]
        context["full_time_jobs"] = full_time_jobs

        part_time_jobs = Job.objects.filter(job_type="Part Time").all()
        if len(part_time_jobs)>4:
            part_time_jobs = list(part_time_jobs)[:4]
        context["part_time_jobs"] = part_time_jobs

        freelance_jobs = Job.objects.filter(job_type="Freelancer").all()
        if len(freelance_jobs)>4:
            freelance_jobs = list(freelance_jobs)[:4]
        context["freelance_jobs"] = freelance_jobs

        categories = JobCategory.objects.all()
        context['categories'] = categories



        return context


class Index(LoginRequiredMixin, TemplateView):
    template_name = "index/index-1.html"
    login_url = reverse_lazy('sign-in')
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        recent_jobs = Job.objects.all().order_by("id").reverse()
        locations = Location.objects.all()
        context["locations"] = locations

        if len(recent_jobs)>4:
            recent_jobs = list(recent_jobs)[:4]
        context["recent_jobs"] = recent_jobs

        featured_jobs = Job.objects.filter(company_id__in=CompanyInfo.objects.filter(~Q(purchased_package_id=4))).all()
        if len(featured_jobs)>4:
            featured_jobs = list(featured_jobs)[:4]
        context["featured_jobs"] = featured_jobs

        full_time_jobs = Job.objects.filter(job_type="Full Time").all()
        if len(full_time_jobs)>4:
            full_time_jobs = list(full_time_jobs)[:4]
        context["full_time_jobs"] = full_time_jobs

        part_time_jobs = Job.objects.filter(job_type="Part Time").all()
        if len(part_time_jobs)>4:
            part_time_jobs = list(part_time_jobs)[:4]
        context["part_time_jobs"] = part_time_jobs

        freelance_jobs = Job.objects.filter(job_type="Freelancer").all()
        if len(freelance_jobs)>4:
            freelance_jobs = list(freelance_jobs)[:4]
        context["freelance_jobs"] = freelance_jobs

        categories = JobCategory.objects.all()
        context['categories'] = categories



        return context

class SearchedJobsList(TemplateView):
    template_name = "pages/jobs/job-list.html"
    paginate_by = 10  # Number of jobs per page

    def get_context_data(self, category, **kwargs):
        context = super().get_context_data(**kwargs)
        job_list = None
        try:
            if self.request.user.is_company:
                job_list = Job.objects.filter(~Q(user=self.request.user) & Q(categories=category)).order_by('id').reverse()
            else:
                job_list = Job.objects.filter(Q(categories=category)).order_by('id').reverse()
        except:
            job_list = Job.objects.filter(Q(categories=category)).order_by('id').reverse()
        context['job_list'] = job_list
        for i in range(len(context['job_list'])):
            if context['job_list'][i].categories:
                context['job_list'][i].categories =  context['job_list'][i].categories.split(',')

         # Apply pagination
        paginator = Paginator(job_list, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        categories = JobCategory.objects.all()
        context['categories'] = categories
        context['job_list'] = page_obj
        return context

    def get(self, request, category, *args, **kwargs):
        context = self.get_context_data(category)
        return render(request, self.template_name, context)


class Index2(LoginRequiredMixin, TemplateView):
    template_name = "index/index-2.html"
    login_url = reverse_lazy('sign-in')


class Index3(LoginRequiredMixin, TemplateView):
    template_name = "index/index-3.html"
    login_url = reverse_lazy('sign-in')

# Manage-Jobs Page
class ManageJobs(LoginRequiredMixin, TemplateView):
    template_name = "manage-jobs.html"
    login_url = reverse_lazy('sign-in')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Retrieve jobs associated with the current user
        jobs = Job.objects.filter(user=self.request.user)
        categories = JobCategory.objects.all()
        locations = Location.objects.all()
        job_type = JobType.objects.all()
        context["categories"] = categories
        context['jobs'] = jobs
        context['job_types'] = job_type
        context['locations'] = locations
        return context


    def post(self, request, *args, **kwargs):

        company_detail = CompanyInfo.objects.get(user_id=request.user.id)
        if company_detail.job_post_count == 0:
            return redirect("pricing")
        job_title = request.POST.get('jobtitle')
        job_description = request.POST.get('jobdescription')
        email = request.POST.get('email')
        phone_number = request.POST.get('phoneNumber')
        categories = request.POST.get('categories')
        job_type = request.POST.get('jobtype')
        designation = request.POST.get('designation')
        salary = request.POST.get('salary')
        qualification = request.POST.get('qualification')
        job_skills = request.POST.get('skills')
        last_date = request.POST.get('lastdate')
        country = request.POST.get('country')
        city = request.POST.get('city')
        zipcode = request.POST.get('zipcode')
        image = request.FILES.get('jobimage')
        responsibilities = request.POST.get("responsibilities").splitlines()
        qualification = qualification.splitlines()
        skillsandxperience = request.POST.get("skillsandxperience").splitlines()
        exp = request.POST.get("experience")
        basic_qualification = request.POST.get('basic_qualification')
        ind_type = request.POST.get('industry_type')

        job = Job(
            job_title=job_title,
            job_description=job_description,
            email=email,
            phone_number=phone_number,
            categories=categories,
            job_type=job_type,
            designation=designation,
            salary=salary,
            qualification= str(qualification),
            job_skills=job_skills,
            last_date=last_date,
            country=country,
            city=city,
            zipcode=zipcode,
            user=request.user,
            job_image = image,
            company = CompanyInfo.objects.get(user_id=request.user.id),
            experience_req = exp,
            skillsandxperience = str(skillsandxperience),
            responsibilities = str(responsibilities),
            industry_type = ind_type,
            basic_qualification = basic_qualification,

        )
        job.save()
        company_detail.job_post_count -= 1
        company_detail.save()
        return redirect('job-list')
        # return ""

class ManageJobsPost(LoginRequiredMixin, TemplateView):
    template_name = "manage-jobs-post.html"
    login_url = reverse_lazy('sign-in')




class BookmarkJobs(LoginRequiredMixin, TemplateView):
    template_name = "bookmark-jobs.html"
    login_url = reverse_lazy('sign-in')

class Profile(LoginRequiredMixin, TemplateView):
    template_name = ""
    login_url = reverse_lazy('sign-in')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.request.user)
        if not self.request.user.is_company:
            self.template_name = "profile.html"
            # Retrieve the UserInfo object based on your logic
            user_info = UserInfo.objects.get(user=self.request.user)
            locations = Location.objects.all()

            # Add the UserInfo object to the context
            context['locations'] = locations
            context['user_info'] = user_info
            if context['user_info'].education_details:
                context['user_info'].education_details = eval(context['user_info'].education_details)
            if context['user_info'].experience_details:
                context['user_info'].experience_details = eval(context['user_info'].experience_details)
            context['languages'] = context['user_info'].languages.split(', ') if context['user_info'].languages else []
            context['skills'] = context['user_info'].skills.split(', ') if context['user_info'].skills else []
            context['cv_file'] = context['cv_file'] if "cv_file" in context.keys() else ""
            if context["cv_file"] != "":
                context['file_size'] = convert_size(user_info.cv_file.size)

            return context
        else:
            print("hello")
            self.template_name = "profile-company.html"
            locations = Location.objects.all()
            context['locations'] = locations
            company_info = CompanyInfo.objects.get(user=self.request.user)
            context['company_info'] = company_info
            return context

class CompanyProfile(LoginRequiredMixin, TemplateView):
    template_name = "profile-company.html"
    login_url = reverse_lazy('sign-in')
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve the UserInfo object based on your logic
        company_info = CompanyInfo.objects.get(user=self.request.user)
        locations = Location.objects.all() 

        # Add the UserInfo object to the context
        context['company_info'] = company_info
        context['locations'] = locations
        # if context['user_info'].education_details:
        #     context['user_info'].education_details = eval(context['user_info'].education_details)
        # if context['user_info'].experience_details:
        #     context['user_info'].experience_details = eval(context['user_info'].experience_details)
        # context['languages'] = context['user_info'].languages.split(', ') if context['user_info'].languages else []
        # context['skills'] = context['user_info'].skills.split(', ') if context['user_info'].skills else []
        # context['cv_file'] = context['cv_file'] if "cv_file" in context.keys() else ""
        # if context["cv_file"] != "":
        #     context['file_size'] = convert_size(user_info.cv_file.size)

        return context


class UserInfoUpdateView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'
    success_url = reverse_lazy('profile')
    login_url = reverse_lazy('sign-in')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Retrieve the UserInfo object for the logged-in user
        context['user_info'] = UserInfo.objects.get(user=self.request.user)
        locations = Location.objects.all()
        context['locations'] = locations
        return context

    def post(self, request, *args, **kwargs):
        
        # Retrieve the UserInfo object for the logged-in user
        user_info = UserInfo.objects.get(user=self.request.user)
        total_edu =len(list(filter(lambda x: x if x.startswith("study-field-") else None, dict(request.POST).keys())))
        total_exp = len(list(filter(lambda x: x if x.startswith("experience-field-") else None, dict(request.POST).keys())))
        experience = []
        education = []

        for i in range(1, total_edu+1):
            deg_name = request.POST.get(f"study-field-{i}")
            school_name = request.POST.get(f"school-field-{i}")
            deg_start = request.POST.get(f"deg-start-year-{i}")
            deg_end = request.POST.get(f"deg-end-year-{i}")
            edu_desc = request.POST.get(f"deg-description-{i}")
            edu_data = {"deg_name": deg_name, "school_name": school_name, "deg_start": deg_start, "deg_end": deg_end, "edu_description": edu_desc}
            education.append(edu_data)

        for i in range(1, total_exp+1):
            exp_name = request.POST.get(f"experience-field-{i}")
            org_name = request.POST.get(f"company-field-{i}")
            exp_start = request.POST.get(f"experience-start-year-{i}")
            exp_end = request.POST.get(f"experience-end-year-{i}")
            exp_desc = request.POST.get(f"experience-description-{i}")
            edu_data = {"exp_name": exp_name, "org_name": org_name, "exp_start": exp_start, "exp_end": exp_end, "exp_desc": exp_desc}
            experience.append(edu_data)

        # Update the UserInfo fields based on the posted data
        user_info.first_name = request.POST.get('first_name')
        user_info.last_name = request.POST.get('last_name')
        user_info.phone_number = request.POST.get('phone_number')
        user_info.introduction = request.POST.get('introduction')
        user_info.languages = request.POST.get('languages')
        user_info.location = request.POST.get('location')

        if request.FILES.get('cv_file'):
            user_info.cv_file = request.FILES.get('cv_file')
        if request.FILES.get('profile_pic'):
            user_info.profile_pic = request.FILES.get('profile_pic')

        user_info.facebook = request.POST.get('facebook')
        user_info.twitter = request.POST.get('twitter')
        user_info.linkedin = request.POST.get('linkedin')
        user_info.whatsapp = request.POST.get('whatsapp')
        user_info.profession = request.POST.get('profession')
        user_info.skills = request.POST.get('skills')

        # user_info.education_details = str(education)
        # user_info.experience_details = str(experience)
        user_info.skype = request.POST.get('skype')
        user_info.address = request.POST.get('address')
        user_info.qualification = request.POST.get('qualification')
        user_info.categories = request.POST.get('professionals')
        if request.POST.get('experience'):
            user_info.experience_years = request.POST.get('experience')
        user_info.salary = request.POST.get('salary')

        all_projects = request.FILES.getlist("projects")
        if all_projects and len(all_projects) >0:
            for project in all_projects:
                project = UserProjects(user_id = user_info, project_file=project)
                project.save()
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')

        if not User.objects.get(id=user_info.user_id).check_password(current_password):
            messages.error(request, 'Incorrect current password')
            return redirect(self.success_url)
        if new_password:
            user_info.user.password = make_password(new_password)
            user_info.user.save()
        # Save the updated UserInfo object
        user_info.save()
        if UserInfo.objects.get(user=self.request.user).profile_pic:
            request.session["profile_pic"] = str(UserInfo.objects.get(user=self.request.user).profile_pic)
        else:
            request.session["profile_pic"] = ""
        messages.success(request, 'Profile updated successfully')
        return redirect(self.success_url)

class CompanyInfoUpdateView(LoginRequiredMixin, TemplateView):
    template_name = 'profile-company.html'
    success_url = reverse_lazy('profile-company')
    login_url = reverse_lazy('sign-in')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Retrieve the UserInfo object for the logged-in user
        context['company_info'] = CompanyInfo.objects.get(user=self.request.user)
        locations = Location.objects.all()

        context['locations'] = locations
        return context
    def post(self, request, *args, **kwargs):

        # Retrieve the UserInfo object for the logged-in user
        company_info = CompanyInfo.objects.get(user=self.request.user)

        # Update the UserInfo fields based on the posted data
        company_info.company_name = request.POST.get('company_name')
        company_info.phone_number = request.POST.get('phone_number')
        company_info.introduction = request.POST.get('introduction')
        company_info.established = request.POST.get('established_year')
        company_info.location = request.POST.get('location')
        company_info.location_url = request.POST.get('location_url')
        company_info.introduction = request.POST.get('description')
        company_info.total_employees = request.POST.get('total_employees')
        company_info.owner_name = request.POST.get('owner_name')
        company_info.location = request.POST.get('location')
        all_gallery = request.FILES.getlist("gallery")
        if all_gallery and len(all_gallery) >0:
            for gallery in all_gallery:
                gal = CompanyGallery(user_id = company_info, companies_gallery=gallery)
                gal.save()
        company_info.facebook = request.POST.get('facebook')
        company_info.twitter = request.POST.get('twitter')
        company_info.linkedin = request.POST.get('linkedin')
        company_info.whatsapp = request.POST.get('whatsapp')
        company_info.skype = request.POST.get('skype')
        company_info.company_website = request.POST.get('web_link')

        monday_start = request.POST.get('moday_start')
        monday_end = request.POST.get('moday_end')
        tuesday_start = request.POST.get('tuesday_start')
        tuesday_end = request.POST.get('tuesday_end')
        wednesday_start = request.POST.get('wednesday_start')
        wednesday_end = request.POST.get('wednesday_end')
        thursday_start = request.POST.get('thursday_start')
        thursday_end = request.POST.get('thursday_end')
        friday_start = request.POST.get('friday_start')
        friday_end = request.POST.get('friday_end')
        saturday_start = request.POST.get('saturday_start')
        saturday_end = request.POST.get('saturday_end')
        days_open = []
        if monday_start and monday_end:
            days_open.append({"day":"Monday", "timing": f"{monday_start} - {monday_end}"})
        else:
            days_open.append({"day":"Monday", "timing": "Close"})
        if tuesday_start and tuesday_end:
            days_open.append({"day":"Tuesday", "timing": f"{tuesday_start} - {tuesday_end}"})
        else:
            days_open.append({"day":"Tuesday", "timing": "Close"})
        if wednesday_start and wednesday_end:
            days_open.append({"day":"Wednesday", "timing": f"{wednesday_start} - {wednesday_end}"})
        else:
            days_open.append({"day":"Wednesday", "timing": "Close"})
        if thursday_start and thursday_end:
            days_open.append({"day":"Thursday", "timing": f"{thursday_start} - {thursday_end}"})
        else:
            days_open.append({"day":"Thursday", "timing": "Close"})
        if friday_start and friday_end:
            days_open.append({"day":"Friday", "timing": f"{friday_start} - {friday_end}"})
        else:
            days_open.append({"day":"Friday", "timing": "Close"})
        if saturday_start and saturday_end:
            days_open.append({"day":"Saturday", "timing": f"{saturday_start} - {saturday_end}"})
        else:
            days_open.append({"day":"Saturday", "timing": "Close"})

        company_info.working_days = str(days_open)
        if request.FILES.get('profile_pic'):
            company_info.profile_pic = request.FILES.get('profile_pic')

        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        print("done")
        if not User.objects.get(id=company_info.user_id).check_password(current_password):
            messages.error(request, 'Incorrect current password')
            return redirect(self.success_url)

        if new_password:
            company_info.user.password = new_password
            company_info.user.save()


        company_info.save()
        if CompanyInfo.objects.get(user=self.request.user).profile_pic:
            request.session["profile_pic"] = str(CompanyInfo.objects.get(user=self.request.user).profile_pic)
        else:
            request.session["profile_pic"] = ""
        messages.success(request, 'Profile updated successfully')
        return redirect(self.success_url)

# Convert the file size to a human-readable format (e.g., KB, MB, GB)
def convert_size(size_in_bytes):
    size_units = ["bytes", "KB", "MB", "GB"]
    size = size_in_bytes
    unit = 0
    while size >= 1024 and unit < len(size_units) - 1:
        size /= 1024
        unit += 1
    return f"{size:.2f} {size_units[unit]}"

