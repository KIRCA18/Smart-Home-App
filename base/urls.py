from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),
    path('', views.home, name="home"),
    path('settings/', views.settings, name="settings"),
    path('house/<str:pk>', views.house, name="house"),
    path('house/<str:pk>/room/<str:rpk>', views.houseRoom, name="house-room"),
    path('create-house/', views.createHouse, name="create-house"),
    path('update-house/<str:pk>/', views.updateHouse, name="update-house"),
    path('delete-house/<str:pk>/', views.deleteHouse, name="delete-house"),
    path('house/<str:pk>/create-room/', views.createRoom, name="create-room"),
    path('update-room/<str:pk>/', views.updateRoom, name="update-room"),
    path('delete-room/<str:pk>', views.deleteRoom, name="delete-room"),
    path('toggle-device/<str:pk>', views.toggleDeviceDashboard, name="toggle-device"),
    path('delete-device/<str:pk>', views.deleteDevice, name="delete-device"),
    path('connect-device/<str:key>', views.connectDevice, name="connect-device"),
    path('exists-device/<str:pk>', views.existsDevice, name="exists-device"),
    path('control-device/<str:pk>', views.controlDevice, name="control-device"),
    path('devices/', views.devices, name="devices"),
    path('update-device/<str:pk>', views.updateDevice, name="update-devices"),
    path('add-device/<str:pk>', views.addDevice, name="add-device"),
    path('cancel-device/<str:pk>', views.cancelDevice, name="cancel-device"),


]
