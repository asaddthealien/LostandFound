from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Item, LostItem, FoundItem, User, Category, Claim, Notification
from django.contrib.auth import authenticate, login, logout
from .forms import Userform
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction

# Create your views here.
def index(request):
    return render(request, "lostandfound/index.html")

@login_required
def listitems(request, status):
    itemstatus = status.lower()

    if itemstatus == 'lost':
        itemobj = LostItem.objects.all()
        return render(request, "lostandfound/lostitems.html", {
        'items': itemobj
    })
    else:
        itemobj = FoundItem.objects.all()
        return render(request, "lostandfound/founditems.html", {
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

        categoryobj, _ = Category.objects.get_or_create(name=request.POST.get('category'))
        categoryobj.save()

        itemobj.category = categoryobj
        #description is optional
        if request.POST.get('description'):
            itemobj.description = request.POST.get('description')
        
        itemobj.postedby = request.user
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
        messages.error(request, "Please fix the form errors and try again.")
        
    else:
        form = Userform()

    return render(request, "lostandfound/register.html", {
        'form': form
    })

def loginview(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        userobj = authenticate(request, username=username, password=password)

        if userobj is not None:
            login(request, userobj)
            return redirect("index")

        messages.error(request, "username or password not correct")

    return render(request, "lostandfound/login.html")

def logoutview(request):
    logout(request)
    return redirect('login')


@login_required
def claim(request, item_id):
    itemobj = get_object_or_404(FoundItem, id=item_id)

    if itemobj.postedby == request.user:
        messages.error(request, "You cannot claim your own posted item.")
        return redirect('listitems', status='found')

    if request.method == "POST":
        claimobj = Claim()
        claimobj.found_item = itemobj
        claimobj.requestby = request.user
        claimobj.proof = request.POST.get("proof")
        claimobj.status = Claim.STATUS_PENDING
        if request.FILES.get('image'):
            claimobj.image = request.FILES.get('image')
        claimobj.save()

        notificationobj = Notification()
        notificationobj.title = "Claim Request"
        notificationobj.message = f"{request.user.username} submitted a claim for your found item '{itemobj.name}'."
        notificationobj.claimreq = claimobj
        notificationobj.sender = request.user
        notificationobj.receiver = claimobj.found_item.postedby
        notificationobj.save()

        messages.success(request, "Your claim request has been successfully submitted.")
        return redirect('index')
    
    return render(request, "lostandfound/claim.html", {
        'item_id': item_id
    })


@login_required
def notificationsview(request):
    notifications = Notification.objects.filter(receiver=request.user).order_by('-created_at')
    return render(request, "lostandfound/notifications.html", {
        'notifications': notifications
    })
    

@login_required
def reviewclaim(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, receiver=request.user)
    claimobj = notification.claimreq
    item_name = claimobj.found_item.name if claimobj.found_item else "the item"

    if request.method == "POST":
        decision = request.POST.get("decision")

        if claimobj.status != Claim.STATUS_PENDING:
            messages.error(request, "This claim has already been reviewed.")
            return redirect('notifications')

        if decision not in ["accept", "reject"]:
            messages.error(request, "Invalid review action.")
            return redirect('review', notification_id=notification.id)

        with transaction.atomic():
            if decision == "accept":
                claimobj.status = Claim.STATUS_ACCEPTED
                claimant_message = (
                    f"Your claim for item '{item_name}' has been verified and accepted."
                )
                if claimobj.found_item:
                    founditemobj = claimobj.found_item
                    claimobj.found_item = None
                    claimobj.save(update_fields=["status", "found_item"])
                    founditemobj.delete()
            else:
                claimobj.status = Claim.STATUS_REJECTED
                claimant_message = (
                    f"Your claim for item '{item_name}' was reviewed and rejected."
                )

            if decision == "reject":
                claimobj.save(update_fields=["status"])
            notification.is_read = True
            notification.save(update_fields=["is_read"])

            Notification.objects.create(
                title="Claim Review Update",
                message=claimant_message,
                claimreq=claimobj,
                receiver=claimobj.requestby,
                sender=request.user,
            )

        messages.success(request, "Claim review submitted successfully.")
        return redirect('notifications')

    return render(request, "lostandfound/reviewclaim.html", {
        'notification': notification,
        'claim': claimobj,
    })
