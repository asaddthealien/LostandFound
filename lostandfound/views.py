from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Item, LostItem, FoundItem, User, Category, Claim, Notification
from django.contrib.auth import authenticate, login, logout
from .forms import Userform
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction, connection
from django.core.mail import send_mail
from django.conf import settings as django_settings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pytesseract
import re
from PIL import Image

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ── OCR: Extract roll number from ID card image ──
def extract_roll_number(image_file):
    try:
        img = Image.open(image_file)
        text = pytesseract.image_to_string(img)
        # FAST/NU roll number format: 24k-0606 or 24K-0606
        match = re.search(r'\b\d{2}[kK]-\d{4}\b', text)
        if match:
            return match.group(0).upper()
    except Exception:
        pass
    return None

# ── Email: Notify student when their ID card is found ──
def notify_id_card_owner(roll_number, item_name, location):
    # Construct NU email from roll number: 24k-0606 → k240606@nu.edu.pk
    parts = roll_number.lower().split('-')  # ['24k', '0606']
    if len(parts) == 2:
        year_letter = parts[0]   # '24k'
        digits = parts[1]        # '0606'
        letter = ''.join(filter(str.isalpha, year_letter))   # 'k'
        year = ''.join(filter(str.isdigit, year_letter))     # '24'
        student_email = f"{letter}{year}{digits}@nu.edu.pk"

        try:
            send_mail(
                subject='Your ID Card Has Been Found — FAST Lost & Found',
                message=f"""Dear Student ({roll_number}),

Your student ID card has been found and reported on the FAST Lost & Found system.

Item: {item_name}
Location: {location}

Please log in to https://lostandfound.example.com and submit a claim to recover it.

— FAST Lost & Found System""",
                from_email=django_settings.EMAIL_HOST_USER,
                recipient_list=[student_email],
                fail_silently=True,
            )
            return student_email
        except Exception:
            pass
    return None

# ── AI Matching Algorithm ──
# Uses TF-IDF vectorization + cosine similarity (real NLP technique)
# Combined with category match and location bonus for best results
def get_ai_matches(lost_item, top_n=5):
    found_items = list(FoundItem.objects.select_related('category', 'postedby').all())

    if not found_items:
        return []

    def item_text(item):
        parts = [item.name or '', item.description or '', item.location or '']
        return ' '.join(parts).lower()

    lost_text = item_text(lost_item)
    found_texts = [item_text(fi) for fi in found_items]

    # TF-IDF vectorization + cosine similarity
    all_texts = [lost_text] + found_texts
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    except Exception:
        similarities = np.zeros(len(found_items))

    scored = []
    for i, fi in enumerate(found_items):
        # Base score from TF-IDF cosine similarity (0 to 70 points)
        score = int(similarities[i] * 70)

        # Category match bonus (25 points)
        if fi.category_id == lost_item.category_id:
            score += 25

        # Location match bonus (5 points)
        if lost_item.location and fi.location:
            if lost_item.location.lower() in fi.location.lower() or fi.location.lower() in lost_item.location.lower():
                score += 5

        # Cap at 100
        score = min(score, 100)

        if score > 0:
            scored.append((score, fi))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_n]


# Create your views here.
def index(request):
    stats = {
        'total_lost': LostItem.objects.count(),
        'total_found': FoundItem.objects.count(),
        'total_claims': Claim.objects.count(),
    }
    return render(request, "lostandfound/index.html", {'stats': stats})


@login_required
def listitems(request, status):
    itemstatus = status.lower()
    search = request.GET.get('q', '').strip()

    if itemstatus == 'lost':
        itemobj = LostItem.objects.select_related('category', 'postedby')
        if search:
            itemobj = itemobj.filter(name__icontains=search)
        return render(request, "lostandfound/lostitems.html", {
            'items': itemobj,
            'search': search,
        })
    else:
        itemobj = FoundItem.objects.select_related('category', 'postedby')
        if search:
            itemobj = itemobj.filter(name__icontains=search)
        return render(request, "lostandfound/founditems.html", {
            'items': itemobj,
            'search': search,
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
        if request.POST.get('description'):
            itemobj.description = request.POST.get('description')

        itemobj.postedby = request.user
        itemobj.save()

        # If lost item posted → run AI matching
        if request.POST.get('status').lower() == 'lost':
            return redirect('matches', lost_id=itemobj.id)

        # If found item posted → run OCR to check if it's an ID card
        if request.POST.get('status').lower() == 'found' and itemobj.image:
            try:
                roll_number = extract_roll_number(itemobj.image)
                if roll_number:
                    student_email = notify_id_card_owner(roll_number, itemobj.name, itemobj.location)
                    if student_email:
                        messages.success(request, f"ID card detected! Roll number {roll_number} - notification sent to {student_email}.")
                    else:
                        messages.info(request, f"ID card detected! Roll number: {roll_number}. Could not auto-send email.")
            except Exception:
                pass

        return HttpResponseRedirect(reverse('listitems', args=(itemobj.status,)))

    else:
        categories = Category.objects.all()
        return render(request, "lostandfound/itempost.html", {'categories': categories})


# ── AI Matches Page ──
@login_required
def matches(request, lost_id):
    lost_item = get_object_or_404(LostItem, id=lost_id)
    results = get_ai_matches(lost_item)
    return render(request, "lostandfound/matches.html", {
        'lost_item': lost_item,
        'results': results,
    })


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

    return render(request, "lostandfound/register.html", {'form': form})


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

    return render(request, "lostandfound/claim.html", {'item_id': item_id})


@login_required
def notificationsview(request):
    notifications = Notification.objects.filter(receiver=request.user).order_by('-created_at')
    return render(request, "lostandfound/notifications.html", {'notifications': notifications})


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
                claimant_message = f"Your claim for item '{item_name}' has been verified and accepted."
                if claimobj.found_item:
                    founditemobj = claimobj.found_item
                    claimobj.found_item = None
                    claimobj.save(update_fields=["status", "found_item"])
                    founditemobj.delete()
            else:
                claimobj.status = Claim.STATUS_REJECTED
                claimant_message = f"Your claim for item '{item_name}' was reviewed and rejected."

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


@login_required
def myitems(request):
    lost_items = LostItem.objects.filter(postedby=request.user)
    found_items = FoundItem.objects.filter(postedby=request.user)
    return render(request, "lostandfound/myitems.html", {
        'lost_items': lost_items,
        'found_items': found_items,
    })


@login_required
def edititem(request, status, item_id):
    if status == 'lost':
        itemobj = get_object_or_404(LostItem, id=item_id, postedby=request.user)
    else:
        itemobj = get_object_or_404(FoundItem, id=item_id, postedby=request.user)

    if request.method == 'POST':
        itemobj.name = request.POST.get('name')
        itemobj.location = request.POST.get('location')
        if request.POST.get('description'):
            itemobj.description = request.POST.get('description')
        if request.FILES.get('image'):
            itemobj.image = request.FILES.get('image')

        categoryobj, _ = Category.objects.get_or_create(name=request.POST.get('category'))
        itemobj.category = categoryobj
        itemobj.save()

        messages.success(request, "Item updated successfully.")
        return redirect('myitems')

    return render(request, "lostandfound/edititem.html", {
        'item': itemobj,
        'status': status,
    })


@login_required
def deleteitem(request, status, item_id):
    if status == 'lost':
        itemobj = get_object_or_404(LostItem, id=item_id, postedby=request.user)
    else:
        itemobj = get_object_or_404(FoundItem, id=item_id, postedby=request.user)

    if request.method == 'POST':
        itemobj.delete()
        messages.success(request, "Item deleted successfully.")
        return redirect('myitems')

    return render(request, "lostandfound/deleteconfirm.html", {
        'item': itemobj,
        'status': status,
    })


@login_required
def dashboard(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                UPPER(u.username) AS username,
                u.email,
                COUNT(DISTINCT li.id) AS lost_posted,
                COUNT(DISTINCT fi.id) AS found_posted,
                COUNT(DISTINCT cl.id) AS claims_made,
                COALESCE(COUNT(DISTINCT li.id) + COUNT(DISTINCT fi.id), 0) AS total_activity
            FROM lostandfound_user u
            LEFT JOIN lostandfound_lostitem li ON li.postedby_id = u.id
            LEFT JOIN lostandfound_founditem fi ON fi.postedby_id = u.id
            LEFT JOIN lostandfound_claim cl ON cl.requestby_id = u.id
            WHERE u.id = %s
            GROUP BY u.id, u.username, u.email
        """, [request.user.id])
        row = cursor.fetchone()
        user_stats = {
            'username': row[0],
            'email': row[1],
            'lost_posted': row[2],
            'found_posted': row[3],
            'claims_made': row[4],
            'total_activity': row[5],
        } if row else {}

        cursor.execute("""
            SELECT 
                c.name AS category,
                COUNT(li.id) AS lost_count,
                COUNT(fi.id) AS found_count
            FROM lostandfound_category c
            LEFT JOIN lostandfound_lostitem li ON li.category_id = c.id
            LEFT JOIN lostandfound_founditem fi ON fi.category_id = c.id
            GROUP BY c.name
            ORDER BY (COUNT(li.id) + COUNT(fi.id)) DESC
        """)
        categories = cursor.fetchall()

    return render(request, "lostandfound/dashboard.html", {
        'user_stats': user_stats,
        'categories': categories,
    })
