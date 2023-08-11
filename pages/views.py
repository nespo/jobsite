from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from .models import User, UserInfo, UserProjects
from django.http import JsonResponse
from company.models import CompanyInfo, CompanyGallery, Job
from django.db.models import Q
from django.core.mail import EmailMessage
from notifications.signals import notify
from django.core.paginator import Paginator

from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from .token import account_activation_token

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from company.models import PricingPlan, JobCategory, JobType, Job, Location

from datetime import datetime, timedelta
import re
from django.template.defaulttags import register

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

# Jobs
class JobList(TemplateView):
    template_name = "pages/jobs/job-list.html"
    paginate_by = 10  # Number of jobs per page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job_list = None
        try:
            if self.request.user.is_company:
                job_list = Job.objects.filter(~Q(user=self.request.user)).order_by('id').reverse()
            else:
                job_list = Job.objects.order_by('id').reverse()
        except:
            job_list = Job.objects.order_by('id').reverse()
        context['job_list'] = job_list
        for i in range(len(context['job_list'])):
            if context['job_list'][i].categories:
                context['job_list'][i].categories =  context['job_list'][i].categories.split(',')

         # Apply pagination
        paginator = Paginator(job_list, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        categories = JobCategory.objects.all()
        location = Location.objects.all()

        context['categories'] = categories
        context['job_list'] = page_obj
        context['locations'] = location

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = ""
        search = request.POST.get('search')
        region = request.POST.get('location')
        expertise = request.POST.get('expertise')
        list_of_search = []
        jobs_info_list = []

        if region=="All" and expertise=="All" and search=="":
            list_of_search = Job.objects.filter(~Q(user_id=self.request.user.id)).all()

        else:
            if search != "" and region=="All" and expertise=="All":
                try:
                    if self.request.user.is_company:
                        jobs_info_list = Job.objects.filter((Q(job_title__contains=search)) & ~Q(user_id=self.request.user.id)).all()
                    else:
                        jobs_info_list = Job.objects.filter(Q(job_title__contains=search)).all()
                except:
                    jobs_info_list = Job.objects.filter(Q(job_title__contains=search)).all()
                list_of_search.extend(jobs_info_list)

            elif search=="" and region!="All" and expertise=="All":
                try:
                    if self.request.user.is_company:
                        jobs_info_list = Job.objects.filter((Q(country=region)) & ~Q(user_id=self.request.user.id)).all()
                    else:
                        jobs_info_list = Job.objects.filter(Q(country=region)).all()
                except:
                    jobs_info_list = Job.objects.filter(Q(country=region)).all()

                list_of_search.extend(jobs_info_list)


            elif search=="" and region=="All" and expertise!="All":
                try:

                    if self.request.user.is_company:
                        jobs_info_list = Job.objects.filter((Q(categories=expertise)) & ~Q(user_id=self.request.user.id)).all()
                    else:
                        jobs_info_list = Job.objects.filter(Q(categories=expertise)).all()
                except:
                    jobs_info_list = Job.objects.filter(Q(categories=expertise)).all()

                list_of_search.extend(jobs_info_list)

            elif search=="" and region!="All" and expertise!="All":
                try:

                    if self.request.user.is_company:
                        jobs_info_list = Job.objects.filter((Q(categories=expertise)) & (Q(country=region)) & ~Q(user_id=self.request.user.id)).all()
                    else:
                        jobs_info_list = Job.objects.filter(Q(categories=expertise) & Q(country=region)).all()
                except:
                    jobs_info_list = Job.objects.filter(Q(categories=expertise) & Q(country=region)).all()

                list_of_search.extend(jobs_info_list)

            elif search!="" and region!="All" and expertise!="All":
                try:

                    if self.request.user.is_company:
                        jobs_info_list = Job.objects.filter((Q(categories=expertise)) & (Q(country=region)) & (Q(job_title__contains=search)) & ~Q(user_id=self.request.user.id)).all()
                    else:
                        jobs_info_list = Job.objects.filter(Q(categories=expertise) & Q(country=region) & (Q(job_title__contains=search))).all()
                except:
                    jobs_info_list = Job.objects.filter(Q(categories=expertise) & Q(country=region) & (Q(job_title__contains=search))).all()

                list_of_search.extend(jobs_info_list)

            elif search!="" and region!="All" and expertise=="All":
                try:

                    if self.request.user.is_company:
                        jobs_info_list = Job.objects.filter((Q(country=region)) & (Q(job_title__contains=search)) & ~Q(user_id=self.request.user.id)).all()
                    else:
                        jobs_info_list = Job.objects.filter(Q(country=region) & (Q(job_title__contains=search))).all()
                except:
                    jobs_info_list = Job.objects.filter(Q(country=region) & (Q(job_title__contains=search))).all()

                list_of_search.extend(jobs_info_list)

            elif search!="" and region=="All" and expertise!="All":
                try:

                    if self.request.user.is_company:
                        jobs_info_list = Job.objects.filter((Q(categories=expertise)) & (Q(job_title__contains=search)) & ~Q(user_id=self.request.user.id)).all()
                    else:
                        jobs_info_list = Job.objects.filter(Q(categories=expertise) & (Q(job_title__contains=search))).all()
                except:
                    jobs_info_list = Job.objects.filter((Q(categories=expertise)) & (Q(job_title__contains=search))).all()

                list_of_search.extend(jobs_info_list)



        jobs_info_list = list(set(list_of_search))


        for job in jobs_info_list:

            data += f"""

            <div class="job-box card mt-5">

                <div class="p-4">
                    <div class="row align-items-center">
                        <div class="col-md-2">
                            <div class="text-center mb-4 mb-lg-0">
                                <a href=/pages/company-details/{job.company_id}/><img src={'images/featured-job/img-01.png' if not job.company.profile_pic else f'/{job.company.profile_pic}'} alt="" class="img-fluid rounded-3"></a>
                            </div>
                        </div>
                        <!--end col-->
                        <div class="col-md-3">
                            <div class="mb-2 mb-md-0">
                                <h5 class="fs-18 mb-0"><a href=/pages/job-details/{job.id}/ class="text-dark">{ job.job_title }</a></h5>
                                <p class="text-muted fs-14 mb-0">{ job.designation }</p>
                            </div>
                        </div>
                        <!--end col-->
                        <div class="col-md-3">
                            <div class="d-flex mb-2">
                                <div class="flex-shrink-0">
                                    <i class="mdi mdi-map-marker text-primary me-1"></i>
                                </div>
                                <p class="text-muted"> {job.country }</p>
                            </div>
                        </div>
                        <!--end col-->
                        <div class="col-md-2">
                            <div class="d-flex mb-0">
                                <div class="flex-shrink-0">
                                    <i class="uil uil-clock-three text-primary me-1"></i>
                                </div>
                                <p class="text-muted mb-0"> { job.time_ago } </p>
                            </div>
                        </div>
                        <!--end col-->
                        <div class="col-md-2">
                            <div>
                                <span class="badge bg-soft-success fs-13 mt-1">{job.job_type}</span>
                            </div>
                        </div>
                        <!--end col-->
                    </div>
                    <!--end row-->
                </div>
                <div class="p-3 bg-light">
                    <div class="row justify-content-between">
                        <div class="col-md-4">
                            <div>
                                <p class="text-muted mb-0"><span class="text-dark">Salary : </span>{ job.salary } $</p>
                            </div>
                        </div>
                        <!--end col-->

                        <!--end col-->
                    </div>
                    <!--end row-->
                </div>
            </div>

            """

        return JsonResponse({"data": data})



class SearchedJobList(TemplateView):
    template_name = "pages/jobs/job-list.html"
    paginate_by = 10  # Number of jobs per page

    def post(self, request, *args, **kwargs):
        work_experience = request.POST.getlist("exp_list")
        job_type = request.POST.get("job_type")
        posted_date = request.POST.getlist("date_posted")
        all_jobs_searched = []
        query = Job.objects.filter(~Q(user_id=self.request.user.id)).all()
        if job_type!="":
            query = query.filter(Q(job_type=job_type)).all()
        if len(work_experience)>0:
            query1 = query.filter(
            (Q(experience_req__isnull=True)|Q(experience_req=0)) if 'no experience' in work_experience else Q()
            | Q(experience_req__lte=3) if '3 years' in work_experience else Q()
            | Q(experience_req__range=(3, 6)) if '3-6 years' in work_experience else Q()
            | Q(experience_req__gt=6) if 'more than 6' in work_experience else Q()
            )
            all_jobs_searched.extend(query1)


        all_jobs_searched = list(set(all_jobs_searched))
        data = ""
        for job in all_jobs_searched:

            data += f"""

            <div class="job-box card mt-5">

                <div class="p-4">
                    <div class="row align-items-center">
                        <div class="col-md-2">
                            <div class="text-center mb-4 mb-lg-0">
                                <a href=/pages/company-details/{job.company_id}/><img src={'images/featured-job/img-01.png' if not job.company.profile_pic else f'/{job.company.profile_pic}'} alt="" class="img-fluid rounded-3"></a>
                            </div>
                        </div>
                        <!--end col-->
                        <div class="col-md-3">
                            <div class="mb-2 mb-md-0">
                                <h5 class="fs-18 mb-0"><a href=/pages/job-details/{job.id}/ class="text-dark">{ job.job_title }</a></h5>
                                <p class="text-muted fs-14 mb-0">{ job.designation }</p>
                            </div>
                        </div>
                        <!--end col-->
                        <div class="col-md-3">
                            <div class="d-flex mb-2">
                                <div class="flex-shrink-0">
                                    <i class="mdi mdi-map-marker text-primary me-1"></i>
                                </div>
                                <p class="text-muted"> {job.country }</p>
                            </div>
                        </div>
                        <!--end col-->
                        <div class="col-md-2">
                            <div class="d-flex mb-0">
                                <div class="flex-shrink-0">
                                    <i class="uil uil-clock-three text-primary me-1"></i>
                                </div>
                                <p class="text-muted mb-0"> { job.time_ago } </p>
                            </div>
                        </div>
                        <!--end col-->
                        <div class="col-md-2">
                            <div>
                                <span class="badge bg-soft-success fs-13 mt-1">{job.job_type}</span>
                            </div>
                        </div>
                        <!--end col-->
                    </div>
                    <!--end row-->
                </div>
                <div class="p-3 bg-light">
                    <div class="row justify-content-between">
                        <div class="col-md-4">
                            <div>
                                <p class="text-muted mb-0"><span class="text-dark">Salary : </span>{ job.salary } $</p>
                            </div>
                        </div>
                        <!--end col-->

                        <!--end col-->
                    </div>
                    <!--end row-->
                </div>
            </div>

            """

        return JsonResponse({"data": data})

class FilterJobList(TemplateView):
    template_name = "pages/jobs/job-list.html"
    paginate_by = 10  # Number of jobs per page

    def post(self, request, *args, **kwargs):
        context = {}

        search = request.POST.get('search-field')
        region = request.POST.get('choices-single-location')
        expertise = request.POST.get('choices-single-categories')

        # jobs_info_list = Job.objects.filter().all()
        job_list = None
        list_of_search = []
        jobs_info_list = []

        if region=="All" and expertise=="All" and search=="":
            list_of_search = Job.objects.filter(~Q(user_id=self.request.user.id)).all()

        else:
            if search != "" and region=="All" and expertise=="All":
                try:
                    if self.request.user.is_company:
                        jobs_info_list = Job.objects.filter((Q(job_title__contains=search)) & ~Q(user_id=self.request.user.id)).all()
                    else:
                        jobs_info_list = Job.objects.filter(Q(job_title__contains=search)).all()
                except:
                    jobs_info_list = Job.objects.filter(Q(job_title__contains=search)).all()
                list_of_search.extend(jobs_info_list)

            elif search=="" and region!="All" and expertise=="All":
                try:
                    if self.request.user.is_company:
                        jobs_info_list = Job.objects.filter((Q(country=region)) & ~Q(user_id=self.request.user.id)).all()
                    else:
                        jobs_info_list = Job.objects.filter(Q(country=region)).all()
                except:
                    jobs_info_list = Job.objects.filter(Q(country=region)).all()

                list_of_search.extend(jobs_info_list)


            elif search=="" and region=="All" and expertise!="All":
                try:

                    if self.request.user.is_company:
                        jobs_info_list = Job.objects.filter((Q(categories=expertise)) & ~Q(user_id=self.request.user.id)).all()
                    else:
                        jobs_info_list = Job.objects.filter(Q(categories=expertise)).all()
                except:
                    jobs_info_list = Job.objects.filter(Q(categories=expertise)).all()

                list_of_search.extend(jobs_info_list)

            elif search=="" and region!="All" and expertise!="All":
                try:

                    if self.request.user.is_company:
                        jobs_info_list = Job.objects.filter((Q(categories=expertise)) & (Q(country=region)) & ~Q(user_id=self.request.user.id)).all()
                    else:
                        jobs_info_list = Job.objects.filter(Q(categories=expertise) & Q(country=region)).all()
                except:
                    jobs_info_list = Job.objects.filter(Q(categories=expertise) & Q(country=region)).all()

                list_of_search.extend(jobs_info_list)

            elif search!="" and region!="All" and expertise!="All":
                try:

                    if self.request.user.is_company:
                        jobs_info_list = Job.objects.filter((Q(categories=expertise)) & (Q(country=region)) & (Q(job_title__contains=search)) & ~Q(user_id=self.request.user.id)).all()
                    else:
                        jobs_info_list = Job.objects.filter(Q(categories=expertise) & Q(country=region) & (Q(job_title__contains=search))).all()
                except:
                    jobs_info_list = Job.objects.filter(Q(categories=expertise) & Q(country=region) & (Q(job_title__contains=search))).all()

                list_of_search.extend(jobs_info_list)

            elif search!="" and region!="All" and expertise=="All":
                try:

                    if self.request.user.is_company:
                        jobs_info_list = Job.objects.filter((Q(country=region)) & (Q(job_title__contains=search)) & ~Q(user_id=self.request.user.id)).all()
                    else:
                        jobs_info_list = Job.objects.filter(Q(country=region) & (Q(job_title__contains=search))).all()
                except:
                    jobs_info_list = Job.objects.filter(Q(country=region) & (Q(job_title__contains=search))).all()

                list_of_search.extend(jobs_info_list)

            elif search!="" and region=="All" and expertise!="All":
                try:

                    if self.request.user.is_company:
                        jobs_info_list = Job.objects.filter((Q(categories=expertise)) & (Q(job_title__contains=search)) & ~Q(user_id=self.request.user.id)).all()
                    else:
                        jobs_info_list = Job.objects.filter(Q(categories=expertise) & (Q(job_title__contains=search))).all()
                except:
                    jobs_info_list = Job.objects.filter((Q(categories=expertise)) & (Q(job_title__contains=search))).all()

                list_of_search.extend(jobs_info_list)



        jobs_info_list = list(set(list_of_search))
        context['job_list'] = jobs_info_list
        for i in range(len(context['job_list'])):
            if context['job_list'][i].categories:
                context['job_list'][i].categories =  context['job_list'][i].categories.split(',')

         # Apply pagination
        paginator = Paginator(jobs_info_list, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        categories = JobCategory.objects.all()
        locations = Location.objects.all()

        context['categories'] = categories
        context['job_list'] = page_obj
        context['locations'] = locations

        return render(request, self.template_name, context)

    

class MyJobs(TemplateView):
    template_name = "pages/jobs/my-jobs.html"
    paginate_by = 10  # Number of jobs per page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_jobs = Job.objects.filter(Q(user=self.request.user)).order_by('id').reverse()
        context["job_list"] = my_jobs
        for i in range(len(context['job_list'])):
            if context['job_list'][i].categories:
                context['job_list'][i].categories =  context['job_list'][i].categories.split(',')

         # Apply pagination
        paginator = Paginator(my_jobs, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        categories = JobCategory.objects.all()

        context['categories'] = categories
        context['job_list'] = page_obj

        return context


    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

class EditJob(TemplateView):
    template_name = "pages/jobs/edit-job.html"
    job_post_detail = None
    def get_context_data(self, id, **kwargs):
        context = super().get_context_data(**kwargs)
        job_info_list = Job.objects.get(id=id)
        locations = Location.objects.all()
        EditJob.job_post_detail = job_info_list
        context['company_info'] = job_info_list.company
        context['job_info_list'] = job_info_list
        context['locations'] = locations
        job_skills_list = context['job_info_list'].job_skills.lower().split(",")
        try:
            context['job_info_list'].qualification =  "".join(eval(context['job_info_list'].qualification))
        except:
            context['job_info_list'].qualification =  ""
        context['job_info_list'].responsibilities = "".join(eval(context['job_info_list'].responsibilities))
        context['job_info_list'].skillsandxperience = "".join(eval(context['job_info_list'].skillsandxperience))
        categories = JobCategory.objects.all()
        job_type = JobType.objects.all()

        context["categories"] = categories
        context['job_types'] = job_type
        context["job_id"] = id
        return context

    def get(self, request, id, *args, **kwargs):
        context = self.get_context_data(id)

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if request.POST.get("type_job") == "delete":
            EditJob.job_post_detail.delete()
            return redirect("my-jobs")
        else:
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

            EditJob.job_post_detail.job_title = job_title
            EditJob.job_post_detail.job_description = job_description
            EditJob.job_post_detail.email = email
            EditJob.job_post_detail.phone_number = phone_number
            EditJob.job_post_detail.categories = categories
            EditJob.job_post_detail.designation = designation
            EditJob.job_post_detail.salary = salary
            EditJob.job_post_detail.job_skills = job_skills
            EditJob.job_post_detail.last_date = last_date
            EditJob.job_post_detail.country = country
            EditJob.job_post_detail.city = city
            EditJob.job_post_detail.zipcode = zipcode
            EditJob.job_post_detail.job_image = image
            EditJob.job_post_detail.responsibilities = responsibilities
            EditJob.job_post_detail.skillsandxperience = skillsandxperience
            EditJob.job_post_detail.experience_req = exp
            EditJob.job_post_detail.basic_qualification = basic_qualification
            EditJob.job_post_detail.qualification = qualification
            EditJob.job_post_detail.ind_type = ind_type
            EditJob.job_post_detail.save()

            return redirect("my-jobs")

class DeleteJob(TemplateView):
    template_name="pages/jobs/my-jobs.html"
    def get(self, request, id, *args, **kwargs):
        job = Job.objects.get(id=id)
        job.delete()
        return redirect('my-jobs')
class JobList2(TemplateView):
    template_name = "pages/jobs/job-list-2.html"
class JobGrid(TemplateView):
    template_name = "pages/jobs/job-grid.html"
class JobGrid2(TemplateView):
    template_name = "pages/jobs/job-grid-2.html"
class JobDetails(TemplateView):
    template_name = "pages/jobs/job-details.html"
    job_post_detail = None
    def get_context_data(self, id, **kwargs):
        context = super().get_context_data(**kwargs)
        job_info_list = Job.objects.get(id=id)
        JobDetails.job_post_detail = job_info_list
        context['company_info'] = job_info_list.company
        context['job_info_list'] = job_info_list
        job_skills_list = context['job_info_list'].job_skills.lower().split(",")
        context['job_info_list'].job_skills = context['job_info_list'].job_skills.split(",")
        context['job_info_list'].qualification = eval(context['job_info_list'].qualification)
        context['job_info_list'].responsibilities = eval(context['job_info_list'].responsibilities)
        context['job_info_list'].skillsandxperience = eval(context['job_info_list'].skillsandxperience)
        related_jobs_list = []
        for job in Job.objects.filter(~Q(id=id)).all():
            if "," in job.job_skills:
                job_cat = job.job_skills.split(",")
            if any(i.lower() in job_skills_list for i in job_cat):
                related_jobs_list.append(job)
        print(related_jobs_list)
        context['related_jobs'] = related_jobs_list

        context["fb_share_link"] = f"https://www.facebook.com/sharer/sharer.php?u=https://testdeveloper110.pythonanywhere.com/pages/job-details/{id}/"
        context["linkedin_share_link"] = f"https://www.linkedin.com/sharing/share-offsite/?url=https://testdeveloper110.pythonanywhere.com/pages/job-details/{id}/"

        return context

    def get(self, request, id, *args, **kwargs):
        context = self.get_context_data(id)

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user_detail = UserInfo.objects.get(user_id=request.user.id)
        if user_detail.job_apply_count == 0:
            return redirect("pricing")

        name = request.POST.get("cand_name")
        mail = request.POST.get("cand_mail")
        message = request.POST.get("cand_message")
        uploaded_file = request.FILES.get("cand_resume")
        email = EmailMessage(
            f'Application for the Job {JobDetails.job_post_detail.job_title}',
            f' Name: {name} \n email: {mail} \n message: {message}',
            "confirmation@webnike.com",    #From Email
            [JobDetails.job_post_detail.user.email])
        email.attach(uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)
        email.send()
        sender = request.user
        receiver = JobDetails.job_post_detail.user
        notify.send(sender, recipient=receiver, verb='Message', description="hellooooooo")
        user_detail.job_apply_count -= 1
        user_detail.save()
        return redirect(f"/pages/job-details/{JobDetails.job_post_detail.id}/")




class JobCategories(TemplateView):
    template_name = "pages/jobs/job-categories.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job_categories = JobCategory.objects.all()
        print(job_categories)
        job_categories = [job_categories[i:i+8] for i in range(0,len(job_categories), 8)]
        print(job_categories)
        context["categories"] = job_categories
        return context

class CandidateList(TemplateView):
    template_name = "pages/candidates-company/candidate-list.html"
    paginate_by = 10  # Number of candidates per page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_info_list = UserInfo.objects.filter(~Q(user_id=self.request.user.id)).exclude(first_name__isnull=True).exclude(last_name__isnull=True).all()
        locations = Location.objects.all()
        context['locations'] = locations
        context['user_info_list'] = user_info_list
        for i in range(len(context['user_info_list'])):
            if context['user_info_list'][i].categories:
                context['user_info_list'][i].categories =  context['user_info_list'][i].categories.split(',')
        categories = JobCategory.objects.all()

        context['categories'] = categories
         # Apply pagination
        paginator = Paginator(user_info_list, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = ""
        search = request.POST.get('search')
        region = request.POST.get('location')
        expertise = request.POST.get('expertise')
        list_of_search = []
        users_info_list = []


        if region=="All" and expertise=="All" and search=="":

             list_of_search = UserInfo.objects.all()

        else:
            if search != "" and region=="All" and expertise=="All":
                try:
                    if self.request.user.is_company:
                        users_info_list = UserInfo.objects.filter((Q(first_name__contains=search)|Q(last_name__contains=search)) & ~Q(user_id=self.request.user.id)).all()
                    else:
                        users_info_list = UserInfo.objects.filter((Q(first_name__contains=search)|Q(last_name__contains=search))).all()
                except:
                    users_info_list = UserInfo.objects.filter((Q(first_name__contains=search)|Q(last_name__contains=search))).all()
                list_of_search.extend(users_info_list)

            elif search=="" and region!="All" and expertise=="All":
                try:
                    if self.request.user.is_company:
                        users_info_list = UserInfo.objects.filter((Q(location=region)) & ~Q(user_id=self.request.user.id)).all()
                    else:
                        users_info_list = UserInfo.objects.filter(Q(location=region)).all()
                except:
                    users_info_list = UserInfo.objects.filter(Q(location=region)).all()

                list_of_search.extend(users_info_list)


            elif search=="" and region=="All" and expertise!="All":
                try:

                    if self.request.user.is_company:
                        users_info_list = UserInfo.objects.filter((Q(profession=expertise)) & ~Q(user_id=self.request.user.id)).all()
                    else:
                        users_info_list = UserInfo.objects.filter(Q(profession=expertise)).all()
                except:
                    users_info_list = UserInfo.objects.filter(Q(profession=expertise)).all()

                list_of_search.extend(users_info_list)

            elif search=="" and region!="All" and expertise!="All":
                try:

                    if self.request.user.is_company:
                        users_info_list = UserInfo.objects.filter((Q(profession=expertise)) & (Q(location=region)) & ~Q(user_id=self.request.user.id)).all()
                    else:
                        users_info_list = UserInfo.objects.filter(Q(profession=expertise) & Q(location=region)).all()
                except:
                    users_info_list = UserInfo.objects.filter(Q(profession=expertise) & Q(location=region)).all()

                list_of_search.extend(users_info_list)

            elif search!="" and region!="All" and expertise!="All":
                try:

                    if self.request.user.is_company:
                        users_info_list = UserInfo.objects.filter((Q(profession=expertise)) & (Q(location=region)) & (Q(first_name__contains=search)|Q(last_name__contains=search)) & ~Q(user_id=self.request.user.id)).all()
                    else:
                        users_info_list = UserInfo.objects.filter(Q(profession=expertise) & Q(location=region) & (Q(first_name__contains=search)|Q(last_name__contains=search))).all()
                except:
                    users_info_list = UserInfo.objects.filter(Q(profession=expertise) & Q(location=region) & (Q(first_name__contains=search)|Q(last_name__contains=search))).all()

                list_of_search.extend(users_info_list)

            elif search!="" and region!="All" and expertise=="All":
                try:

                    if self.request.user.is_company:
                        users_info_list = UserInfo.objects.filter((Q(location=region)) & (Q(first_name__contains=search)|Q(last_name__contains=search)) & ~Q(user_id=self.request.user.id)).all()
                    else:
                        users_info_list = UserInfo.objects.filter(Q(location=region) & (Q(first_name__contains=search)|Q(last_name__contains=search))).all()
                except:
                    users_info_list = UserInfo.objects.filter(Q(location=region) & (Q(first_name__contains=search)|Q(last_name__contains=search))).all()

                list_of_search.extend(users_info_list)

            elif search!="" and region=="All" and expertise!="All":
                try:

                    if self.request.user.is_company:
                        users_info_list = UserInfo.objects.filter((Q(profession=expertise)) & (Q(first_name__contains=search)|Q(last_name__contains=search)) & ~Q(user_id=self.request.user.id)).all()
                    else:
                        users_info_list = UserInfo.objects.filter(Q(profession=expertise) & (Q(first_name__contains=search)|Q(last_name__contains=search))).all()
                except:
                    users_info_list = UserInfo.objects.filter((Q(profession=expertise)) & (Q(first_name__contains=search)|Q(last_name__contains=search))).all()

                list_of_search.extend(users_info_list)








        users_info_list = list(set(list_of_search))

        candidate_categories = ""

        for candidate in users_info_list:
            if candidate.user_id == self.request.user.id or not candidate.last_name or not candidate.first_name:
                continue
            if candidate.categories:
                candidate.categories = candidate.categories.split(',')
                for cat in candidate.categories:
                    candidate_categories += f'<span class="badge bg-soft-muted fs-14 mt-1">{cat}</span>'


            data += f"""                         <div class="candidate-list-box card mt-4">
                                                <div class="card-body p-4">
                                                    <div class="row align-items-center">
                                                        <div class="col-auto">
                                                            <div class="candidate-list-images">
                                                                <a href="javascript:void(0)"><img src={ '/static/images/profile.jpg' if not candidate.profile_pic else f'/{candidate.profile_pic}' } alt="" class="avatar-md img-thumbnail rounded-circle"></a>
                                                            </div>
                                                        </div><!--end col-->

                                                        <div class="col-lg-5">
                                                            <div class="candidate-list-content mt-3 mt-lg-0">
                                                                <h5 class="fs-19 mb-0"><a href=/pages/candidate-details/{candidate.id}/ class="primary-link">{ candidate.first_name } { candidate.last_name }</a> <span class="badge bg-success ms-1"><i class="mdi mdi-star align-middle"></i> 4.8</span></h5>
                                                                <p class="text-muted mb-2"> { candidate.profession }</p>
                                                                <ul class="list-inline mb-0 text-muted">
                                                                    <li class="list-inline-item">
                                                                        <i class="mdi mdi-map-marker"></i> { candidate.location }
                                                                    </li>
                                                                    {f'''<li class="list-inline-item">
                                                                        <i class="uil uil-wallet"></i> {candidate.salary} / hours
                                                                    </li>''' if candidate.salary else ''}
                                                                </ul>
                                                            </div>
                                                        </div><!--end col-->

                                                        <div class="col-lg-4">
                                                            <div class="mt-2 mt-lg-0">
                                                                {candidate_categories}
                                                            </div>
                                                        </div><!--end col-->
                                                    </div><!--end row-->
                                                </div>
                                            </div> <!--end card-->
                                       """
        return JsonResponse({"data": data})


class CandidateGrid(TemplateView):
    template_name = "pages/candidates-company/candidate-grid.html"
class CandidateDetails(TemplateView):
    template_name = "pages/candidates-company/candidate-details.html"
    def get_context_data(self, id, **kwargs):
        context = super().get_context_data(**kwargs)
        user_info_list = UserInfo.objects.get(id=id)
        context['user_info_list'] = user_info_list
        try:
            projects = UserProjects.objects.filter(user_id=user_info_list).all()
            context["projects"] = projects
        except UserProjects.DoesNotExist:
            context["projects"] = None
        context['email'] = User.objects.get(id=context["user_info_list"].user_id).email
        return context

    def get(self, request, id, *args, **kwargs):
        context = self.get_context_data(id)
        if context['user_info_list'].education_details:
            context['user_info_list'].education_details = eval(context['user_info_list'].education_details)
        if context['user_info_list'].experience_details:
            context['user_info_list'].experience_details = eval(context['user_info_list'].experience_details)
        if context['user_info_list'].skills:
            context['user_info_list'].skills = context['user_info_list'].skills.split(",")
        if context['user_info_list'].categories:
            context['user_info_list'].categories = " /".join(context['user_info_list'].categories.split(","))


        return render(request, self.template_name, context)

class CompanyList(TemplateView):
    template_name = "pages/candidates-company/company-list.html"
    paginate_by = 10  # Number of companies per page
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        companies_list = CompanyInfo.objects.filter(~Q(user_id=self.request.user.id)).exclude(company_name__isnull=True).all()
        locations = Location.objects.all()
        context['companies_list'] = companies_list
        job_count_dict = {}
        for company in companies_list:
            total_jobs = Job.objects.filter(company_id=company.id).count()
            job_count_dict[company.id] = total_jobs
        # Apply pagination
        paginator = Paginator(companies_list, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context["total_jobs"] = job_count_dict
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)







class CompanyDetails(TemplateView):
    template_name = "pages/candidates-company/company-details.html"


    def get_context_data(self, id, **kwargs):
        context = super().get_context_data(**kwargs)
        company_info_list = CompanyInfo.objects.get(id=id)
        jobs = Job.objects.filter(user=company_info_list.user_id).all()
        for i in range(len(jobs)):
            jobs[i].job_type = jobs[i].job_type.split(", ")
        company_info_list.working_days = eval(company_info_list.working_days)
        context['company_info_list'] = company_info_list
        context['jobs_list'] = jobs
        try:
            company_gallery = CompanyGallery.objects.filter(user_id=company_info_list).all()
            context["company_gallery"] = company_gallery
        except CompanyGallery.DoesNotExist:
            context["company_gallery"] = None
        context['email'] = User.objects.get(id=context["company_info_list"].user_id).email

        return context

    def get(self, request, id, *args, **kwargs):
        context = self.get_context_data(id)
        return render(request, self.template_name, context)





# Extra-Pages

from django.contrib.auth.hashers import make_password

class SignUp(TemplateView):
    template_name = "pages/extra-pages/sign-up.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        is_company = bool(request.POST.get('is_company'))
        try:
            if User.objects.filter(Q(email=email)|Q(username=username)).exists():
                error_message = "Username or Email already taken. Please choose a different username or email."
                return render(request, self.template_name, {'error_message': error_message})

            user = User(username=username, email=email, is_company=is_company)
            user.set_password(password)
            user.is_active = False
            user.save()
            if is_company:
                company_info = CompanyInfo(user=user)
                company_info.job_post_count = 50
                company_info.purchased_package = PricingPlan.objects.get(Q(for_company=True) & Q(name="Basic"))
                company_info.save()
            else:
                user_info = UserInfo(user=user)
                user_info.job_apply_count = 50
                user_info.purchased_package = PricingPlan.objects.get(Q(for_company=False) & Q(name="Basic"))
                user_info.save()

            # if not user.is_company:
            #     if UserInfo.objects.get(user_id=user.id).profile_pic:
            #         request.session["profile_pic"] = str(UserInfo.objects.get(user_id=user.id).profile_pic)
            #     else:
            #         request.session["profile_pic"] = ""

            # else:
            #     if CompanyInfo.objects.get(user_id=user.id).profile_pic:
            #         request.session["profile_pic"] = str(CompanyInfo.objects.get(user_id=user.id).profile_pic)
            #     else:
            #         request.session["profile_pic"] = ""

            # login(request, user)

            current_site = get_current_site(request)
            subject = 'Activate Your Jobcy Account'
            message = render_to_string('account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)

            messages.success(request, ('Please Confirm your email to complete registration.'))

            return redirect('sign-in')
        except:
            user = User.objects.get(username=username)
            print(user)
            if is_company:
                print(user.id)
                company_info = CompanyInfo.objects.get(user_id=user.id)
                company_info.delete()
            else:
                user_info = UserInfo.objects.get(user_id=user.id)
                user_info.delete()
            user.delete()
            return redirect('sign-in')



class ActivateAccount(TemplateView):

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = False
            user.profile.email_confirmed = True
            user.save()
            if not user.is_company:
                user_info = UserInfo.objects.get(user_id=user)
                user_info.purchased_package = PricingPlan.objects.get(Q(name="Basic") & Q(for_company=False))
                user_info.job_apply_count = user_info.purchased_package.jobs_count
                user_info.save()
            else:
                company_info = CompanyInfo.objects.get(user_id=user)
                company_info.purchased_package = PricingPlan.objects.get(Q(name="Basic") & Q(for_company=True))
                company_info.job_post_count = company_info.purchased_package.jobs_count
                company_info.save()

            login(request, user)
            messages.success(request, ('Your account have been confirmed.'))
            return redirect('sign-in')
        else:
            messages.warning(request, ('The confirmation link was invalid, possibly because it has already been used.'))
            return redirect('sign-in')


class Signin(TemplateView):
    template_name = "pages/extra-pages/sign-in.html"

    def get(self, request, *args, **kwargs):
        # Render the sign-in form
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            error_message = "Invalid username"
            return render(request, self.template_name, {'error_message': error_message})
        if user.check_password(password) and user.is_active:
                login(request, user)
                if not user.is_company:
                    if UserInfo.objects.get(user_id=user.id).profile_pic:
                        request.session["profile_pic"] = str(UserInfo.objects.get(user_id=user.id).profile_pic)
                    else:
                        request.session["profile_pic"] = ""

                else:
                    if CompanyInfo.objects.get(user_id=user.id).profile_pic:
                        request.session["profile_pic"] = str(CompanyInfo.objects.get(user_id=user.id).profile_pic)
                    else:
                        request.session["profile_pic"] = ""

                return redirect('index')

        error_message = "Invalid password or user not activated."
        return render(request, self.template_name, {'error_message': error_message})



class SignOut(TemplateView):
    template_name = "pages/extra-pages/sign-out.html"

    def get(self, request, *args, **kwargs):

        if "profile_pic" in request.session:
            del request.session["profile_pic"]

        logout(request)
        return render(request, self.template_name)



class ResetPassword(TemplateView):
    template_name = "pages/extra-pages/reset-password.html"
class ComingSoon(TemplateView):
    template_name = "pages/extra-pages/coming-soon.html"
class Error404(TemplateView):
    template_name = "pages/extra-pages/404-error.html"
class Components(TemplateView):
    template_name = "pages/extra-pages/components.html"

# Convert the file size to a human-readable format (e.g., KB, MB, GB)
def convert_size(size_in_bytes):
    size_units = ["bytes", "KB", "MB", "GB"]
    size = size_in_bytes
    unit = 0
    while size >= 1024 and unit < len(size_units) - 1:
        size /= 1024
        unit += 1
    return f"{size:.2f} {size_units[unit]}"