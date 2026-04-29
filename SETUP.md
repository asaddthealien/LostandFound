# Project Setup Guide for Contributors

## Prerequisites
- Python 3.12+ installed
- PostgreSQL connection credentials (ask project owner for dbsetup.env)
- Git installed

## Initial Setup (First Time Only)

### 1. Clone the repository
```bash
git clone <repository-url>
cd "DBMS Project"
```

### 2. Create a Python virtual environment
```bash
python -m venv venv
```

### 3. Activate the virtual environment
**On Linux/macOS:**
```bash
source venv/bin/activate
```

**On Windows (CMD):**
```bash
venv\Scripts\activate.bat
```

**On Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Get the database configuration file
Ask the project owner (or check email) for the **dbsetup.env** file.

Once received, place it in the project root directory:
```
DBMS Project/
├── dbsetup.env    ← Place the file here
├── manage.py
├── requirements.txt
└── ... (other files)
```

**DO NOT commit dbsetup.env to Git** (it's in .gitignore for security).

The file should contain:
```
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=<password>
DB_HOST=<host>.c-2.ap-southeast-1.aws.neon.tech
DB_PORT=5432
```

### 6. Apply database migrations
```bash
python manage.py migrate
```

### 7. Create a superuser (optional, for admin panel)
```bash
python manage.py createsuperuser
```

### 8. Run the development server
```bash
python manage.py runserver
```

Open `http://localhost:8000` in your browser.

---

## Daily Development

### Start working each day:
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS

# Run the server
python manage.py runserver
```

### Apply new migrations (if database schema changed):
```bash
python manage.py migrate
```

### Create new migrations (after modifying models):
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Important Notes

1. **Never commit dbsetup.env** - It's in .gitignore to protect database credentials
2. **Always activate venv** before running Django commands
3. **Pull latest changes** before starting work: `git pull origin main`
4. **Run migrations** after pulling if there are new migration files

---

## Troubleshooting

### "No module named 'django'"
Make sure virtual environment is activated and dependencies are installed:
```bash
pip install -r requirements.txt
```

### "Cannot connect to database"
Check that:
1. You have the correct dbsetup.env file with valid credentials
2. The Neon PostgreSQL database is online
3. Your internet connection is working

### "Migrations not applied"
```bash
python manage.py migrate
```

---

## Project Structure
```
DBMS Project/
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── db.sqlite3            # Local SQLite (not used, for reference only)
├── config/               # Django project configuration
│   ├── settings.py       # Database config here
│   ├── urls.py
│   └── wsgi.py
├── lostandfound/         # Main Django app
│   ├── models.py         # Database models (User, Item, Claim, etc.)
│   ├── views.py          # View logic
│   ├── urls.py           # App URLs
│   ├── migrations/       # Database migrations (auto-generated)
│   └── templates/        # HTML templates
└── media/                # User-uploaded images
```

---

## Database Details
- **Engine**: PostgreSQL
- **Host**: Neon (managed PostgreSQL cloud service)
- **SSL Mode**: Required (`sslmode='require'`)
- **Models**: User (custom), Item, LostItem, FoundItem, Claim, Notification, Category

---

Questions? Ask the project owner.
