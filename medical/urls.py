from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    # home page url
    path('', views.index, name='index'),

    # authentication urls
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('create_pdf', views.render_pdf_view, name='create_pdf'),

    # resetting password urls
    # reset password urls
    path('password_reset/',
         auth_views.PasswordResetView.as_view(),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),

    # business urls
    path('record_medicine', views.record_meds, name='record_medicine'),
    path('edit_medication/<int:id>', views.edit_medication, name='edit_medication'),
    path('update_medication/<int:id>', views.update_medication, name='update_medication'),
    path('delete_medication/<int:id>', views.delete_medication, name='delete_medication'),
    path('dashboard', views.dashboard, name="dashboard"),

    path('dash', views.dashi, name="dash"),
    path('about', views.about_view, name="about"),
    path('mails', views.sending_email, name="mails"),
    path('list_medicines', views.view_med, name='list_medicines'),
    path('edit_med/<int:id>', views.edit_med, name='edit_med'),
    path('search_med', views.search_med, name='search_med'),
    path('record_request', views.record_request, name='record_request'),
    path('list_requests', views.view_requests, name='list_requests'),
    path('list_responses', views.view_responses, name='list_responses'),
    path('list_returned', views.view_returned, name='list_returned'),
    path('returned', views.returned, name='returned'),
    path('list_approved', views.view_approved, name='list_approved'),
    path('temp', views.temps, name="temp"),
    path('main', views.main, name='main'),
    path('approve_report', views.approved_pdf, name='approve_report'),
    path('medicalApproval/<int:id>', views.medical_approval, name="medicalApproval"),
    path('medicalDisapproval/<int:id>', views.medical_disapproval, name="medicalDisapproval"),
    path('medicalReturned/<int:id>', views.medical_Returned, name="medicalReturned"),
    path('notification/<str:case>', views.notification, name="notification"),
   

    path('search_medicine', views.search_medication, name='search_medicine'),
    path('wait', views.wait, name='wait'),
    path('contact', views.contact_view, name='contact'),
    path('view_reports/<str:case>', views.print_pdf_for_all, name='print_pdf_for_all'),
    path('response_report/<str:case>', views.get_report, name='response_report'),
    path('approvedd_report/<str:case>', views.approvedd_report, name='approvedd_report'),
    path('print_approved/<str:case>', views.print_pdf_for_approved, name='print_approved'),
    path('directors', views.directors, name='directors'),
    path('search_director', views.search_director, name='search_director'),


]
