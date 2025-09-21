import json
import time
from datetime import datetime, timedelta
import secrets
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, pre_delete, m2m_changed
from django.dispatch import receiver
import string
import random
import qrcode
import os
from django.conf import settings
from django.utils import timezone
from django.db.models import Max


# Create your models here.
class User(AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    status = models.CharField(
        max_length=10,
        choices=[('online', 'Online'), ('offline', 'Offline')],
        default='offline'
    )
    registered_date = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_avatar_url(self):
        """Return avatar URL or default avatar"""
        if self.avatar:
            return self.avatar.url
        return '/static/img/default_avatar.jpeg'


class House(models.Model):
    COUNTRIES = [
        ("Afghanistan", "Afghanistan"),
        ("Albania", "Albania"),
        ("Algeria", "Algeria"),
        ("Andorra", "Andorra"),
        ("Angola", "Angola"),
        ("Antigua_and_Barbuda", "Antigua and Barbuda"),
        ("Argentina", "Argentina"),
        ("Armenia", "Armenia"),
        ("Australia", "Australia"),
        ("Austria", "Austria"),
        ("Azerbaijan", "Azerbaijan"),
        ("Bahamas", "Bahamas"),
        ("Bahrain", "Bahrain"),
        ("Bangladesh", "Bangladesh"),
        ("Barbados", "Barbados"),
        ("Belarus", "Belarus"),
        ("Belgium", "Belgium"),
        ("Belize", "Belize"),
        ("Benin", "Benin"),
        ("Bhutan", "Bhutan"),
        ("Bolivia", "Bolivia"),
        ("Bosnia_and_Herzegovina", "Bosnia and Herzegovina"),
        ("Botswana", "Botswana"),
        ("Brazil", "Brazil"),
        ("Brunei", "Brunei"),
        ("Bulgaria", "Bulgaria"),
        ("Burkina_Faso", "Burkina Faso"),
        ("Burundi", "Burundi"),
        ("Cabo_Verde", "Cabo Verde"),
        ("Cambodia", "Cambodia"),
        ("Cameroon", "Cameroon"),
        ("Canada", "Canada"),
        ("Central_African_Republic", "Central African Republic"),
        ("Chad", "Chad"),
        ("Chile", "Chile"),
        ("China", "China"),
        ("Colombia", "Colombia"),
        ("Comoros", "Comoros"),
        ("Congo_(Congo-Brazzaville)", "Congo (Congo-Brazzaville)"),
        ("Costa_Rica", "Costa Rica"),
        ("Croatia", "Croatia"),
        ("Cuba", "Cuba"),
        ("Cyprus", "Cyprus"),
        ("Czech_Republic", "Czech Republic"),
        ("Democratic_Republic_of_the_Congo", "Democratic Republic of the Congo"),
        ("Denmark", "Denmark"),
        ("Djibouti", "Djibouti"),
        ("Dominica", "Dominica"),
        ("Dominican_Republic", "Dominican Republic"),
        ("Ecuador", "Ecuador"),
        ("Egypt", "Egypt"),
        ("El_Salvador", "El Salvador"),
        ("Equatorial_Guinea", "Equatorial Guinea"),
        ("Eritrea", "Eritrea"),
        ("Estonia", "Estonia"),
        ("Eswatini", "Eswatini"),
        ("Ethiopia", "Ethiopia"),
        ("Fiji", "Fiji"),
        ("Finland", "Finland"),
        ("France", "France"),
        ("Gabon", "Gabon"),
        ("Gambia", "Gambia"),
        ("Georgia", "Georgia"),
        ("Germany", "Germany"),
        ("Ghana", "Ghana"),
        ("Greece", "Greece"),
        ("Grenada", "Grenada"),
        ("Guatemala", "Guatemala"),
        ("Guinea", "Guinea"),
        ("Guinea-Bissau", "Guinea-Bissau"),
        ("Guyana", "Guyana"),
        ("Haiti", "Haiti"),
        ("Honduras", "Honduras"),
        ("Hungary", "Hungary"),
        ("Iceland", "Iceland"),
        ("India", "India"),
        ("Indonesia", "Indonesia"),
        ("Iran", "Iran"),
        ("Iraq", "Iraq"),
        ("Ireland", "Ireland"),
        ("Israel", "Israel"),
        ("Italy", "Italy"),
        ("Jamaica", "Jamaica"),
        ("Japan", "Japan"),
        ("Jordan", "Jordan"),
        ("Kazakhstan", "Kazakhstan"),
        ("Kenya", "Kenya"),
        ("Kiribati", "Kiribati"),
        ("Kuwait", "Kuwait"),
        ("Kyrgyzstan", "Kyrgyzstan"),
        ("Laos", "Laos"),
        ("Latvia", "Latvia"),
        ("Lebanon", "Lebanon"),
        ("Lesotho", "Lesotho"),
        ("Liberia", "Liberia"),
        ("Libya", "Libya"),
        ("Liechtenstein", "Liechtenstein"),
        ("Lithuania", "Lithuania"),
        ("Luxembourg", "Luxembourg"),
        ("Madagascar", "Madagascar"),
        ("Malawi", "Malawi"),
        ("Malaysia", "Malaysia"),
        ("Maldives", "Maldives"),
        ("Mali", "Mali"),
        ("Malta", "Malta"),
        ("Marshall_Islands", "Marshall Islands"),
        ("Mauritania", "Mauritania"),
        ("Mauritius", "Mauritius"),
        ("Mexico", "Mexico"),
        ("Micronesia", "Micronesia"),
        ("Moldova", "Moldova"),
        ("Monaco", "Monaco"),
        ("Mongolia", "Mongolia"),
        ("Montenegro", "Montenegro"),
        ("Morocco", "Morocco"),
        ("Mozambique", "Mozambique"),
        ("Myanmar", "Myanmar"),
        ("Namibia", "Namibia"),
        ("Nauru", "Nauru"),
        ("Nepal", "Nepal"),
        ("Netherlands", "Netherlands"),
        ("New_Zealand", "New Zealand"),
        ("Nicaragua", "Nicaragua"),
        ("Niger", "Niger"),
        ("Nigeria", "Nigeria"),
        ("North_Korea", "North Korea"),
        ("North_Macedonia", "North Macedonia"),
        ("Norway", "Norway"),
        ("Oman", "Oman"),
        ("Pakistan", "Pakistan"),
        ("Palau", "Palau"),
        ("Palestine_State", "Palestine State"),
        ("Panama", "Panama"),
        ("Papua_New_Guinea", "Papua New Guinea"),
        ("Paraguay", "Paraguay"),
        ("Peru", "Peru"),
        ("Philippines", "Philippines"),
        ("Poland", "Poland"),
        ("Portugal", "Portugal"),
        ("Qatar", "Qatar"),
        ("Romania", "Romania"),
        ("Russia", "Russia"),
        ("Rwanda", "Rwanda"),
        ("Saint_Kitts_and_Nevis", "Saint Kitts and Nevis"),
        ("Saint_Lucia", "Saint Lucia"),
        ("Saint_Vincent_and_the_Grenadines", "Saint Vincent and the Grenadines"),
        ("Samoa", "Samoa"),
        ("San_Marino", "San Marino"),
        ("Sao_Tome_and_Principe", "Sao Tome and Principe"),
        ("Saudi_Arabia", "Saudi Arabia"),
        ("Senegal", "Senegal"),
        ("Serbia", "Serbia"),
        ("Seychelles", "Seychelles"),
        ("Sierra_Leone", "Sierra Leone"),
        ("Singapore", "Singapore"),
        ("Slovakia", "Slovakia"),
        ("Slovenia", "Slovenia"),
        ("Solomon_Islands", "Solomon Islands"),
        ("Somalia", "Somalia"),
        ("South_Africa", "South Africa"),
        ("South_Korea", "South Korea"),
        ("South_Sudan", "South Sudan"),
        ("Spain", "Spain"),
        ("Sri_Lanka", "Sri Lanka"),
        ("Sudan", "Sudan"),
        ("Suriname", "Suriname"),
        ("Sweden", "Sweden"),
        ("Switzerland", "Switzerland"),
        ("Syria", "Syria"),
        ("Tajikistan", "Tajikistan"),
        ("Tanzania", "Tanzania"),
        ("Thailand", "Thailand"),
        ("Timor-Leste", "Timor-Leste"),
        ("Togo", "Togo"),
        ("Tonga", "Tonga"),
        ("Trinidad_and_Tobago", "Trinidad and Tobago"),
        ("Tunisia", "Tunisia"),
        ("Turkey", "Turkey"),
        ("Turkmenistan", "Turkmenistan"),
        ("Tuvalu", "Tuvalu"),
        ("Uganda", "Uganda"),
        ("Ukraine", "Ukraine"),
        ("United_Arab_Emirates", "United Arab Emirates"),
        ("United_Kingdom", "United Kingdom"),
        ("United_States", "United States"),
        ("Uruguay", "Uruguay"),
        ("Uzbekistan", "Uzbekistan"),
        ("Vanuatu", "Vanuatu"),
        ("Vatican_City", "Vatican City"),
        ("Venezuela", "Venezuela"),
        ("Vietnam", "Vietnam"),
        ("Yemen", "Yemen"),
        ("Zambia", "Zambia"),
        ("Zimbabwe", "Zimbabwe")
    ]

    name = models.CharField(max_length=50)
    country = models.CharField(max_length=500, choices=COUNTRIES)
    city = models.CharField(max_length=500)
    street = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='houses')
    created_at = models.DateTimeField(auto_now_add=True)

    # timezone = models.CharField(max_length=50, default='UTC')

    def __str__(self):
        return f'{self.name}'


@receiver(post_save, sender=House)
def create_owner_dashboard(sender, instance, created, **kwargs):
    if created:
        Dashboard.objects.get_or_create(
            house=instance,
            user=instance.owner
        )


@receiver(m2m_changed, sender=House.members.through)
def create_member_dashboard(sender, instance, action, pk_set, **kwargs):
    # instance = House
    if action == "post_add":
        for user_id in pk_set:
            user = User.objects.get(pk=user_id)
            Dashboard.objects.get_or_create(
                house=instance,
                user=user
            )


@receiver(m2m_changed, sender=House.members.through)
def handle_member_removed(sender, instance, action, pk_set, **kwargs):
    if action == "post_remove":
        for user_id in pk_set:
            Dashboard.objects.filter(house=instance, user_id=user_id).delete()


class HouseInvitation(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    invited_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invitations')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = datetime.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invite to {self.house.name} for {self.invited_user.username}"


class Room(models.Model):
    ROOM_TYPE = [
        ('living_room', 'Living Room'),
        ('kitchen', 'Kitchen'),
        ('bedroom', 'Bedroom'),
        ('bathroom', 'Bathroom'),
        ('dining_room', 'Dining Room'),
        ('hallway', 'Hallway'),
        ('garage', 'Garage'),
        ('basement', 'Basement'),
        ('attic', 'Attic'),
        ('laundry_room', 'Laundry Room'),
        ('entryway', 'Entryway'),
        ('garden', 'Garden'),
        ('other', 'Other')
    ]

    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50, choices=ROOM_TYPE)
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='rooms')

    class Meta:
        unique_together = ['name', 'house']

    @property
    def last_activity(self):
        return DeviceData.objects.filter(device__room=self).aggregate(
            latest=Max("timestamp")  # replace with your datetime field name
        )["latest"]

    def __str__(self):
        return f"{self.name} ({self.house.name})"


# DEVICE_TYPES = [
#     ('light', 'Light'),  # check
#     ('thermostat', 'Thermostat'),  # check
#     ('humidity', 'Humidity'),  # check
#     ('smart_lock', 'Smart Lock'),
#     ('door_sensor', 'Door Sensor'),
#     ('motion_sensor', 'Motion Sensor'),
#     ('smoke_detector', 'Smoke Detector'),
#     ('smart_plug', 'Smart Plug'),  # check
#     ('window_sensor', 'Window Sensor'),
# ]


class Action(models.Model):
    """
    Represents a control command that can be sent to a device.
    Example: turn_on, turn_off, set_brightness, set_temperature, etc.
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    command = models.CharField(max_length=100, null=False, unique=True, blank=False)
    parameters_schema = models.JSONField(default=dict, blank=True)  # JSON schema for parameters

    def __str__(self):
        return self.name

    def handleGroupAction(self, groupID, values):
        group = Group.objects.get(id=groupID)
        valuesNeeded = self.parameters_schema
        for key in valuesNeeded.keys():
            if not values[key]:
                return
        for device in group.devices.all():
            if self in device.device.type.actions.all():
                self.handleDeviceAction(device, values, valuesChecked=True)

    def handleDeviceAction(self, device, values, valuesChecked=False):
        print(device)
        if not valuesChecked:
            print(valuesChecked)
            valuesNeeded = self.parameters_schema
            print(valuesNeeded)
            for key in valuesNeeded.keys():
                if not values[key]:
                    return
        message = {'command': self.command, 'values': {}}
        for key in values.keys():
            message['values'][key] = values[key]
        from .mqtt import client as mqtt_client
        print('controlling device')
        print(device.device.mac_address)
        print(json.dumps(message))
        mqtt_client.publish(f'/devices/control/{device.device.mac_address}', json.dumps(message))


class Signal(models.Model):
    """
    Represents a type of signal or data a device can send.
    Example: temperature_reading, power_usage, motion_detected, etc.
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    data_type = models.CharField(
        max_length=20,
        choices=[
            ('number', 'Number'),
            ('boolean', 'Boolean'),
            ('string', 'String'),
            ('json', 'JSON Object')
        ],
        default='number'
    )
    unit = models.CharField(max_length=20, blank=True)  # e.g., °C, %, W, etc.

    def __str__(self):
        return self.name


class DeviceType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    actions = models.ManyToManyField(Action, blank=True)
    signals = models.ManyToManyField(Signal, blank=True)

    def __str__(self):
        return self.name


class State(models.Model):
    field = models.CharField(max_length=50)
    data_type = models.CharField(max_length=20, choices=[
        ('number', 'Number'),
        ('boolean', 'Boolean'),
        ('string', 'String')
    ])

    def __str__(self):
        return self.field


class Device(models.Model):
    """
    Physical device with its unique identifier
    """
    mac_address = models.CharField(max_length=50, unique=True)
    type = models.ForeignKey(DeviceType, on_delete=models.CASCADE)
    manufacturer = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    firmware_version = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    state_schema = models.ManyToManyField(State, blank=True)
    token = models.CharField(max_length=10, unique=True, blank=True)
    view = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.type.name} ({self.mac_address})"

    def generate_token(self, length: int = 6) -> str:
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def generate_qr_code(self):
        qr_content = f"mac={self.mac_address}&token={self.token}"

        # Ensure folder exists
        qr_folder = os.path.join(settings.MEDIA_ROOT, "qrcodes")
        os.makedirs(qr_folder, exist_ok=True)

        # Filename: device_<mac>.png
        filename = f"device_{self.mac_address.replace(':', '-')}.png"
        filepath = os.path.join(qr_folder, filename)

        # Generate and save QR
        img = qrcode.make(qr_content)
        img.save(filepath)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        super().save(*args, **kwargs)
        self.generate_qr_code()


class RoomDevice(models.Model):
    """
    Device instance installed in a specific room
    """
    name = models.CharField(max_length=50)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='devices')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='installations')
    status = models.CharField(
        max_length=10,
        choices=[('online', 'Online'), ('offline', 'Offline')],
        default='offline'
    )
    installed_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    settings = models.JSONField(default=dict, blank=True)  # Device-specific settings

    @property
    def latest_data(self):
        return self.data

    @property
    def type(self):
        return self.device.type

    def get_latest_signal_value(self, signal_name):
        """Get the latest value for a specific signal"""
        latest_data = self.latest_data
        if latest_data and latest_data.data:
            return latest_data.data.get(signal_name)
        return None

    class Meta:
        unique_together = ['name', 'room']

    def __str__(self):
        return f'{self.name} @ {self.room}'

    def get_state_value(self, field):
        return self.data.data.get(field)


#
# @receiver(post_save, sender=Device)
# def generate_device_password(sender, instance, created, **kwargs):
#     if created and not instance.password:
#         instance.password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
#         instance.save()

class Widget(models.Model):
    name = models.CharField(max_length=50)
    html = models.TextField()

    def __str__(self):
        return self.name


class Dashboard(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='dashboards')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboards')
    widgets = models.ManyToManyField(Widget, blank=True)
    devices = models.ManyToManyField(RoomDevice, blank=True)

    class Meta:
        unique_together = ['user', 'house']

    def __str__(self):
        return f'{self.user.id} {self.user} @ {self.house}'


class DeviceData(models.Model):
    device = models.OneToOneField(RoomDevice, on_delete=models.CASCADE, related_name='data')
    timestamp = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()  # Stores device-specific data in JSON format

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.device.name} data at {self.timestamp}"


class SignalData(models.Model):
    device = models.ForeignKey(RoomDevice, on_delete=models.CASCADE, related_name="signals")
    signal_type = models.CharField(max_length=50)  # e.g. "turn_on", "temperature_change"
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=["device", "signal_type", "-timestamp"]),
        ]


class Group(models.Model):
    """
    Group of RoomDevices. Useful to apply actions or automation rules on multiple devices together.
    """
    name = models.CharField(max_length=50)
    devices = models.ManyToManyField(RoomDevice, related_name='groups')
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='groups')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def actions(self) -> []:
        return (
            Action.objects
            .filter(devicetype__device__installations__groups=self)
            .distinct()
            .order_by("id")
        )

    class Meta:
        unique_together = ['name', 'house']

    def __str__(self):
        return f"{self.name} ({self.house.name})"


class AutomationRule(models.Model):
    """
    Automation rule that uses expression-based condition logic
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='automation_rules')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    trigger_count = models.IntegerField(default=0)

    # Expression-based condition logic
    condition_expression = models.TextField(
        blank=True,
        default="",
        help_text="Logical expression using condition positions, e.g., '(1 && 2) || (3 && 4)'"
    )

    class Meta:
        ordering = ['id']
        unique_together = ['name', 'house']

    def get_condition_str(self):
        conditions = self.conditions.all().order_by('position')
        expression = self.condition_expression
        expression = expression.replace('&&', ' AND ')
        expression = expression.replace('||', ' OR ')
        print(conditions)
        for index in range(len(conditions)):
            expression = expression.replace(f'{index + 1}', '{}')
        return expression.format(*conditions)

    def evaluate_conditions(self):
        """Evaluate conditions using the expression"""
        print("evaluate conditions")
        conditions = list(self.conditions.all().order_by('position'))

        if not conditions:
            print("no conditions")
            return True, []

        # If no expression is set, default to AND all conditions
        print(f'condition_expression: {self.condition_expression.strip()}')
        print(not self.condition_expression.strip())
        if not self.condition_expression.strip():
            conditions_met = []
            result = True
            for condition in conditions:
                condition_result = condition.evaluate()
                if condition_result:
                    conditions_met.append(condition.id)
                result = result and condition_result
            print(conditions_met)
            return result, conditions_met

        # Evaluate using the expression
        return self._evaluate_expression(conditions)

    def _evaluate_expression(self, conditions):
        """Evaluate the condition expression"""
        import re

        conditions_met = []
        condition_results = {}

        # First, evaluate each condition and store results
        for condition in conditions:
            print(f'evaluate condition {condition}')
            result = condition.evaluate()
            print(f'condition result: {result}')
            condition_results[condition.position] = result
            if result:
                conditions_met.append(condition.id)

        # Replace condition positions with their boolean results
        expression = self.condition_expression

        # Find all numbers in the expression (condition positions)
        positions = re.findall(r'\b\d+\b', expression)
        print(f'positions: {positions}')
        for pos in set(positions):
            pos_int = int(pos)
            # Replace the position with the actual boolean result
            result_str = 'True' if condition_results.get(pos_int, False) else 'False'
            expression = re.sub(rf'\b{pos}\b', result_str, expression)

        # Convert && to 'and' and || to 'or' for Python evaluation
        expression = expression.replace('&&', ' and ').replace('||', ' or ')
        print(f'expression: {expression}')
        try:
            # Safely evaluate the expression
            result = eval(expression)
            return result, conditions_met
        except Exception as e:
            print(f"Error evaluating expression '{self.condition_expression}': {e}")
            return False, []

    def validate_expression(self):
        """Validate that the expression uses valid condition positions"""
        if not self.condition_expression.strip():
            return True, "No expression set - will use AND logic"

        import re

        # Get all condition positions
        condition_positions = set(self.conditions.values_list('position', flat=True))

        # Find all numbers referenced in the expression
        referenced_positions = set(int(pos) for pos in re.findall(r'\b\d+\b', self.condition_expression))

        # Check for missing conditions
        missing = referenced_positions - condition_positions
        if missing:
            return False, f"Expression references non-existent conditions: {sorted(missing)}"

        # Check for unused conditions
        unused = condition_positions - referenced_positions
        if unused:
            return False, f"Conditions not used in expression: {sorted(unused)}"

        return True, "Expression is valid"

    def __str__(self):
        return f"{self.name} ({self.house.name})"


class AutomationCondition(models.Model):
    """
    Conditions that must be met for an automation rule to trigger
    """
    CONDITION_TYPES = [
        ('state_value', 'Device State Value'),
        ('schedule', 'Schedule/Time'),
        ('action_trigger', 'Action Trigger'),
        ('weather', 'Weather Condition'),
    ]

    OPERATORS = [
        ('eq', 'Equals'),
        ('ne', 'Not Equals'),
        ('gt', 'Greater Than'),
        ('gte', 'Greater Than or Equal'),
        ('lt', 'Less Than'),
        ('lte', 'Less Than or Equal'),
        ('in_range', 'In Range'),
        ('not_in_range', 'Not In Range'),
        ('contains', 'Contains'),
        ('not_contains', 'Does Not Contain'),
        ('changed_to', 'Changed To'),
        ('changed_from', 'Changed From'),
    ]

    WEATHER_CONDITIONS = [
        ('sunny', 'Sunny'),
        ('cloudy', 'Cloudy'),
        ('rainy', 'Rainy'),
        ('snowy', 'Snowy'),
        ('stormy', 'Stormy'),
        ('foggy', 'Foggy'),
    ]

    rule = models.ForeignKey(AutomationRule, on_delete=models.CASCADE, related_name='conditions')

    # Position in the rule (used in the expression)
    position = models.PositiveIntegerField()

    condition_type = models.CharField(max_length=20, choices=CONDITION_TYPES)

    # State value condition fields
    device = models.ForeignKey(RoomDevice, on_delete=models.CASCADE, null=True, blank=True)
    state_field = models.ForeignKey(State, on_delete=models.CASCADE, null=True, blank=True)
    operator = models.CharField(max_length=20, choices=OPERATORS, default='eq')
    target_value = models.TextField(null=True, blank=True)

    # Schedule condition fields
    time = models.TimeField(null=True, blank=True)
    days_of_week = models.JSONField(default=list, blank=True)
    specific_date = models.DateField(null=True, blank=True)

    # Action trigger condition fields
    trigger_action = models.ForeignKey(Signal, on_delete=models.CASCADE, null=True, blank=True)

    # Weather condition fields
    weather_condition = models.CharField(max_length=20, choices=WEATHER_CONDITIONS, blank=True)
    temperature_min = models.FloatField(null=True, blank=True)
    temperature_max = models.FloatField(null=True, blank=True)
    humidity_min = models.FloatField(null=True, blank=True)
    humidity_max = models.FloatField(null=True, blank=True)
    check_forecast_hours = models.IntegerField(default=0)

    class Meta:
        ordering = ['position']
        unique_together = ['rule', 'position']

    def save(self, *args, **kwargs):
        # Auto-assign position if not set
        if not self.position:
            max_pos = self.rule.conditions.aggregate(
                models.Max('position')
            )['position__max'] or 0
            self.position = max_pos + 1
        super().save(*args, **kwargs)

    def evaluate(self):
        """Evaluate this condition and return True/False"""
        try:
            if self.condition_type == 'state_value':
                return self._evaluate_state_value()
            elif self.condition_type == 'schedule':
                return self._evaluate_schedule()
            elif self.condition_type == 'action_trigger':
                return self._evaluate_action_trigger()
            elif self.condition_type == 'weather':
                return self._evaluate_weather()
        except Exception as e:
            print(f"Error evaluating condition {self.id}: {e}")
            return False
        return False

    def _evaluate_state_value(self):
        """Evaluate device state value condition"""
        if not self.device or not self.state_field:
            return False

        current_value = self.device.get_state_value(self.state_field.field)
        if current_value is None:
            return False
        print(f'current_value: {current_value}')
        target_value = self.target_value if self.state_field.data_type == 'string' else int(
            self.target_value) if self.state_field.data_type == 'number' else bool(self.target_value)
        print(f'target_value: {target_value}')
        print(f'operator: {self.operator}')
        try:
            type
            if self.operator == 'eq':
                print('operator equals')
                print(f'current_value == target_value: {current_value == target_value}')
                print(f'type current_value: {type(current_value)}')
                print(f'type target_value: {type(target_value)}')
                return current_value == target_value
            elif self.operator == 'ne':
                return current_value != target_value
            elif self.operator == 'gt' and self.state_field.data_type == 'number':
                return float(current_value) > float(target_value)
            elif self.operator == 'gte' and self.state_field.data_type == 'number':
                return float(current_value) >= float(target_value)
            elif self.operator == 'lt' and self.state_field.data_type == 'number':
                return float(current_value) < float(target_value)
            elif self.operator == 'lte' and self.state_field.data_type == 'number':
                return float(current_value) <= float(target_value)
            # elif self.operator == 'in_range' and self.state_field.data_type == 'number':
            #     if isinstance(target_value, list) and len(target_value) == 2:
            #         return float(target_value[0]) <= float(current_value) <= float(target_value[1])
            # elif self.operator == 'not_in_range' and self.state_field.data_type == 'number':
            #     if isinstance(target_value, list) and len(target_value) == 2:
            #         return not (float(target_value[0]) <= float(current_value) <= float(target_value[1]))
            # elif self.operator == 'contains' and self.state_field.data_type == 'string':
            #     return str(target_value) in str(current_value)
            # elif self.operator == 'not_contains' and self.state_field.data_type == 'string':
            #     return str(target_value) not in str(current_value)
        except (ValueError, TypeError):
            return False

        return False

    def _evaluate_schedule(self):
        """Evaluate schedule/time condition (hours and minutes only)"""
        from datetime import datetime

        now = datetime.now()
        current_time = now.time()
        current_date = now.date()
        current_weekday = now.weekday()
        print(current_time)
        print(self.time)
        # Check specific date if set
        if self.specific_date and self.specific_date != current_date:
            return False

        # Check day of week if specified
        if self.days_of_week and not self.days_of_week[current_weekday]:
            return False

        # Compare only hours and minutes
        if self.time:
            return self.time.hour == current_time.hour and self.time.minute == current_time.minute

        return False

    def _evaluate_action_trigger(self):
        """Evaluate action trigger condition"""
        latest_signal = self.device.signals.first()
        if not latest_signal:
            return False  # no signals exist

        one_minute_ago = timezone.now() - timedelta(minutes=1)
        if latest_signal.timestamp >= one_minute_ago:
            return True

        return False

    def _evaluate_weather(self):
        """Evaluate weather condition"""
        try:
            from .utils import get_weather_condition

            weather_condition = get_weather_condition(
                house=self.rule.house,
                forecast_hours=self.check_forecast_hours
            )

            print(f'weather condition: {weather_condition}')
            print(f'self.weather_condition: {self.weather_condition}')
            if not weather_condition:
                return False

            # Check weather condition
            if self.weather_condition:
                if weather_condition.lower() != self.weather_condition:
                    return False

            return True

        except ImportError:
            print("Weather utility not implemented")
            return False
        except Exception as e:
            print(f"Weather condition evaluation error: {e}")
            return False

    def __str__(self):
        if self.condition_type == 'state_value':
            return f'{self.device} {self.state_field} {self.get_operator_display()} {self.target_value}'
        elif self.condition_type == 'schedule':
            if self.specific_date is not None:
                return f'When at {self.time} on {self.specific_date}'
            else:
                dayArr = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                return f'When at {self.time} on ({",".join([dayArr[index] for index in range(len(dayArr)) if self.days_of_week[index] == True])})'
        elif self.condition_type == 'action_trigger':
            return f'{self.device} on {self.trigger_action}'
        elif self.condition_type == 'weather':
            return f'When {"yesterdays" if self.check_forecast_hours == -24 else "tomorrows" if self.check_forecast_hours == 24 else "todays"} weather is {self.get_weather_condition_display()}'
        return f"Condition {self.position} for {self.rule.name}: {self.get_condition_type_display()}"


class AutomationAction(models.Model):
    """
    Actions to be executed when automation conditions are met
    """
    ACTION_TYPES = [
        ('device_action', 'Device Action'),
        ('group_action', 'Group Action'),
        ('notification', 'Send Notification'),
        ('custom', 'Custom Action'),
    ]

    rule = models.ForeignKey(AutomationRule, on_delete=models.CASCADE, related_name='actions')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    execution_order = models.IntegerField(default=0)  # Order of execution

    # Device action fields
    device = models.ForeignKey(RoomDevice, on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    action = models.ForeignKey(Action, on_delete=models.CASCADE, null=True, blank=True)
    parameters = models.JSONField(default=dict, blank=True)  # Action parameters

    # Notification fields
    notification_title = models.CharField(max_length=100, blank=True)
    notification_message = models.TextField(blank=True)
    notification_users = models.ManyToManyField(User, blank=True)

    # Custom action fields
    custom_function = models.CharField(max_length=100, blank=True)
    custom_parameters = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['execution_order']

    def execute(self):
        """Execute this action"""
        if self.action_type == 'device_action':
            return self._execute_device_action()
        elif self.action_type == 'group_action':
            return self._execute_group_action()
        elif self.action_type == 'notification':
            return self._execute_notification()
        # Add more action types as needed
        return False

    def _execute_device_action(self):
        """Execute action on a device"""
        if not self.device or not self.action:
            return False

        self.action.handleDeviceAction(self.device, self.parameters, True)
        print(f"Executing {self.action.name} on {self.device.name} with params: {self.parameters}")
        return True

    def _execute_group_action(self):
        """Execute action on all devices in a group"""
        if not self.group or not self.action:
            return False

        self.action.handleGroupAction(self.group.id, self.parameters)
        return True

    def _execute_single_device_action(self, device):
        """Helper method to execute action on a single device"""
        # Implement your device control logic here
        print(f"Executing {self.action.name} on {device.name} with params: {self.parameters}")
        return True

    def _execute_notification(self):
        """Send notification to users"""
        # Implement your notification logic here
        print(f"Sending notification: {self.notification_title} - {self.notification_message}")
        return True

    def __str__(self):
        if self.action_type == 'device_action':
            return f'{self.action.name} {self.device}'
        elif self.action_type == 'group_action':
            return f'{self.action.name} {self.group}'
        return f"Action for {self.rule.name}: {self.action_type}"
