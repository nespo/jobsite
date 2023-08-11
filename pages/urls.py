from django.urls import path
# urls.py
from pages import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import ActivateAccount

urlpatterns = [
    # Jobs
    path('job-list', views.JobList.as_view(),name="job-list"),
    path('searched-job-list', views.SearchedJobList.as_view(),name="search-job-list"),
    path('filtered-job-list', views.FilterJobList.as_view(),name="filtered-job-list"),
    path('my-jobs', views.MyJobs.as_view(), name="my-jobs"),
    path('edit-job/<int:id>/', views.EditJob.as_view(), name="edit-job"),
    path('edit-job/', views.EditJob.as_view(), name="edit-delete-job"),
    path('delete-job/<int:id>/', views.DeleteJob.as_view(), name="delete-job"),
    path('job-list-2', views.JobList2.as_view(),name="job-list-2"),
    path('job-grid', views.JobGrid.as_view(),name="job-grid"),
    path('job-grid-2', views.JobGrid2.as_view(),name="job-grid-2"),
    path('job-details/<int:id>/', views.JobDetails.as_view(),name="job-details"),
    path('job-details', views.JobDetails.as_view(),name="job-detail"),
    path('job-categories', views.JobCategories.as_view(),name="job-categories"),

    # Candidates/Company
    path('candidate-list', views.CandidateList.as_view(),name="candidate-list"),
    path('candidate-grid', views.CandidateGrid.as_view(),name="candidate-grid"),
    path('candidate-details/<int:id>/', views.CandidateDetails.as_view(),name="candidate-details"),
    path('company-list', views.CompanyList.as_view(),name="company-list"),
    path('company-details/<int:id>/', views.CompanyDetails.as_view(),name="company-details"),

    # Extra-Pages
    path('sign-up', views.SignUp.as_view(),name="sign-up"),
    path('sign-in', views.Signin.as_view(),name="sign-in"),
    path('sign-out', views.SignOut.as_view(),name="sign-out"),
    path('reset-password', views.ResetPassword.as_view(),name="reset-password"),
    path('comingsoon', views.ComingSoon.as_view(),name="comingsoon"),
    path('404-error', views.Error404.as_view(),name="404-error"),
    path('components', views.Components.as_view(),name="components"),

    path('activate/<uidb64>/<token>/', ActivateAccount.as_view(), name='activate'),
]
