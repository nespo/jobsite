from django.urls import path
# urls.py
from contact import views

urlpatterns = [
    # Contact
    path('contact',views.ContactView.as_view(),name='contact'),
    path('job_approved',views.JobApproveView.as_view(),name='job_approved'),
    path('job_disapproved',views.JobDisApproveView.as_view(),name='job_disapproved'),
    path('co_disapproved',views.CoDisApproveView.as_view(),name='co_disapproved'),
    path('co_approved',views.CoApproveView.as_view(),name='co_approved'),
]

