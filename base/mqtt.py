import paho.mqtt.client as mqtt
from django.conf import settings
from .models import RoomDevice, Device, DeviceData, SignalData, AutomationCondition, Signal, AutomationRule
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import json
from django.utils import timezone


def on_connect(mqtt_client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
        mqtt_client.subscribe('/devices/data')
        mqtt_client.subscribe('/devices/exist')
    else:
        print('Bad connection. Code:', rc)


def on_message(mqtt_client, userdata, msg):
    # print(msg)
    if msg.topic == '/devices/data':
        data_message(mqtt_client, userdata, msg)
    elif msg.topic == '/devices/exist':
        exist_message(mqtt_client, userdata, msg)
    else:
        print(f"Unknown topic: {msg.topic} \n Message: {msg.payload}")


def exist_message(mqtt_client, userdata, msg):
    mac_address = msg.payload.decode('utf-8')
    print(mac_address)
    device = Device.objects.get(mac_address=mac_address)
    if device.installations:
        client.publish(f'/devices/exist/{mac_address}', "true")
    else:
        client.publish(f'/devices/exist/{mac_address}', "false")


def data_message(mqtt_client, userdata, msg):
    alldata = json.loads(msg.payload)
    print(alldata)
    device = Device.objects.get(mac_address=alldata['id'])
    roomDevice = device.installations.first()
    # print(roomDevice)
    if roomDevice is None:
        print("Device not added to room (not installed)")
        return
    if roomDevice.status == "offline":
        roomDevice.status = "online"
    roomDevice.last_seen = timezone.now()
    roomDevice.save()
    if alldata['type'] == 'action':
        print('alldata', alldata)
        latestSignal = SignalData.objects.create(device=roomDevice, signal_type=alldata['action'])
        signal = Signal.objects.get(name=alldata['action'])
        print('signal:', signal)
        conditions = AutomationCondition.objects.filter(device=roomDevice, condition_type='action_trigger',
                                                        trigger_action=signal)
        print('conditions:', conditions)
        rules = AutomationRule.objects.filter(conditions__in=conditions, is_active=True).distinct()
        print('rules:', rules)
        print('action')
        for rule in rules:
            if rule.evaluate_conditions()[0]:
                for action in rule.actions.all():
                    action.execute()
    elif alldata['type'] == 'state':
        lastData = None
        if hasattr(roomDevice, "data"):
            lastData = roomDevice.data.data
            deviceData = roomDevice.data
            deviceData.data = alldata['data']
            deviceData.timestamp = timezone.now()
            deviceData.save()
        else:
            deviceData = DeviceData.objects.create(device=roomDevice, data=alldata['data'])
        # deviceData = DeviceData.objects.create(device=roomDevice, data=alldata['data'])
        # print(lastData)
        if not lastData or lastData != deviceData.data:
            conditions = AutomationCondition.objects.filter(device=roomDevice, condition_type='state_value')
            rules = AutomationRule.objects.filter(conditions__in=conditions, is_active=True).distinct()
            for rule in rules:
                if rule.evaluate_conditions()[0]:
                    for action in rule.actions.all():
                        action.execute()
    # TODO: Test the upper code
    #####################################
    # alldata = json.loads(msg.payload)
    # device = Device.objects.get(id=alldata['id'])
    # if device.latest_data is not None:
    #     DeviceData.objects.all().filter(device=device).exclude(id=device.latest_data.id).delete()
    # deviceData = DeviceData.objects.create(device=device, data=alldata['data'])
    ###########################################

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
    host="192.168.66.105",
    port=1883,
    keepalive=60
)
