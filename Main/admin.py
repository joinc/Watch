from django.contrib import admin
from Main.models import TypeStatus, UserProfile, TypeViolations, TypeNotify, TempEmployer, Employer, StatusEmployer, \
    Event, Info, Notify, Message, UpdateEmployer, Configure, Widget, WidgetStatus, Department, TypeResult, TypeProtocol

admin.site.register(TypeStatus)
admin.site.register(Department)
admin.site.register(TypeViolations)
admin.site.register(TypeNotify)
admin.site.register(Employer)
admin.site.register(StatusEmployer)
admin.site.register(UserProfile)
admin.site.register(TempEmployer)
admin.site.register(Event)
admin.site.register(Info)
admin.site.register(Notify)
admin.site.register(Message)
admin.site.register(UpdateEmployer)
admin.site.register(Configure)
admin.site.register(Widget)
admin.site.register(WidgetStatus)
admin.site.register(TypeResult)
admin.site.register(TypeProtocol)
