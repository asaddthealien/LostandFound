from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Item

# Create your views here.
def index(request):
    return render(request, "lostandfound/index.html")

def listitems(request, status):
    itemstatus = status.lower()
    itemobj = Item.objects.filter(status=itemstatus)
    if itemstatus == 'lost':
        return render(request, "lostandfound/claimitem.html", {
        'items': itemobj
    })
    else:
        return render(request, "lostandfound/lostitems.html", {
        'items': itemobj
    })
def itempost(request):
    if request.method == 'POST':
        itemobj = Item()
        if request.POST.get('name') and request.FILES.get('image') and request.POST.get('location'):
            itemobj.name = request.POST.get('name')
            itemobj.location = request.POST.get('location')
            itemobj.image = request.FILES.get('image')
            itemobj.status = request.POST.get('status')
            #description is optional
            if request.POST.get('description'):
                itemobj.description = request.POST.get('description')
            
            itemobj.save()

        return HttpResponseRedirect(reverse('listitems', args=(itemobj.status,)))
    
    else:
        return render(request, "lostandfound/itempost.html")

