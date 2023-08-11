from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from company.models import Job, CompanyInfo, PricingPlan, JobCategory, JobType, Location

@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(JobType)
class JobTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(PricingPlan)
class CompanyInfoAdmin(admin.ModelAdmin):
    pass

@admin.register(Location)
class Location(admin.ModelAdmin):
    pass

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'location', 'established','approve_button')
    search_fields = ('company_name', 'user__username', 'location')
    readonly_fields = ('user',)
    list_filter = ('user__is_active',)


    def has_add_permission(self, request):
        return False
    
    def approve_button(self, obj):
        if not obj.user.is_active:
            return format_html(f"""<a class="button" href="/co_approved?job_id={obj.id}">Approve</a>""")
        else:
            return format_html(f"""<a class="button" style="background-color:red" href="/co_disapproved?job_id={obj.id}">DisApprove</a>""")
        return '-'  

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'categories', 'get_company_name_link', 'is_approved', 'time_ago', 'approve_button')
    list_filter = ('is_approved','categories',)
    readonly_fields = ('posted_date', 'time_ago')
    search_fields = ('job_title', 'categories', 'company__company_name')
    date_hierarchy = 'posted_date'
    list_per_page = 20

    def time_ago(self, obj):
        return obj.time_ago
    time_ago.short_description = 'Posted'
    time_ago.admin_order_field = 'posted_date'

    def has_delete_permission(self, request, obj=None):
        return False

    def get_company_name_link(self, obj):
        company_info = obj.company
        company_name = company_info.company_name
        # Get the current URL
        current_url = reverse('admin:index')
        # Construct the company detail URL based on the current URL
        company_detail_url = f"{current_url.rstrip('/')}/{company_info._meta.app_label}/{company_info._meta.model_name}/{company_info.pk}/change/"
        return format_html('<a href="{}">{}</a>', company_detail_url, company_name)
    get_company_name_link.short_description = 'Company Name'
    get_company_name_link.admin_order_field = 'company__company_name'

    def approve_button(self, obj):
        if not obj.is_approved:
            return format_html(f"""<a class="button" href="/job_approved?job_id={obj.id}">Approve</a>""")
        else:
            return format_html(f"""<a class="button" style="background-color:red" href="/job_disapproved?job_id={obj.id}">DisApprove</a>""")
        return '-'  
    approve_button.allow_tags = True