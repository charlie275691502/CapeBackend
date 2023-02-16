from django.shortcuts import render

# Create your views here.
def hello(request):
    return render(request, 'hello.html')

def rooms(request):
    return render(request, 'index.html')

def room(request, room_name):
    return render(request, 'room.html', {'room_name': room_name})
    