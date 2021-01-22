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
from Main import views, employer, message, profile, response, report, tools
# from django.conf.urls.static import static
# from django.conf import settings

urlpatterns = [
    path('', views.index, name='index', ),
    path('admin/', admin.site.urls),
    path('login/', views.login, name='login', ),
    path('logout/', views.logout, name='logout', ),
    path('emps/', tools.temp_emp_list, name='emps', ),
    path('emp/all/', employer.employer_all, name='all', ),
    path('emp/draft/', employer.employer_draft, name='draft', ),
    path('emp/check/', employer.employer_check, name='check', ),
    path('emp/work/', employer.employer_work, name='work', ),
    path('emp/ready/', employer.employer_ready, name='ready', ),
    path('emp/closed/', employer.employer_closed, name='closed', ),
    path('load/', employer.emp_load, name='load', ),
    path('upload/', employer.emp_upload, name='upload', ),
    path('export/', tools.export_to_spreadsheet, name='export', ),
    path('emp/new/', employer.employer_new, name='new', ),
    path('emp/find/', employer.emp_find, name='find', ),
    path('emp/<int:employer_id>/', employer.employer_view, name='emp', ),
    path('emp/<int:employer_id>/audit/', employer.employer_audit, name='audit', ),
    path('emp/<int:employer_id>/print/', employer.employer_print, name='print', ),
    path('emp/<int:employer_id>/edit/', employer.employer_edit, name='edit', ),
    path('emp/<int:employer_id>/save/', employer.employer_save, name='save', ),
    path('emp/<int:employer_id>/delete/', employer.employer_delete, name='delete', ),
    path('emp/<int:employer_id>/close/', employer.employer_close, name='close', ),
    path('emp/<int:employer_id>/event/', tools.event_add, name='event', ),
    path('emp/<int:employer_id>/notify/', tools.notify_add, name='notify', ),
    path('arch/new/', tools.temp_arch_new, name='arch', ),
    path('arch/<int:employer_id>/edit/', tools.employer_arch_edit, name='archedit', ),
    path('arch/<int:employer_id>/save/', tools.employer_arch_save, name='archsave', ),
    path('inf/<int:inf_id>/delete/', tools.inf_delete, name='infdelete', ),
    path('notify/<int:notify_id>/delete/', tools.notify_delete, name='notifydelete', ),
    path('create/<int:temp_employer_id>/', tools.create_temp_emp, name='create', ),
    path('profile/list/', profile.profile_list, name='profile_list', ),
    path('profile/block/', profile.profile_block, name='profile_block', ),
    path('profile/unblock/', profile.profile_unblock, name='profile_unblock', ),
    path('profile/role/', profile.profile_role, name='profile_role', ),
    path('send/', tools.send_email, name='send', ),
    path('message/list/', message.message_list, name='message_list', ),
    path('message/<int:message_id>/read/', message.message_read, name='message_read', ),
    path('report/list/', report.report_list, name='report_list', ),
    path('report/month/', report.report_month, name='report_month', ),
    path('report/date/', report.report_date, name='report_date', ),
    path('response/list/', response.response_list, name='response_list', ),
    path('response/set/', response.response_set, name='response_set', ),
]

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
