# FAST Lost & Found

FAST Lost & Found is a Django-based web application for managing lost and found items on campus. Users can post items they have lost or found, search listings, submit claims, and let item owners review those claims before approving or rejecting them.

The project is designed to make item recovery more organized and traceable. It supports user accounts, claim reviews, notifications, email alerts, and cloud image storage.

## Features

- User registration and login with FAST/NU email validation
- Post lost and found items with title, description, location, category, and image
- Search and browse listings
- Submit claim requests for found items
- Review claims from the owner dashboard
- Schedule handover details after approval
- Send notifications to both parties
- Store uploaded images through Cloudinary

## AI Features

- OCR-based roll number detection from uploaded card images
- Automatic email notification when a student ID card is detected
- AI-assisted matching of lost items with found items using TF-IDF and cosine similarity

## Handover Flow

1. A user submits a claim for a found item.
2. The owner reviews the request.
3. If approved, the owner enters a handover location and time.
4. The system generates a random exchange code.
5. Emails are sent to both the claimer and the owner with the handover details.

## Tech Stack

- Django 6
- PostgreSQL
- Cloudinary for image storage
- Tesseract OCR
- scikit-learn for item matching
- Bootstrap-free custom templates

## Setup

Use the step-by-step setup guide in [SETUP.md](SETUP.md).

In short:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Make sure `dbsetup.env` is configured before running the app.

## Project Structure

- `config/` - Django project settings and URL config
- `lostandfound/` - Main app with models, views, URLs, forms, and templates
- `media/` - Local media storage directory
- `README.md` - Project overview
- `SETUP.md` - Installation and contributor setup guide

## Notes for Deployment

- Set `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` in `dbsetup.env`
- Keep Cloudinary credentials configured for image uploads
- Run migrations after pulling the latest changes
- Ensure Tesseract is installed on the deployment machine

## Status

The project is complete and ready for deployment after environment and email settings are verified.