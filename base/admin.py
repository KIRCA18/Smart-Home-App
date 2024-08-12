from django.contrib import admin

# Register your models here.

from .models import User, House, Room, Device, DeviceData

admin.site.register(User)
admin.site.register(House)
admin.site.register(Room)
admin.site.register(Device)
admin.site.register(DeviceData)
