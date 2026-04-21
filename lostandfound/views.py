from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Item, LostItem, FoundItem, User
from django.contrib.auth import authenticate, login, logout
from .forms import Userform

# Create your views here.
def index(request):
    return render(request, "lostandfound/index.html")

def listitems(request, status):
    itemstatus = status.lower()

    if itemstatus == 'lost':
        itemobj = LostItem.objects.all()
        return render(request, "lostandfound/claimitem.html", {
        'items': itemobj
    })
    else:
        itemobj = FoundItem.objects.all()
        return render(request, "lostandfound/lostitems.html", {
        'items': itemobj
    })

def itempost(request):
    if request.method == 'POST':
        if request.POST.get('status').lower() == 'lost':
            itemobj = LostItem()
        else:
            itemobj = FoundItem()

        if request.POST.get('name') and request.FILES.get('image') and request.POST.get('location'):
            itemobj.name = request.POST.get('name')
            itemobj.location = request.POST.get('location')
            itemobj.image = request.FILES.get('image')
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
            return redirect('')
        
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
            return redirect('')
        else: 
                
