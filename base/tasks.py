from celery import shared_task
from django.utils import timezone
from .models import AutomationRule, AutomationCondition, RoomDevice
from datetime import timedelta
from .mqtt import client as mqtt_client

@shared_task
def evaluate_scheduled_rules():
    now = timezone.localtime().time()
    print(f"Checking rules at {now}")

    rules = AutomationRule.objects.filter(
        conditions__condition_type='schedule',
        is_active=True,
    ).distinct()

    for rule in rules:
        print(f"Evaluating rule {rule}")
        if rule.evaluate_conditions()[0]:
            actions = rule.actions.all().order_by('execution_order')
            for action in actions:
                action.execute()


@shared_task
def find_offline_devices():
    now = timezone.localtime().time()
    print(f"Checking offline at {now}")
    cutoff = timezone.now() - timedelta(minutes=2)
    devices = RoomDevice.objects.filter(data__timestamp__lt=cutoff)

    for device in devices:
        device.status = 'offline'
        device.save()


@shared_task
def heart_beat():
    now = timezone.localtime().time()
    print(f"Sending heartbeat at {now}")
    devices = RoomDevice.objects.filter()

    for device in devices:
        mqtt_client.publish(f'/devices/heartbeat/{device.device.mac_address}', '')

