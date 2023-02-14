from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello),
    path('index/', views.index),
    path('index/<str:room_name>/', views.room, name='room')
]