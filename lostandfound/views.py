from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Item, LostItem, FoundItem, User, Category, Claim, Notification
from django.contrib.auth import authenticate, login, logout
from .forms import Userform
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    return render(request, "lostandfound/index.html")

@login_required
def listitems(request, status):
    itemstatus = status.lower()

    if itemstatus == 'lost':
        itemobj = LostItem.objects.all()
        return render(request, "lostandfound/founditem.html", {
        'items': itemobj
    })
    else:
        itemobj = FoundItem.objects.all()
        return render(request, "lostandfound/lostitems.html", {
        'items': itemobj
    })

@login_required
def itempost(request):
    if request.method == 'POST':
        if request.POST.get('status').lower() == 'lost':
            itemobj = LostItem()
        else:
            itemobj = FoundItem()

        itemobj.name = request.POST.get('name')
        itemobj.location = request.POST.get('location')
        itemobj.image = request.FILES.get('image')

        categoryobj = Category(request.POST.get('category'))
        categoryobj.save()

        itemobj.category = categoryobj
        #description is optional
        if request.POST.get('description'):
            itemobj.description = request.POST.get('description')
            
        itemobj.save()

        return HttpResponseRedirect(reverse('listitems', args=(itemobj.status,)))
    
    else:
        return render(request, "lostandfound/itempost.html")

def registerview(request):
    if request.method == "POST":
        form = Userform(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
        
    else:
        form = Userform()

    return render(request, "lostandfound/register.html", {
        'form': form
    })

def loginview(request):
    if request.method == "POST":
        userobj = User.objects.get(User.name == request.POST.get('username'))
        if request.POST.get('password') == userobj.password:
            login(request, userobj)
            return redirect("index")
        else: 
            messages.error(request, "username or password not correct")

    return render(request, "lostandfound/login.html")

def logoutview(request):
    logout(request)
    return redirect('loginview')


def claim(request, item_id):
    if request.method == "POST":
        itemobj = FoundItem.objects.get(id = item_id)
        claimobj = Claim()
        claimobj.found_item = itemobj
        claimobj.requestby = request.user
        claimobj.proof = request.POST.get("proof")
        claimobj.status = "Pending"
        if request.FILES.get('image'):
            claimobj.image = request.FILES.get('image')
        claimobj.save()

        notificationobj = Notification()
        notificationobj.claimreq = claimobj
        notificationobj.sender = request.user
        notificationobj.receiver = claimobj.found_item.postedby
        notificationobj.save()

        messages.success("your claim request has been sucessfully submitted")
        return redirect('index')
    
    return render(request, "lostandfound/claim.html")


def notificationsview(request):
    notifications = Notification.objects.get(receiver = request.user)
    return render(request, "lostandfound/notifications.html", {
        'notifications': notifications
    })
    

# def reviewclaim(request, notification_id):
