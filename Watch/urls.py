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
from Main import views, employer, message, response, report, information, notify, configure
# from django.conf.urls.static import static
# from django.conf import settings

urlpatterns = [
    path('', views.index, name='index', ),
    path('admin/', admin.site.urls),
    path('login/', views.login, name='login', ),
    path('logout/', views.logout, name='logout', ),
    path('configure/list/', configure.configure_list, name='configure_list', ),
    path('configure/employer/load/', configure.employer_load, name='employer_load', ),
    path('configure/widget/list/', configure.widget_list, name='widget_list', ),
    path('configure/email/send/', configure.send_email, name='send_email', ),
    path('configure/profile/list/', configure.profile_list, name='profile_list', ),
    path('configure/profile/<int:profile_id>/blocked/', configure.profile_change_blocked, name='profile_change_blocked', ),
    path('configure/employer/status_check', configure.employer_status_sync, name='employer_status_check', ),
    path('employer/temp/list/', employer.employer_temp_list, name='employer_temp_list', ),
    path('employer/create/', employer.employer_create, name='employer_create', ),
    path('employer/widget/<int:widget_id>/show/', employer.employer_widget_show, name='employer_widget_show', ),
    path('employer/export/', employer.export_to_spreadsheet, name='employer_export', ),
    path('employer/find/', employer.employer_find, name='employer_find', ),
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
    path('create/<int:temp_employer_id>/', employer.employer_temp_create, name='create', ),
    path('message/list/', message.message_list, name='message_list', ),
    path('message/<int:message_id>/read/', message.message_read, name='message_read', ),
    path('report/list/', report.report_list, name='report_list', ),
    path('report/month/', report.report_month, name='report_month', ),
    path('report/date/', report.report_date, name='report_date', ),
    path('response/list/', response.response_list, name='response_list', ),
    path('response/set/', response.response_set, name='response_set', ),
]

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
