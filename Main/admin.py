from django.contrib import admin
from Main.models import UserProfile, TempEmployer, Employer, Event, Info, Notify, Message, ConfigWatch

admin.site.register(Employer)
admin.site.register(UserProfile)
admin.site.register(TempEmployer)
admin.site.register(Event)
admin.site.register(Info)
admin.site.register(Notify)
admin.site.register(Message)
admin.site.register(ConfigWatch)
