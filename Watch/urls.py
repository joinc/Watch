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
from Main import views, employer, message, profile, response, report, tools, information, notify
# from django.conf.urls.static import static
# from django.conf import settings

urlpatterns = [
    path('', views.index, name='index', ),
    path('admin/', admin.site.urls),
    path('login/', views.login, name='login', ),
    path('logout/', views.logout, name='logout', ),
    path('send/', tools.send_email, name='send', ),
    path('employer/temp/list/', employer.employer_temp_list, name='emps', ),
    path('employer/new/', employer.employer_create, name='employer_new', ),
    path('employer/load/', employer.emp_load, name='employer_load', ),
    path('employer/all/', employer.employer_all, name='employer_all', ),
    path('employer/draft/', employer.employer_draft, name='employer_draft', ),
    path('employer/check/', employer.employer_check, name='employer_check', ),
    path('employer/work/', employer.employer_work, name='employer_work', ),
    path('employer/ready/', employer.employer_ready, name='employer_ready', ),
    path('employer/closed/', employer.employer_closed, name='employer_closed', ),
    path('employer/upload/', employer.emp_upload, name='employer_upload', ),
    path('employer/export/', employer.export_to_spreadsheet, name='employer_export', ),
    path('employer/find/', employer.employer_find, name='employer_find', ),
    path('employer/status_check', employer.employer_status_sync, name='employer_status_check', ),
    path('employer/<int:employer_id>/view/', employer.employer_view, name='employer_view', ),
    path('employer/<int:employer_id>/audit/', employer.employer_audit, name='employer_audit', ),
    path('employer/<int:employer_id>/print/', employer.employer_print, name='employer_print', ),
    path('employer/<int:employer_id>/edit/', employer.employer_edit, name='employer_edit', ),
    path('employer/<int:employer_id>/save/', employer.employer_save, name='employer_save', ),
    path('employer/<int:employer_id>/delete/', employer.employer_delete, name='employer_delete', ),
    path('employer/<int:employer_id>/close/', employer.employer_close, name='employer_close', ),
    path('employer/<int:employer_id>/event/', employer.event_add, name='event', ),
    path('employer/<int:employer_id>/notify/', employer.notify_add, name='notify', ),
    path('employer/arch/new/', employer.temp_arch_new, name='archive', ),
    path('employer/arch/<int:employer_id>/edit/', employer.employer_arch_edit, name='archive_edit', ),
    path('employer/arch/<int:employer_id>/save/', employer.employer_arch_save, name='archive_save', ),
    path('information/<int:employer_id>/create/', information.information_create, name='information_create', ),
    path('information/<int:information_id>/delete/', information.information_delete, name='information_delete', ),
    path('notify/<int:employer_id>/create/', notify.notify_create, name='notify_create', ),
    path('notify/<int:notify_id>/delete/', notify.notify_delete, name='notify_delete', ),
    path('create/<int:temp_employer_id>/', employer.create_temp_emp, name='create', ),
    path('profile/list/', profile.profile_list, name='profile_list', ),
    path('profile/block/', profile.profile_block, name='profile_block', ),
    path('profile/unblock/', profile.profile_unblock, name='profile_unblock', ),
    path('profile/role/', profile.profile_role, name='profile_role', ),
    path('message/list/', message.message_list, name='message_list', ),
    path('message/<int:message_id>/read/', message.message_read, name='message_read', ),
    path('report/list/', report.report_list, name='report_list', ),
    path('report/month/', report.report_month, name='report_month', ),
    path('report/date/', report.report_date, name='report_date', ),
    path('response/list/', response.response_list, name='response_list', ),
    path('response/set/', response.response_set, name='response_set', ),
]

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
