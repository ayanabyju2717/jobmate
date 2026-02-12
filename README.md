# JobMate – AI-Powered On-Demand Employee Service Platform

A Django-based marketplace where **Customers** can hire **Employees** for temporary tasks (hourly, daily, or monthly) with transparent pricing and AI-driven matching.

---

## Features

- **Role-Based Authentication** – Admin, Employee, and Customer roles with custom profiles
- **AI Matching Engine** – Ranks employees by skill overlap (50%), ratings (30%), and proximity (20%)
- **Smart Search (NLP)** – Tokenized search across skills, bios, locations, and names
- **Booking Workflow** – Create → Accept/Reject → Start → Complete → Review
- **Pricing Engine** – Automated cost calculation (Rate × Duration)
- **Progress Tracking** – Employees upload work proof (text + images)
- **Admin Dashboard** – Analytics, employee verification, revenue tracking, fraud detection
- **Signal-Based Notifications** – Email alerts on booking/review status changes

---

## Tech Stack

| Layer       | Technology                     |
|-------------|--------------------------------|
| Backend     | Django 6.0 (Python 3.13)       |
| Frontend    | Bootstrap 5.3 + Bootstrap Icons |
| Database    | PostgreSQL 12+                 |
| Auth        | Django custom `AbstractUser`   |

---

## Prerequisites

- **Python 3.10+** installed
- **pip** (comes with Python)
- **PostgreSQL 12+** installed and running
- **Git** (optional, for cloning)

---

## Setup & Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd job-mate
```

### 2. Create PostgreSQL Database

Open PostgreSQL command line (psql) or use pgAdmin:

```sql
CREATE DATABASE jobmate_db;
CREATE USER jobmate_user WITH PASSWORD 'your_secure_password';
ALTER ROLE jobmate_user SET client_encoding TO 'utf8';
ALTER ROLE jobmate_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE jobmate_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE jobmate_db TO jobmate_user;
```

### 3. Create a Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install django Pillow psycopg2-binary python-decouple
```

### 5. Configure Environment Variables

Copy the example environment file and update it with your database credentials:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Edit `.env` and update the database settings:

```env
DB_NAME=jobmate_db
DB_USER=jobmate_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

### 6. Run Migrations

```bash
python manage.py makemigrations accounts bookings dashboard
python manage.py migrate
```

### 7. Create a Superuser (Admin)

```bash
python manage.py createsuperuser
```

When prompted, set the username, email, and password. Then update the role to admin:

```bash
python manage.py shell -c "
from accounts.models import User
u = User.objects.get(username='admin')
u.role = 'admin'
u.save()
print('Admin role set.')
"
```

### 8. (Optional) Seed Demo Data

```bash
python manage.py shell -c "
from accounts.models import Skill
skills = [
    ('Plumbing', 'Trades'), ('Electrical', 'Trades'), ('Carpentry', 'Trades'),
    ('Painting', 'Trades'), ('Cleaning', 'Home'), ('Landscaping', 'Home'),
    ('Moving', 'Home'), ('Web Development', 'Tech'), ('Graphic Design', 'Tech'),
    ('Data Entry', 'Office'), ('Photography', 'Creative'), ('Cooking', 'Home'),
]
for name, cat in skills:
    Skill.objects.get_or_create(name=name, defaults={'category': cat})
print(f'{Skill.objects.count()} skills created')
"
```

### 9. Start the Development Server

```bash
python manage.py runserver
```

Open your browser at **http://127.0.0.1:8000**

---

## Demo Accounts

If you ran the seed script during initial setup:

| Username    | Password   | Role     |
|-------------|------------|----------|
| `admin`     | `admin123` | Admin    |
| `customer1` | `test1234` | Customer |
| `emp1`      | `test1234` | Employee |
| `emp2`      | `test1234` | Employee |
| `emp3`      | `test1234` | Employee |
| `emp4`      | `test1234` | Employee |

---

## Project Structure

```
job-mate/
├── manage.py                 # Django management script
├── db.sqlite3                # SQLite database
├── jobmate/                  # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                 # User auth, profiles, skills
│   ├── models.py             # User, EmployeeProfile, CustomerProfile, Skill
│   ├── views.py              # Signup, login, profile views
│   ├── forms.py              # Registration & profile forms
│   ├── urls.py
│   └── admin.py
├── bookings/                 # Core booking system
│   ├── models.py             # Booking, Review, WorkProof
│   ├── views.py              # Booking CRUD, reviews, work proof
│   ├── forms.py              # Booking, review, search forms
│   ├── services.py           # AI Matching Engine + Pricing + NLP Search
│   ├── signals.py            # Notification signals
│   ├── urls.py
│   └── admin.py
├── dashboard/                # Admin analytics
│   ├── views.py              # Admin dashboard + employee verification
│   └── urls.py
├── templates/                # HTML templates (Bootstrap 5)
│   ├── base.html
│   ├── accounts/
│   ├── bookings/
│   └── dashboard/
├── static/                   # Static assets
└── media/                    # Uploaded files (profiles, work proofs)
```

---

## Key URLs

| URL                              | Description                     |
|----------------------------------|---------------------------------|
| `/`                              | Home page with search & workers |
| `/employees/`                    | Browse/search all employees     |
| `/accounts/signup/`              | Register a new account          |
| `/accounts/login/`               | Login                           |
| `/accounts/profile/`             | View your profile               |
| `/accounts/employee/<id>/`       | Public employee profile         |
| `/book/<employee_id>/`           | Create a booking                |
| `/bookings/`                     | List your bookings              |
| `/bookings/<id>/`                | Booking detail                  |
| `/bookings/<id>/<action>/`       | Accept/reject/start/complete    |
| `/bookings/<id>/review/`         | Leave a review                  |
| `/bookings/<id>/proof/`          | Upload work proof               |
| `/dashboard/`                    | Admin dashboard                 |
| `/admin/`                        | Django admin panel               |

---

## AI Matching Engine

Located in `bookings/services.py`, the `rank_employees()` function calculates a match score:

```
Match Score = (Skill Overlap × 0.50) + (Rating × 0.30) + (Proximity × 0.20)
```

- **Skill Score** – Jaccard similarity between required and employee skill sets
- **Rating Score** – Normalized 0–5 star rating
- **Proximity Score** – Haversine distance (1 = same spot, 0 = 50+ km away)

> To plug in a real ML model, replace the weighted-sum logic in `rank_employees()` with your trained model's prediction.

---

## License

This project is for educational/demonstration purposes.
