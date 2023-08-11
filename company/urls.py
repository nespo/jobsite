from django.urls import path
# urls.py
from company import views
urlpatterns = [
    path('about', views.About.as_view(),name="about"),
    path('services', views.Services.as_view(),name="services"),
    path('team', views.Team.as_view(),name="team"),
    path('pricing', views.Pricing.as_view(),name="pricing"),
    path('privacy-policy', views.PrivacyPolicy.as_view(),name="privacy-policy"),
    path('faqs', views.FAQs.as_view(),name="faqs"),


    path('process-payment', views.PaypalFormView.as_view(), name='process_payment'),
    path('payment-done', views.payment_done, name='payment_done'),
    path('payment-cancelled', views.payment_canceled, name='plan-cancelled'),
    path('update_Count', views.update_count, name='update_Count'),


]