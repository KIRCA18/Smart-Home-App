from django.contrib import admin

# Register your models here.

from .models import User, House, HouseInvitation, Action, Signal, DeviceType, State, RoomDevice, Room, Device, \
    DeviceData, Group, AutomationRule, AutomationCondition, AutomationAction, Dashboard, Widget, SignalData

admin.site.register(User)
admin.site.register(House)
admin.site.register(HouseInvitation)
admin.site.register(Action)
admin.site.register(Signal)
admin.site.register(DeviceType)
admin.site.register(State)
admin.site.register(RoomDevice)
admin.site.register(Group)
admin.site.register(AutomationRule)
admin.site.register(AutomationCondition)
admin.site.register(AutomationAction)
admin.site.register(Room)
admin.site.register(Device)
admin.site.register(DeviceData)
admin.site.register(Dashboard)
admin.site.register(Widget)
admin.site.register(SignalData)
