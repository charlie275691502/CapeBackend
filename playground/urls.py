from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello),
    path('rooms/', views.rooms),
    path('rooms/<str:room_name>/', views.room, name='room')
]