from django.contrib import admin
from Main.models import Status, UserProfile, TempEmployer, Employer, StatusEmployer, Event, Info, Notify, \
    Message, UpdateEmployer, StatusRoute, Config

admin.site.register(Status)
admin.site.register(Employer)
admin.site.register(StatusEmployer)
admin.site.register(UserProfile)
admin.site.register(TempEmployer)
admin.site.register(Event)
admin.site.register(Info)
admin.site.register(Notify)
admin.site.register(Message)
admin.site.register(UpdateEmployer)
admin.site.register(StatusRoute)
admin.site.register(Config)
