from django.forms import ModelForm
from .models import User, House, Room, Device
from django.contrib.auth.forms import UserCreationForm


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(MyUserCreationForm, self).__init__(*args, **kwargs)
        # Apply 'form-control' class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class HouseForm(ModelForm):
    class Meta:
        model = House
        fields = ['name', 'address']

    def __init__(self, *args, **kwargs):
        super(HouseForm, self).__init__(*args, **kwargs)
        # Apply 'form-control' class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'type']

    def __init__(self, *args, **kwargs):
        super(RoomForm, self).__init__(*args, **kwargs)
        # Apply 'form-control' class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class DeviceForm(ModelForm):
    class Meta:
        model = Device
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(DeviceForm, self).__init__(*args, **kwargs)
        # Apply 'form-control' class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


