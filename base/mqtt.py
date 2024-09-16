import paho.mqtt.client as mqtt
from django.conf import settings
from .models import Device, DeviceData
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import json


def on_connect(mqtt_client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
        mqtt_client.subscribe('/devices/data')
    else:
        print('Bad connection. Code:', rc)


def on_message(mqtt_client, userdata, msg):
    alldata = json.loads(msg.payload)
    device = Device.objects.get(id=alldata['id'])
    if device.latest_data is not None:
        DeviceData.objects.all().filter(device=device).exclude(id=device.latest_data.id).delete()
    deviceData = DeviceData.objects.create(device=device, data=alldata['data'])
    # ddq = DeviceData.objects.all().filter(device=device).exclude(id=deviceData.id).delete()
    # latest_two_ids = DeviceData.objects.filter(device=device).order_by('-created_at').values_list('id', flat=True)[:2]
    # DeviceData.objects.filter(device=device).exclude(id__in=latest_two_ids).delete()

    # print(len(DeviceData.objects.all().filter(device=device)))
    # print(deviceData)
    # print(f'id: {alldata["id"]}, all {alldata["data"]}')
    # print(f'Received message on topic: {msg.topic} with payload: {msg.payload}')


@receiver(pre_delete, sender=Device)
def delete_device(sender, instance, **kwargs):
    client.publish(f'/devices/delete/{instance.id}', '')


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set('smarthomeapp', 'a1s2d3')
client.connect(
    host="mqtt-broker",
    port=1883,
    keepalive=60
)
