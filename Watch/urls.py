"""Watch URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import path
from django.contrib import admin
from Main import views, employer, message
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index', ),
    path('admin/', admin.site.urls),
    path('login/', views.LoginFormView.as_view(), name='login', ),
    path('logout/', views.Logout, name='logout', ),
    path('emps/', views.TempEmpList, name='emps', ),
    path('check/', views.emp_check_list, name='check', ),
    path('ready/', views.emp_ready_list, name='ready', ),
    path('work/', views.emp_work_list, name='work', ),
    path('load/', views.emp_load, name='load', ),
    path('upload/', views.emp_upload, name='upload', ),
    path('emp/new/', employer.employer_new, name='new', ),
    path('emp/list/', employer.employer_list, name='list', ),
    path('emp/<int:Employer_id>/', employer.employer_view, name='emp', ),
    path('emp/<int:Employer_id>/audit/', employer.employer_audit, name='audit', ),
    path('emp/<int:Employer_id>/print/', employer.employer_print, name='print', ),
    path('emp/<int:Employer_id>/edit/', employer.employer_edit, name='edit', ),
    path('emp/<int:Employer_id>/save/', employer.employer_save, name='save', ),
    path('emp/<int:Employer_id>/delete/', employer.employer_delete, name='delete', ),
    path('emp/<int:Employer_id>/event/', views.EventAdd, name='event', ),
    path('emp/<int:Employer_id>/notify/', views.NotifyAdd, name='notify', ),
    path('arch/new/', views.TempArchNew, name='arch', ),
    path('arch/<int:Employer_id>/edit/', views.EmployerArchEdit, name='archedit', ),
    path('arch/<int:Employer_id>/save/', views.EmployerArchSave, name='archsave', ),
    path('notify/<int:Notify_id>/delete/', views.NotifyDelete, name='notifydelete', ),
    path('create/<int:TempEmployer_id>/', views.CreateTempEmp, name='create', ),
    path('users/', views.UserList, name='users', ),
    path('userrole/', views.UserRole, name='userrole', ),
    path('send/', views.SendEMail, name='send', ),
    path('message/', message.message_list, name='messagelist', ),
    path('message/<int:Message_id>/read/', message.message_read, name='messageread', ),
    path('respons/', views.ResponsList, name='responslist', ),
    path('responsset/', views.ResponsSet, name='responsset', ),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
