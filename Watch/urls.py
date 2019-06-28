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
    path('emps/', views.temp_emp_list, name='emps', ),
    path('all/', views.emp_all_list, name='all', ),
    path('draft/', views.emp_draft_list, name='draft', ),
    path('check/', views.emp_check_list, name='check', ),
    path('work/', views.emp_work_list, name='work', ),
    path('ready/', views.emp_ready_list, name='ready', ),
    path('closed/', views.emp_closed_list, name='closed', ),
    path('find/', views.emp_find_list, name='find', ),
    path('find/<int:page>/', views.emp_find_list, name='find', ),
    path('search/', views.emp_search, name='search', ),
    path('load/', views.emp_load, name='load', ),
    path('upload/', views.emp_upload, name='upload', ),
    path('export/', views.emp_export, name='export', ),
    path('emp/new/', employer.employer_new, name='new', ),
    path('emp/<int:employer_id>/', employer.employer_view, name='emp', ),
    path('emp/<int:employer_id>/audit/', employer.employer_audit, name='audit', ),
    path('emp/<int:employer_id>/print/', employer.employer_print, name='print', ),
    path('emp/<int:employer_id>/edit/', employer.employer_edit, name='edit', ),
    path('emp/<int:employer_id>/save/', employer.employer_save, name='save', ),
    path('emp/<int:employer_id>/delete/', employer.employer_delete, name='delete', ),
    path('emp/<int:employer_id>/close/', employer.employer_close, name='close', ),
    path('emp/<int:employer_id>/event/', views.event_add, name='event', ),
    path('emp/<int:employer_id>/notify/', views.notify_add, name='notify', ),
    path('arch/new/', views.temp_arch_new, name='arch', ),
    path('arch/<int:employer_id>/edit/', views.employer_arch_edit, name='archedit', ),
    path('arch/<int:employer_id>/save/', views.employer_arch_save, name='archsave', ),
    path('notify/<int:notify_id>/delete/', views.notify_delete, name='notifydelete', ),
    path('create/<int:temp_employer_id>/', views.create_temp_emp, name='create', ),
    path('users/', views.user_list, name='users', ),
    path('userrole/', views.user_role, name='userrole', ),
    path('send/', views.send_email, name='send', ),
    path('message/', message.message_list, name='messagelist', ),
    path('message/<int:message_id>/read/', message.message_read, name='messageread', ),
    path('report/list/', views.report_list, name='reportlist', ),
    path('report/view/', views.report_view, name='reportview', ),
    path('respons/', views.respons_list, name='responslist', ),
    path('responsset/', views.respons_set, name='responsset', ),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
