from django.shortcuts import render , redirect
from django.contrib import messages
from .models import Room,Topic,Message,User
from django.db.models import Q, Count
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from .forms import UserForm


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login the user
            login(request, user)
            return redirect('home')  
        else:
            
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'base/login.html') 


def logoutuser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        users = User.objects.all()
        for user in users:
            if user.username == username:
                messages.error(request, "Username already exits!")
                return render(request, 'base/signup.html')


        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'base/signup.html')  # Reload the same page with error message

        # Optionally, you can add more validations for username and password here

        # If passwords match, create a new user
        user = User.objects.create_user(username=username, password=password)
        user.first_name = fullname
        user.save()

        messages.success(request, "Account created successfully!")
        login(request,user)
        return redirect('home')  # Redirect to the login page after successful signup

    return render(request, 'base/signup.html')  # Render the signup form



def home(request):
    q = request.GET.get('q', '') 
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(host__username__icontains=q)
    )
    room_messages = Message.objects.filter(Q(room__topic__name__icontains = q))

    topics = Topic.objects.all()
    
    topics = Topic.objects.annotate(room_count=Count('room'))

    context = {'rooms': rooms, 'topics': topics, 
                'room_messages':room_messages,
               }
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id = pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body'),
        )
        return redirect('room', pk=room.id)


    context = {'room' : room, 'room_messages' : room_messages , 'participants' :participants}        
    return render(request, 'base/room.html',context)


login_required(login_url='login_page')
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()  # Rooms where the user is the host
    participants = User.objects.filter(participants__in=rooms).distinct()  # Get all unique participants
    room_messages = user.message_set.all()
    topics = Topic.objects.annotate(room_count=Count('room'))
    
    context = {
        'user': user,
        'rooms': rooms,
        'participants': participants,  # Unique participants
        'room_messages': room_messages,
        'topics': topics
    }
    return render(request, 'base/user_profile.html', context)
@login_required(login_url='login_page')
def createRoom(request):
    topics = Topic.objects.all() 
    if request.method == 'POST':
        # Retrieve data from the POST request
        room_name = request.POST.get('room_name')
        topic_name = request.POST.get('topic')
        room_about = request.POST.get('room_about')

        # Get or create the topic
        topic, created = Topic.objects.get_or_create(name=topic_name)

        # Create the new room
        room = Room.objects.create(
            host=request.user,
            name=room_name,
            topic=topic,
            description=room_about,
        )

        # Redirect to the home page
        return redirect('room', pk = room.id)

    context = {'topics': topics}
    return render(request, 'base/create-room.html', context)


def setting(request):
    return render(request,'base/settings.html')

def topics(request):
    q = request.GET.get('q', '') 
    topics = Topic.objects.filter(Q(name__icontains=q))
    
    context = {'topics' : topics} 
    return render(request,'base/topics.html',context)

@login_required(login_url='login_page')
def UpdateRoom(request,pk): 
    room = Room.objects.get(id=pk)
    topics = Topic.objects.all()
    if request.user != room.host:
        return redirect("home")
     

    if request.method == 'POST':
        # Retrieve data from the POST request
        room_name = request.POST.get('room_name')
        topic = request.POST.get('topic')
        room_about = request.POST.get('room_about')

        # Get or create the topic
        topic, created = Topic.objects.get_or_create(name=topic)

        room.name = room_name
        room.topic = topic
        room.description = room_about
        room.save()

        # Redirect to the home page
        return redirect('room', pk = room.id)
    
    context = {'room' : room , 'topics' : topics}
    return render(request,'base/edit_room.html',context)   


@login_required(login_url='login_page')
def UpdateUser(request):
    
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST,instance=user)
        if form.is_valid():
            form.save()
            return redirect('userProfile', pk = user.id)
    return render(request,'base/edit-user.html', {'form' : form})
 

@login_required(login_url='login_page')
def deleteRoom(request,pk):
    objct = 'room' 
    room = Room.objects.get(id = pk)
    if request.user != room.host:
        return HttpResponse("You Are not Allowed Here")

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    
    context = {'obj':room, 'objct':objct}
    return render(request,'base/delete.html',context)

@login_required(login_url='login_page')
def deleteMessage(request,pk):
    objct = 'message'
    message = Message.objects.get(id = pk)
    id = message.room.id
    if request.user != message.user:
        return redirect('room', pk = id)
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    context = {'obj':message, 'objct' : objct }
    return render(request,'base/delete.html',context)

def recentActivities(request):
    q = request.GET.get('q', '') 
    room_messages = Message.objects.filter(Q(room__topic__name__icontains = q))
    return render(request,'base/activity.html', {'room_messages' : room_messages})