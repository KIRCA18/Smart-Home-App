import json

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.forms import UserCreationForm
from .forms import HouseForm, MyUserCreationForm, RoomForm
from .models import House, User, Room, Device


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
        form = MyUserCreationForm(request.POST)
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


def automationPage(request):
    houses = House.objects.all().filter(owner=request.user.id)
    devices = Device.objects.all().filter(dashboard=True, room__house__owner=request.user.id)
    context = {'houses': houses, 'devices': devices}
    return render(request, 'home.html', context)

@login_required(login_url='login')
def home(request):
    # print(request.user)
    houses = House.objects.all().filter(owner=request.user.id)
    devices = Device.objects.all().filter(dashboard=True, room__house__owner=request.user.id)
    context = {'houses': houses, 'devices': devices}
    return render(request, 'home.html', context)


@login_required(login_url='login')
def house(request, pk):
    # houses = House.objects.all().filter(owner=request.user.id)
    houseInstance = House.objects.get(id=pk)
    if houseInstance.owner != request.user:
        return redirect('login')

    if len(houseInstance.room_set.all()) > 0:
        return redirect('house-room', pk=pk, rpk=houseInstance.room_set.first().id)
    return redirect('create-room', pk=pk)
    #
    # context = {'houses': houses, 'house': houseInstance}
    # return render(request, 'house.html', context)


@login_required(login_url='login')
def houseRoom(request, pk, rpk):
    houseInstance = House.objects.get(id=pk)
    editForm = HouseForm(instance=houseInstance)

    form = RoomForm()
    room = Room.objects.all().filter(id=rpk)
    houses = House.objects.all().filter(owner=request.user.id)
    roomInstance = Room.objects.get(id=rpk)
    roomEditForm = RoomForm(instance=roomInstance)

    context = {'houses': houses, 'house': houseInstance, 'room': room[0], 'form': form, 'editForm': editForm,
               'roomEditForm': roomEditForm}
    return render(request, 'house.html', context)


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
    houses = House.objects.all().filter(owner=request.user.id)
    context = {'form': form, 'houses': houses}
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

    houses = House.objects.all().filter(owner=request.user.id)
    return render(request, 'delete.html', {'obj': deleteHouse, 'houses': houses})


@login_required(login_url='login')
def createRoom(request, pk):
    form = RoomForm()
    houseInstance = House.objects.get(id=pk)

    if houseInstance.owner != request.user:
        return redirect('login')

    if request.method == 'POST':
        houseInstance = House.objects.all().filter(id=pk)
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.house = houseInstance[0]
            room.save()
            return redirect('house', pk=pk)

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
            return redirect('house-room', pk=roomInstance.house.id, rpk=roomInstance.id)

    houses = House.objects.all().filter(owner=request.user.id)
    context = {'form': form, 'houses': houses}
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
    device = Device.objects.get(id=pk)
    houses = House.objects.all().filter(owner=request.user.id)
    if device.room.house.owner != request.user:
        logout(request)
        return redirect('login')

    if request.method == 'POST':
        device.delete()
        redirect('house-room', pk=device.room.house.id, rpk=device.room.id)

    return render(request, 'delete.html', {'obj': device, 'houses': houses})
