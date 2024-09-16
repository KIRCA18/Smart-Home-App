from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
import string
import random


# Create your models here.
class User(AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    registered_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class House(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}'


class Room(models.Model):
    ROOM_TYPE = [
        ('living_room', 'Living Room'),
        ('kitchen', 'Kitchen'),
        ('bedroom', 'Bedroom'),
        ('bathroom', 'Bathroom'),
        ('toilet', 'Toilet'),
        ('dining_room', 'Dining Room'),
        ('office', 'Office'),
        ('hallway', 'Hallway'),
        ('garage', 'Garage'),
        ('basement', 'Basement'),
        ('attic', 'Attic'),
        ('laundry_room', 'Laundry Room'),
        ('home_theater', 'Home Theater'),
        ('library', 'Library'),
        ('guest_room', 'Guest Room'),
        ('storage_room', 'Storage Room'),
        ('outdoor_patio', 'Outdoor Patio'),
        ('entryway', 'Entryway'),
        ('playroom', 'Playroom'),
        ('workshop', 'Workshop'),
    ]

    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50, choices=ROOM_TYPE)
    house = models.ForeignKey(House, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Device(models.Model):
    DEVICE_TYPES = [
        ('light', 'Light'),  #check
        ('thermostat', 'Thermostat'),  #check
        ('humidity', 'Humidity'),  #check
        ('smart_lock', 'Smart Lock'),
        ('door_sensor', 'Door Sensor'),
        ('motion_sensor', 'Motion Sensor'),
        ('smoke_detector', 'Smoke Detector'),
        ('smart_plug', 'Smart Plug'),  #check
        ('window_sensor', 'Window Sensor'),
    ]

    password = models.CharField(max_length=8, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, choices=DEVICE_TYPES, null=True, blank=True)
    state = models.IntegerField(default=1)
    dashboard = models.BooleanField(default=False)

    @property
    def latest_data(self):
        return self.data.first()

    def __str__(self):
        return f'{self.name} @ {self.room}'


@receiver(post_save, sender=Device)
def generate_device_password(sender, instance, created, **kwargs):
    if created and not instance.password:
        instance.password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        instance.save()


class DeviceData(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='data')
    timestamp = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()  # Stores device-specific data in JSON format

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.device.name} data at {self.timestamp}"
