import json
import re

from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.forms import UserCreationForm
from .forms import HouseForm, MyUserCreationForm, RoomForm, RoomDeviceForm
# from .forms import DeviceForm
from .models import House, User, Room, Device, DeviceData, RoomDevice, HouseInvitation, Action, AutomationCondition, \
    State, Signal, Group, Dashboard, Widget, AutomationRule, AutomationAction
from .mqtt import client as mqtt_client
import time
import requests
from django.conf import settings as django_settings
from rapidfuzz import fuzz, process


# Create your views here.

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist!')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid password!')

    context = {'page': page}
    return render(request, 'login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            error_message = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_message.append(error)
            for message in error_message:
                messages.error(request, message)

    return render(request, 'login_register.html', {'form': form})


@login_required(login_url='login')
def home(request):
    # print(request.user)
    houses = House.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct()
    if len(houses) == 0:
        return redirect('create-house')
    return redirect('house', pk=houses.first().id)


@login_required(login_url='login')
def settings(request):
    if request.method == 'POST':
        if request.GET.get('name') == 'true':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            user = User.objects.get(username=request.user.username)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            print('change name')
            return redirect('settings')
        elif request.GET.get('password') == 'true':
            form = PasswordChangeForm(user=request.user, data=request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                print('change password')
                return redirect('settings')
            else:
                messages.error(request, 'Invalid Password!')
        elif request.GET.get('username') == 'true':
            newusername = request.POST.get('username')
            if User.objects.filter(username=newusername).exists():
                messages.error(request, 'Username already taken!')
            else:
                user = User.objects.get(username=request.user.username)
                user.username = newusername
                user.save()
                print('change username')
                return redirect('settings')

    passwordForm = PasswordChangeForm(request.user)
    houses = House.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct()
    context = {'houses': houses, 'devices': devices, 'password_form': passwordForm, 'location': 'Settings'}
    return render(request, 'settings.html', context)


@login_required(login_url='login')
def devices(request):
    room = request.GET.get('room', None)
    if room is not None:
        alldevices = Device.objects.all().filter(room_id=room)
        roomInstance = Room.objects.get(id=room)
        context = {'room': roomInstance, 'devices': alldevices}
    else:
        alldevices = Device.objects.all().filter(dashboard=True, room__house__owner=request.user.id)
        context = {'devices': alldevices}
    return render(request, 'devices.html', context)


@login_required(login_url='login')
def house(request, pk):
    selected_house = get_object_or_404(House, id=pk)
    dashboard, created = Dashboard.objects.get_or_create(user=request.user, house=selected_house)
    print(dashboard.widgets.all())
    devices = RoomDevice.objects.all().filter(room__house=selected_house)
    widgets = Widget.objects.all()
    # context = {'houses': houses, 'devices': devices, 'location': 'Dashboard', 'selected_house': selected_house,
    #            'role': 'owner' if selected_house.owner == request.user else 'member'}
    context = {'location': 'Dashboard', 'selected_house': selected_house,
               'role': 'owner' if selected_house.owner == request.user else 'member', 'dashboard': dashboard,
               'devices': devices, 'widgets': widgets}

    address = f'{selected_house.city}, {selected_house.country}'
    weather_response = requests.get(
        "https://api.weatherapi.com/v1/current.json",
        params={"key": django_settings.WEATHER_API_KEY, "q": address}
    )
    weather_data = weather_response.json()
    context['condition'] = weather_data['current']['condition']['text']
    context['icon'] = weather_data['current']['condition']['icon']
    context['temp_c'] = weather_data['current']['temp_c']
    context['temp_f'] = weather_data['current']['temp_f']
    return render(request, 'home.html', context)
    # houses = House.objects.all().filter(owner=request.user.id)
    ###########################################
    # houseInstance = House.objects.get(id=pk)
    # if houseInstance.owner != request.user:
    #     return redirect('login')
    #
    # if len(houseInstance.room_set.all()) > 0:
    #     return redirect('house-room', pk=pk, rpk=houseInstance.room_set.first().id)
    # return redirect('create-room', pk=pk)
    ######################################
    #
    # context = {'houses': houses, 'house': houseInstance}
    # return render(request, 'house.html', context)


@login_required(login_url='login')
def partialHouse(request, pk):
    selected_house = get_object_or_404(House, id=pk)
    dashboard, created = Dashboard.objects.get_or_create(user=request.user, house=selected_house)
    # context = {'houses': houses, 'devices': devices, 'location': 'Dashboard', 'selected_house': selected_house,
    #            'role': 'owner' if selected_house.owner == request.user else 'member'}
    context = {'selected_house': selected_house,
               'dashboard': dashboard}

    address = f'{selected_house.city}, {selected_house.country}'
    weather_response = requests.get(
        "https://api.weatherapi.com/v1/current.json",
        params={"key": django_settings.WEATHER_API_KEY, "q": address}
    )
    weather_data = weather_response.json()
    context['condition'] = weather_data['current']['condition']['text']
    context['icon'] = weather_data['current']['condition']['icon']
    context['temp_c'] = weather_data['current']['temp_c']
    context['temp_f'] = weather_data['current']['temp_f']
    return render(request, 'dashboard_partial.html', context)


@login_required(login_url='login')
def houseRooms(request, pk):
    # TODO: Add check to see if the user is owner or member in the house (chosen with PK)
    selected_house = get_object_or_404(House, id=pk)
    rooms = Room.objects.all().filter(house=selected_house)
    num_devices = len(RoomDevice.objects.all().filter(room__house=selected_house))
    return render(request, 'rooms.html',
                  {'rooms': rooms, 'selected_house': selected_house, 'devices': num_devices,
                   'location': 'Rooms'})


@login_required(login_url='login')
def houseRoom(request, pk, rpk):
    houseInstance = House.objects.get(id=pk)
    editForm = HouseForm(instance=houseInstance)

    form = RoomForm()
    room = Room.objects.all().filter(id=rpk)
    roomInstance = Room.objects.get(id=rpk)
    roomEditForm = RoomForm(instance=roomInstance)

    context = {'house': houseInstance, 'room': room[0], 'form': form, 'editForm': editForm,
               'roomEditForm': roomEditForm}
    return render(request, 'house.html', context)


@login_required(login_url='login')
def inviteMember(request, pk):
    if request.method == 'POST':
        username = request.POST.get('username')
        selected_house = get_object_or_404(House, pk=pk)
        invited_user = User.objects.filter(username=username).first()
        if not invited_user:
            messages.error(request, f"User '{username}' does not exist.")
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        if invited_user == request.user:
            messages.error(request, "You cannot invite yourself.")
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        HouseInvitation.objects.create(
            house=selected_house,
            invited_user=invited_user,
            invited_by=request.user,
        )
        messages.success(request, f"Invitation sent to {invited_user.username}.")
        return redirect(request.META['HTTP_REFERER'])
    return redirect(request.META['HTTP_REFERER'])


@login_required(login_url='login')
def handleInvite(request, pk):
    invitation = get_object_or_404(HouseInvitation, pk=pk)
    action = request.GET.get('action')
    if action == 'accept':
        invitation.accepted = True
        invitation.house.members.add(invitation.invited_user)
        invitation.save()
    elif action == 'decline':
        invitation.delete()
    return redirect('home')


@login_required(login_url='login')
def removeMember(request, pk, mpk):
    selected_house = get_object_or_404(House, pk=pk)
    member = get_object_or_404(selected_house.members, id=mpk)
    selected_house.members.remove(member)
    return redirect(request.META['HTTP_REFERER'])


@login_required(login_url='login')
def houseDevices(request, pk):
    device_param = request.GET.get('device')  # returns None if not present
    room_param = request.GET.get('room')
    selected_house = get_object_or_404(House, id=pk)
    houseDevices = RoomDevice.objects.filter(room__house=selected_house).order_by('id')
    context = {}
    if device_param:
        houseDevices = houseDevices.filter(name__icontains=device_param)
        context['deviceValue'] = device_param

    # Filter by room if provided
    if room_param:
        houseDevices = houseDevices.filter(room=room_param)
        context['selected_room'] = int(room_param)
    rooms = Room.objects.all().filter(house=selected_house)
    onlineDevices = houseDevices.filter(status="online")
    offlineDevices = houseDevices.filter(status="offline")
    context['devices'] = houseDevices
    context['total'] = len(houseDevices)
    context['online'] = len(onlineDevices)
    context['offline'] = len(offlineDevices)
    context['selected_house'] = selected_house
    context['rooms'] = rooms
    context['location'] = 'Devices'

    # TODO: add model logic for online/offline and pass it to the context
    return render(request, 'devices_page.html',
                  context)


@login_required(login_url='login')
def houseGroups(request, pk):
    selected_house = get_object_or_404(House, id=pk)
    groups = Group.objects.filter(house=selected_house)
    action = request.GET.get('action')
    if action:
        group = int(request.GET.get('group'))
        if not group:
            messages.error(request, 'No group selected')
        action = Action.objects.get(id=int(action))
        values = {}
        valueNames = action.parameters_schema  # already a dict
        for key in valueNames.keys():
            if request.GET.get(key) is not None:
                values[key] = int(request.GET.get(key)) if valueNames[key] == 'number' else request.GET.get(key)
            else:
                messages.error(request, f'Missing value: {key}')
        action.handleGroupAction(group, values)
        return redirect('house-groups', pk)
    return render(request, 'groups.html', {'groups': groups, 'selected_house': selected_house, 'location': 'Groups'})


@login_required(login_url='login')
def createGroup(request, pk):
    selected_house = get_object_or_404(House, id=pk)
    if request.method == 'POST':
        if not request.POST.get('name', '').strip():
            messages.error(request, "You must enter a name.")
        device_object_str = request.POST.get('device_object', '[]')  # default to empty list
        groupDevices = json.loads(device_object_str)
        if len(groupDevices) == 0:
            messages.error(request, "You must enter at least one device.")
        description = request.POST.get('description', '')
        group = Group.objects.create(name=request.POST.get('name'), house=selected_house, description=description)
        group.devices.add(*groupDevices)

    devices = RoomDevice.objects.filter(room__house=selected_house)
    return render(request, 'create_group.html',
                  {'devices': devices, 'selected_house': selected_house, 'location': 'Create Group'})


@login_required(login_url='login')
def houseAutomation(request, pk):
    selected_house = get_object_or_404(House, id=pk)
    automations = AutomationRule.objects.filter(house=selected_house)
    return render(request, 'automation.html',
                  {'automations': automations, 'selected_house': selected_house, 'location': 'Automation'})


@login_required(login_url='login')
def addAutomation(request, pk):
    selected_house = get_object_or_404(House, id=pk)
    if request.method == 'POST':
        name = request.POST.get('name', '')
        description = request.POST.get('description', '')
        operators = json.loads(request.POST.get('operator_object', '[]'))
        triggers = json.loads(request.POST.get('trigger_object', '{}'))
        actions = json.loads(request.POST.get('action_object', '{}'))

        brackets = [trigger['leftBrackets'] + trigger['rightBrackets'] for trigger in triggers.values()]
        brackets = "".join(brackets)

        print(brackets)
        print(f'brackets good = {checkBrackets(brackets)}')
        print(name)
        createdRule = AutomationRule.objects.create(name=name, description=description, house=selected_house)
        actionsCounter = 0
        for action in actions.values():
            actionObject = Action.objects.get(id=int(action['action']))
            temp = AutomationAction.objects.create(rule=createdRule, action_type=action['actionType'],
                                                   execution_order=actionsCounter, action=actionObject,
                                                   parameters=action['values'])
            if action['actionType'] == 'device_action':
                device = RoomDevice.objects.get(id=int(action['device']))
                temp.device = device
                temp.save()
            elif action['actionType'] == 'group_action':
                group = Group.objects.get(id=int(action['group']))
                temp.group = group
                temp.save()
            actionsCounter += 1

        conditionString = ""
        triggerCount = 0
        for trigger in triggers.values():
            print(trigger)
            conditionString = conditionString + trigger['leftBrackets'] + str(triggerCount + 1) + trigger[
                'rightBrackets'] + \
                              (operators[triggerCount] if len(operators) > triggerCount else "")
            print(f'condition string: {conditionString}')
            AutoCondition = AutomationCondition.objects.create(rule=createdRule, condition_type=trigger['triggerType'],
                                                               operator=trigger['operator'])
            if trigger['triggerType'] == 'state_value':
                device = RoomDevice.objects.get(id=int(trigger['device']))
                state = State.objects.get(id=int(trigger['state']))
                print('print(state)')
                print(state)
                AutoCondition.state_field = state
                AutoCondition.device = device
                AutoCondition.target_value = trigger['value']
                AutoCondition.save()
            elif trigger['triggerType'] == 'schedule':
                AutoCondition.time = trigger['value']
                AutoCondition.days_of_week = trigger['daysOfWeek']
                if trigger['specificDate'] != '':
                    AutoCondition.specific_date = trigger['specificDate']
                AutoCondition.save()
            elif trigger['triggerType'] == 'action_trigger':
                signal = Signal.objects.get(id=int(trigger['action']))
                device = RoomDevice.objects.get(id=int(trigger['device']))
                AutoCondition.device = device
                AutoCondition.trigger_action = signal
                AutoCondition.save()
            elif trigger['triggerType'] == 'weather':
                AutoCondition.weather_condition = trigger['weatherCondition']
                AutoCondition.check_forecast_hours = 24 if trigger['when'] == 'tomorrow' else -24 if trigger[
                                                                                                         'when'] == 'yesterday' else 0
                AutoCondition.save()
            triggerCount += 1
        print(f'final condition string: {conditionString}')
        createdRule.condition_expression = conditionString
        createdRule.save()
        print(conditionString)
        print(description)
        print(triggers)
        print(operators)
        print(actions)

    devices = RoomDevice.objects.filter(room__house=selected_house)
    actions = Action.objects.all()
    states = State.objects.all()
    signals = Signal.objects.all()
    groups = Group.objects.filter(house=selected_house)
    condition_types = [condition[0] for condition in AutomationCondition.CONDITION_TYPES]
    return render(request, 'add_automation.html',
                  {'selected_house': selected_house, 'devices': devices, 'actions': actions, 'states': states,
                   'signals': signals, 'groups': groups, 'condition_types': condition_types,
                   'location': 'Add Automation'})


@login_required(login_url='login')
def toggleAutomation(request, pk):
    selected_house = get_object_or_404(House, id=pk)
    automation = request.GET.get("automation", None)
    print(f'automation: {automation}')
    if not automation:
        messages.error(request, "Bad Request")
    automation = int(automation)
    automation = get_object_or_404(AutomationRule, id=automation)
    print(request.GET.get("is_active", False))
    active = request.GET.get("is_active", None)
    if active:
        active = True if request.GET.get("is_active") == "true" else False
    print(active)
    automation.is_active = active
    automation.save()
    return redirect('house-automation', pk=pk)


@login_required(login_url='login')
def deleteAutomation(request, pk):
    selected_house = get_object_or_404(House, id=pk)
    automation = request.GET.get("automation", None)
    print(f'automation: {automation}')
    if not automation:
        messages.error(request, "Bad Request")
    automation = int(automation)
    automation = get_object_or_404(AutomationRule, id=automation)
    automation.delete()
    return redirect('house-automation', pk=pk)


def checkBrackets(brackets):
    stack = []

    for bracket in brackets:
        if bracket == '(':
            stack.append(bracket)
        else:
            if len(bracket) > 0:
                stack.pop()
            else:
                return False
    return len(stack) == 0


@login_required(login_url='login')
def housePowerUsage(request, pk):
    selected_house = get_object_or_404(House, id=pk)
    # TODO: add model logic for online/offline and pass it to the context
    return render(request, 'power_usage_page.html', {'selected_house': selected_house, 'location': 'Power Usage'})


@login_required(login_url='login')
def houseMembers(request, pk):
    selected_house = get_object_or_404(House, id=pk)
    print(([selected_house.owner] + list(selected_house.members.all())))
    return render(request, 'members.html', {'selected_house': selected_house,
                                            'members': ([selected_house.owner] + list(selected_house.members.all())),
                                            'location': 'Members'})


@login_required(login_url='login')
def createHouse(request):
    form = HouseForm()
    if request.method == 'POST':
        form = HouseForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.owner = request.user
            room.save()
            return redirect('house', pk=room.id)

    houses = House.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct()
    context = {'form': form, 'houses': houses, 'create': True}
    return render(request, 'house_form.html', context)


@login_required(login_url='login')
def updateHouse(request, pk):
    houseInstance = House.objects.get(id=pk)
    form = HouseForm(instance=houseInstance)

    if request.user != houseInstance.owner:
        return redirect('login')

    if request.method == 'POST':
        form = HouseForm(request.POST, instance=houseInstance)
        if form.is_valid():
            form.save()
            return redirect('house', pk=houseInstance.id)

    context = {'form': form}
    return render(request, 'house_form.html', context)


@login_required(login_url='login')
def deleteHouse(request, pk):
    deleteHouse = House.objects.get(id=pk)

    if request.user != deleteHouse.owner:
        return redirect('login')

    if request.method == 'POST':
        deleteHouse.delete()
        return redirect('home')

    return render(request, 'delete.html', {'obj': deleteHouse})


@login_required(login_url='login')
def createRoom(request, pk):
    roomType = request.GET.get("type", "")
    if roomType != "":
        form = RoomForm({'type': roomType, 'name': ''})
    else:
        form = RoomForm()
    houseInstance = House.objects.get(id=pk)

    if houseInstance.owner != request.user and request.user not in houseInstance.members:
        return redirect('login')

    if request.method == 'POST':
        houseInstance = House.objects.all().filter(id=pk)
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.house = houseInstance[0]
            room.save()
            return redirect('house-rooms', pk=pk)

    houses = House.objects.all().filter(owner=request.user.id)
    editForm = HouseForm(instance=houseInstance)
    context = {'form': form, 'houses': houses, 'house': houseInstance, 'editForm': editForm}
    return render(request, 'room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    roomInstance = Room.objects.get(id=pk)
    form = RoomForm(instance=roomInstance)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=roomInstance)
        if form.is_valid():
            form.save()
            return redirect(request.GET.get("next"))

    # houses = House.objects.all().filter(owner=request.user.id)
    context = {'form': form}
    return render(request, 'room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    roomInstance = Room.objects.get(id=pk)

    if request.user != roomInstance.house.owner:
        logout(request)
        return redirect('login')

    if request.method == 'POST':
        roomInstance.delete()
        return redirect('house', pk=roomInstance.house.id)

    houses = House.objects.all().filter(owner=request.user.id)
    return render(request, 'delete.html', {'obj': roomInstance, 'houses': houses})


@login_required(login_url='login')
def toggleDeviceDashboard(request, pk):
    device = Device.objects.get(id=pk)
    if device.room.house.owner != request.user:
        logout(request)
        return redirect('login')
    device.dashboard = not device.dashboard
    device.save()

    return redirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='login')
def deleteDevice(request, pk):
    device = RoomDevice.objects.get(id=pk)
    houses = House.objects.all().filter(Q(owner=request.user) | Q(members=request.user))
    if device.room.house not in houses:
        logout(request)
        return redirect('login')

    if request.method == 'POST':
        device.delete()
        return redirect(request.GET.get('next'))

    return render(request, 'delete.html', {'obj': device, 'houses': houses})


@csrf_exempt
def connectDevice(request, key):
    print("connectDevice")
    print(key)
    if request.method == 'POST':
        device_config = json.loads(request.body)
        connect_device = Device.objects.get(id=key)
        if connect_device.password != device_config['password']:
            raise Http404('Device password mismatch')
        connect_device.type = device_config['type']
        connect_device.save()
        print(connect_device)
        return HttpResponse('Connected')
    return HttpResponse('Connected')


def existsDevice(request, pk):
    deviceInstance = get_object_or_404(Device, id=pk)
    return HttpResponse('Exists')


@login_required(login_url='login')
def addQRDevice(request, pk):
    if request.method == 'POST':
        mac = request.POST.get('mac').upper()
        token = request.POST.get('token')
        device = Device.objects.filter(mac_address=mac, token=token).first()
        if device is None:
            messages.error(request, "MAC address doesn't match token")
        else:
            room = request.POST.get('room')
            room = Room.objects.get(id=room)
            name = request.POST.get('name')
            RoomDevice.objects.create(name=name, room=room, device=device)

    selected_house = get_object_or_404(House, id=pk)
    return render(request, 'add_qr_device.html', {'selected_house': selected_house})


@login_required(login_url='login')
def addManualDevice(request, pk):
    if request.method == 'POST':
        mac = request.POST.get('mac').upper()
        token = request.POST.get('token')
        device = Device.objects.filter(mac_address=mac, token=token).first()
        if device is None:
            messages.error(request, "MAC address doesn't match token")
        else:
            room = request.POST.get('room')
            room = Room.objects.get(id=room)
            name = request.POST.get('name')
            RoomDevice.objects.create(name=name, room=room, device=device)

    selected_house = get_object_or_404(House, id=pk)
    return render(request, 'add_manual_device.html', {'selected_house': selected_house})


@login_required(login_url='login')
def addDevice(request, pk):
    if request.method == 'POST':
        device_id = request.POST.get('id')
        print(device_id)
        # deviceInstance = Device.objects.get(id=device_id)
        # form = DeviceForm(request.POST, instance=deviceInstance)
        # if form.is_valid():
        #     form.save()
        #     return redirect('house-room', pk=deviceInstance.room.house.id, rpk=deviceInstance.room.id)

    device = Device.objects.create(room_id=pk)
    # form = DeviceForm(instance=device)
    return render(request, 'device_form.html', {'device': device})


@login_required(login_url='login')
def cancelDevice(request, pk):
    device = Device.objects.get(id=pk)
    device.delete()
    print(device)
    return redirect('house-room', pk=device.room.house.id, rpk=device.room.id)


@login_required(login_url='login')
def updateDevice(request, pk):
    device = RoomDevice.objects.get(id=pk)
    selected_house = get_object_or_404(House, id=device.room.house.id)
    if request.method == 'POST':
        form = RoomDeviceForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            return redirect('house', pk=device.room.house.id)

    return render(request, 'device_form.html', {'device': device, 'selected_house': selected_house})


@login_required(login_url='login')
def controlDevice(request):
    action = request.GET.get('action')
    if action:
        device = int(request.GET.get('device'))
        deviceObject = RoomDevice.objects.get(id=device)
        if not device:
            messages.error(request, 'No device selected')
        action = Action.objects.get(id=int(action))
        values = {}
        valueNames = action.parameters_schema  # already a dict
        for key in valueNames.keys():
            if request.GET.get(key) is not None:
                values[key] = int(request.GET.get(key)) if valueNames[key] == 'number' else request.GET.get(key)
            else:
                messages.error(request, f'Missing value: {key}')
        action.handleDeviceAction(deviceObject, values)
    time.sleep(0.3)
    return redirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='login')
def addWidget(request, pk):
    widget_type = request.GET.get('type')
    device_or_widget_id = request.GET.get('id')
    selected_house = get_object_or_404(House, id=pk)
    if widget_type and device_or_widget_id:
        dashboard = Dashboard.objects.get(user=request.user, house=selected_house)
        if widget_type == "widget":
            widget = Widget.objects.get(id=device_or_widget_id)
            dashboard.widgets.add(widget)
        elif widget_type == "device":
            device = RoomDevice.objects.get(id=device_or_widget_id)
            dashboard.devices.add(device)

    return redirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='login')
def removeWidget(request, pk):
    widget_type = request.GET.get('type')
    device_or_widget_id = request.GET.get('id')
    selected_house = get_object_or_404(House, id=pk)
    if widget_type and device_or_widget_id:
        dashboard = Dashboard.objects.get(user=request.user, house=selected_house)
        if widget_type == "widget":
            widget = Widget.objects.get(id=device_or_widget_id)
            dashboard.widgets.remove(widget)
        elif widget_type == "device":
            device = RoomDevice.objects.get(id=device_or_widget_id)
            dashboard.devices.remove(device)

    return redirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='login')
def updateGroup(request, pk):
    group = Group.objects.get(id=pk)
    selected_house = get_object_or_404(House, id=group.house.id)
    print(selected_house)
    devices = RoomDevice.objects.filter(room__house=selected_house)
    if request.method == 'POST':
        if not request.POST.get('name', '').strip():
            messages.error(request, "You must enter a name.")
        device_object_str = request.POST.get('device_object', '[]')  # default to empty list
        groupDevices = json.loads(device_object_str)
        if len(groupDevices) == 0:
            messages.error(request, "You must enter at least one device.")
        description = request.POST.get('description', '')
        group = Group.objects.get(id=pk)
        group.update(name=request.POST.get('name'), house=selected_house, description=description)
        group.devices.set(groupDevices)
        return redirect(request.GET.get('next'))
    return render(request, 'update_group.html',
                  {'devices': devices, 'group': group, 'selected_house': selected_house, 'location': 'Update Group'})


@login_required(login_url='login')
def deleteGroup(request, pk):
    group = Group.objects.get(id=pk)
    selected_house = get_object_or_404(House, id=group.house.id)
    if request.user != group.house.owner and request.user not in group.house.members.all():
        logout(request)
        return redirect('login')

    if request.method == 'POST':
        group.delete()
        return redirect(request.GET.get('next'))

    houses = House.objects.all().filter(owner=request.user.id)
    return render(request, 'delete.html', {'obj': group, 'houses': houses, 'selected_house': selected_house})


# def fuzzy_match(text, queryset, min_score=70, key=lambda x: x.command):
#     text = text.lower()
#     best_score = 0
#     best_match = None
#     for item in queryset:
#         score = fuzz.partial_ratio(key(item).lower(), text)
#         if score > best_score:
#             best_score = score
#             best_match = item
#     if best_score >= min_score:
#         return best_match
#     return None


def clean_text(text):
    text = text.lower()
    text = re.sub(r"\b(set|turn|on|off|to|the|device)\b", "", text)
    return text.strip()


def fuzzy_match(text, queryset, min_score=70, key=lambda x: x.command):
    text = clean_text(text)

    choices = {key(item).lower(): item for item in queryset}
    best = process.extractOne(query=text, choices=list(choices.keys()), scorer=fuzz.WRatio)

    if best and best[1] >= min_score:
        matched_text, score = best[0], best[1]
        return choices[matched_text]

    return None


def fuzzy_match_action(text, queryset, min_score=70, key=lambda x: x.command):

    choices = {key(item).lower(): item for item in queryset}
    best = process.extractOne(query=text, choices=list(choices.keys()), scorer=fuzz.WRatio)

    if best and best[1] >= min_score:
        matched_text, score = best[0], best[1]
        return choices[matched_text]

    return None



@csrf_exempt
@login_required(login_url='login')
def processCommand(request, pk):
    selected_house = get_object_or_404(House, id=pk)
    if request.method == "POST":
        data = json.loads(request.body)
        text = data.get("text", "").lower()
        print(text)
        device = fuzzy_match(text, RoomDevice.objects.filter(room__house=selected_house), key=lambda d: d.name)
        if not device:
            return JsonResponse({"message": "No matching device found."})

        print(device)

        action = fuzzy_match_action(text, device.device.type.actions.all(), key=lambda a: a.command)
        if not action:
            return JsonResponse({"message": "No matching action found for this device."})
        print(action)
        import re
        value_match = re.search(r'\d+', text)
        value = {}
        if len(action.parameters_schema.keys()) > 0:
            print(list(action.parameters_schema.keys())[0])
            value = {list(action.parameters_schema.keys())[0]: int(value_match.group()) if value_match else None}

        # 4. Execute
        result = action.handleDeviceAction(device, value, True)
        return JsonResponse({"message": result})

    return JsonResponse({"message": "Invalid request."})


@login_required(login_url='login')
def voiceCommand(request, pk):
    selected_house = get_object_or_404(House, id=pk)
    return render(request, 'voice_command.html', {'selected_house': selected_house})
