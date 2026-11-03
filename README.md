# Django Teaching Guide (Step by Step)

A beginner-friendly guide. Commands are for **Windows (PowerShell)**; Mac/Linux differences are noted.

Throughout this guide we use:

- Project name: `mysite`
- App name: `core`

## Table of Contents

1. [Virtual Environment (venv)](#1-virtual-environment-venv)
2. [Install Django, Create Project and App](#2-install-django-create-project-and-app)
3. [Templates Setup](#3-templates-setup)
4. [Views: Hello World](#4-views-hello-world)
5. [URL Routing](#5-url-routing)
6. [Change the Database](#6-change-the-database-sqlite--mysql--postgresql)
7. [Models, makemigrations and migrate](#7-models-makemigrations-and-migrate)
8. [Insert, Edit, Delete Data (ORM)](#8-insert-edit-delete-data-orm)
9. [User Registration and Roles](#9-user-registration-and-roles-admin--staff--normal-user)
10. [Login and Logout](#10-login-and-logout)
11. [Role-based Dashboards](#11-role-based-dashboards)
12. [Quick Command Cheat Sheet](#12-quick-command-cheat-sheet)

---

## 1. Virtual Environment (venv)

### What is it?
A virtual environment is a **private, isolated Python folder for one project**. Packages you install go inside it, not into your whole computer.

### Why do we need it?
| Problem without venv | How venv solves it |
|---|---|
| Project A needs Django 4.2, Project B needs Django 5.0 - they clash | Each project has its own Django version |
| Installing everything globally makes your system messy | Everything stays inside the project folder |
| Hard to share the project with others | `pip freeze > requirements.txt` lists exactly what is needed |
| Deleting a project leaves junk packages behind | Delete the `venv` folder, everything is gone |

### Create it
```powershell
python -m venv venv
```
This creates a folder named `venv` (you can name it anything).

### Activate it
```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat

# Mac / Linux
source venv/bin/activate
```
When active, your prompt shows `(venv)` at the start.

> **PowerShell error "running scripts is disabled"?** Run this once:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

### Deactivate it
```powershell
deactivate
```

### Save and restore packages
```powershell
pip freeze > requirements.txt      # save
pip install -r requirements.txt    # restore on another computer
```

> Add `venv/` to `.gitignore`. Never upload the venv folder to Git.

---

## 2. Install Django, Create Project and App

### Install Django (venv must be active)
```powershell
pip install django
python -m django --version
```

### Create a project
```powershell
django-admin startproject mysite .
```
The `.` at the end creates the project in the current folder (no extra nesting).

Structure:
```
Django-Demo/
├── manage.py          <- command-line tool for the project
└── mysite/
    ├── settings.py    <- all project configuration
    ├── urls.py        <- main URL routes
    ├── asgi.py / wsgi.py
    └── __init__.py
```

Run the server to test:
```powershell
python manage.py runserver
```
Open http://127.0.0.1:8000/ - you will see the Django rocket page.

### Create an app
A **project** is the whole website. An **app** is one feature/module of it (users, blog, shop...). One project can have many apps.

```powershell
python manage.py startapp core
```

Structure:
```
core/
├── admin.py      <- register models in admin panel
├── apps.py       <- app config
├── models.py     <- database tables
├── views.py      <- logic (what to show)
├── tests.py
└── migrations/   <- database change history
```

### Integrate (register) the app in the project
Open `mysite/settings.py` and add the app to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'core',            # <- our app
]
```
Without this, Django ignores the app (its models, templates, etc. will not work).

---

## 3. Templates Setup

Templates are the HTML files shown to the user. There are **two ways** to organize them. Both can be used together.

### Way A: App-level templates folder (default, app-specific)
Django automatically looks inside each app's `templates` folder (because of `APP_DIRS: True`).

Create this structure:
```
core/
└── templates/
    └── core/
        └── hello.html
```
> The extra inner `core/` folder is a **namespace**. It prevents two apps having `index.html` from clashing. In views you refer to it as `'core/hello.html'`.

### Way B: Project-level templates folder (shared, e.g. base layout)
Create a `templates` folder next to `manage.py`:
```
Django-Demo/
├── manage.py
├── templates/
│   └── base.html
├── mysite/
└── core/
```

Tell Django about it in `mysite/settings.py`:
```python
import os   # not needed if you use Path (default in new Django)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],     # <- project-level folder
        'APP_DIRS': True,                     # <- app-level templates folders
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

| Setting | Meaning |
|---|---|
| `DIRS` | Extra folders you list manually (project-wide templates) |
| `APP_DIRS: True` | Also search `templates/` inside every installed app |

### Base template (reuse layout)
`templates/base.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{% block title %}My Site{% endblock %}</title>
</head>
<body>
    <nav>
        <a href="/">Home</a>
        {% if user.is_authenticated %}
            <a href="{% url 'dashboard' %}">Dashboard</a>
            <form method="post" action="{% url 'logout' %}" style="display:inline">
                {% csrf_token %}
                <button type="submit">Logout ({{ user.username }})</button>
            </form>
        {% else %}
            <a href="{% url 'login' %}">Login</a>
            <a href="{% url 'register' %}">Register</a>
        {% endif %}
    </nav>
    <hr>
    {% block content %}{% endblock %}
</body>
</html>
```

A child page extends it:
```html
{% extends "base.html" %}
{% block title %}Hello{% endblock %}
{% block content %}
    <h1>Hello World</h1>
{% endblock %}
```

---

## 4. Views: Hello World

A **view** is a Python function that receives a request and returns a response.

`core/views.py`:
```python
from django.http import HttpResponse
from django.shortcuts import render


# 1) Simple view with HttpResponse (plain text/HTML string)
def hello(request):
    return HttpResponse("Hello World")


# 2) View with a template
def hello_template(request):
    context = {"message": "Hello World"}
    return render(request, "core/hello.html", context)
```

`core/templates/core/hello.html`:
```html
<!DOCTYPE html>
<html>
<head><title>Hello</title></head>
<body>
    <h1>{{ message }}</h1>
</body>
</html>
```
`{{ message }}` prints the value sent from the view's `context`.

| | `HttpResponse` | `render` |
|---|---|---|
| Returns | A string you write in Python | An HTML template filled with data |
| Use for | Tiny tests, plain text, APIs | Real web pages |

---

## 5. URL Routing

Flow of a request:

```
Browser -> mysite/urls.py (project) -> core/urls.py (app) -> core/views.py -> Template -> Response
```

### Step 1: Create the app's `core/urls.py` (the file does not exist by default)
```python
from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello, name='hello'),
    path('hello-template/', views.hello_template, name='hello_template'),
]
```

### Step 2: Connect the app URLs to the project: `mysite/urls.py`
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),      # <- connect app routes
]
```

### Test
```powershell
python manage.py runserver
```
- http://127.0.0.1:8000/hello/ -> plain "Hello World"
- http://127.0.0.1:8000/hello-template/ -> "Hello World" from the template

> `name='hello'` lets you build links without hard-coding: `{% url 'hello' %}` in templates, or `reverse('hello')` / `redirect('hello')` in Python.

---

## 6. Change the Database (SQLite / MySQL / PostgreSQL)

All database config lives in `DATABASES` in `mysite/settings.py`. Django's ORM means **your models and views do not change**, only these settings.

### SQLite (default - no install needed, good for learning)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### MySQL
1. Install MySQL server and create a database:
   ```sql
   CREATE DATABASE mydb CHARACTER SET utf8mb4;
   ```
2. Install the Python driver:
   ```powershell
   pip install mysqlclient
   ```
   (If it fails to build on Windows, use `pip install pymysql` and add
   `import pymysql; pymysql.install_as_MySQLdb()` at the top of `mysite/__init__.py`.)
3. Settings:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'mydb',
           'USER': 'root',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```

### PostgreSQL
1. Install PostgreSQL and create a database:
   ```sql
   CREATE DATABASE mydb;
   ```
2. Install the driver:
   ```powershell
   pip install psycopg2-binary
   ```
3. Settings:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'mydb',
           'USER': 'postgres',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

### After changing the database
The new database is empty, so create the tables again:
```powershell
python manage.py migrate
```
Data in the old database is **not** copied automatically.

> **Security tip:** do not commit real passwords to Git. Use environment variables (`os.environ.get('DB_PASSWORD')`) or a `.env` file.

---

## 7. Models, makemigrations and migrate

### What is a model?
A model is a **Python class that represents a database table**. Each attribute is a column. You never write SQL by hand.

`core/models.py`:
```python
from django.db import models


class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    age = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
```
Django automatically adds an `id` primary key.

### makemigrations and migrate: what and why

| Command | What it does | Think of it as |
|---|---|---|
| `python manage.py makemigrations` | Looks at your models and **writes a migration file** (a plan of changes) in `core/migrations/` | "Prepare the blueprint" |
| `python manage.py migrate` | **Runs** the migration files on the database (creates/alters tables) | "Build it in the database" |

```powershell
python manage.py makemigrations
python manage.py migrate
```

**Why is this useful?**
- No manual SQL: change Python, Django changes the database.
- **Version history** of your database structure, stored in Git so the whole team stays in sync.
- Works on any database (SQLite, MySQL, PostgreSQL) with the same code.
- Safe changes: add/rename/remove columns later without losing data.
- Reversible: `python manage.py migrate core 0001` rolls back to an earlier state.

**Remember:** every time you change `models.py` -> run `makemigrations` then `migrate`.

Useful extras:
```powershell
python manage.py showmigrations      # see which migrations are applied
python manage.py sqlmigrate core 0001  # see the SQL Django will run
```

### Register in admin (optional but handy)
`core/admin.py`:
```python
from django.contrib import admin
from .models import Student

admin.site.register(Student)
```

---

## 8. Insert, Edit, Delete Data (ORM)

ORM = Object Relational Mapper. You use Python objects instead of SQL.

### Try in the Django shell
```powershell
python manage.py shell
```

```python
from core.models import Student

# ---------- CREATE (insert) ----------
s = Student(name="Ravi", email="ravi@example.com", age=20)
s.save()

# shortcut
Student.objects.create(name="Sita", email="sita@example.com", age=22)

# ---------- READ ----------
Student.objects.all()                       # all rows
Student.objects.get(id=1)                   # exactly one row (error if none/many)
Student.objects.filter(age__gte=21)         # conditions
Student.objects.filter(name__icontains="ra")
Student.objects.order_by('-age')            # sort (descending)
Student.objects.count()

# ---------- UPDATE (edit) ----------
s = Student.objects.get(id=1)
s.age = 21
s.save()

# update many at once
Student.objects.filter(age__lt=18).update(age=18)

# ---------- DELETE ----------
s = Student.objects.get(id=1)
s.delete()

Student.objects.filter(age__lt=18).delete()  # delete many
```

### Using it in views (full CRUD example)

`core/views.py`:
```python
from django.shortcuts import render, redirect, get_object_or_404
from .models import Student


def student_list(request):
    students = Student.objects.all()
    return render(request, "core/student_list.html", {"students": students})


def student_add(request):
    if request.method == "POST":
        Student.objects.create(
            name=request.POST["name"],
            email=request.POST["email"],
            age=request.POST["age"],
        )
        return redirect("student_list")
    return render(request, "core/student_form.html")


def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.name = request.POST["name"]
        student.email = request.POST["email"]
        student.age = request.POST["age"]
        student.save()
        return redirect("student_list")
    return render(request, "core/student_form.html", {"student": student})


def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.delete()
    return redirect("student_list")
```

`core/urls.py` (add):
```python
path('students/', views.student_list, name='student_list'),
path('students/add/', views.student_add, name='student_add'),
path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
```

`core/templates/core/student_list.html`:
```html
{% extends "base.html" %}
{% block content %}
<h2>Students</h2>
<a href="{% url 'student_add' %}">+ Add Student</a>
<table border="1" cellpadding="6">
    <tr><th>Name</th><th>Email</th><th>Age</th><th>Actions</th></tr>
    {% for s in students %}
    <tr>
        <td>{{ s.name }}</td>
        <td>{{ s.email }}</td>
        <td>{{ s.age }}</td>
        <td>
            <a href="{% url 'student_edit' s.pk %}">Edit</a>
            <form method="post" action="{% url 'student_delete' s.pk %}" style="display:inline">
                {% csrf_token %}
                <button type="submit">Delete</button>
            </form>
        </td>
    </tr>
    {% empty %}
    <tr><td colspan="4">No students yet.</td></tr>
    {% endfor %}
</table>
{% endblock %}
```

`core/templates/core/student_form.html`:
```html
{% extends "base.html" %}
{% block content %}
<h2>{% if student %}Edit{% else %}Add{% endif %} Student</h2>
<form method="post">
    {% csrf_token %}
    <p>Name:  <input name="name"  value="{{ student.name }}" required></p>
    <p>Email: <input name="email" type="email" value="{{ student.email }}" required></p>
    <p>Age:   <input name="age"   type="number" value="{{ student.age }}" required></p>
    <button type="submit">Save</button>
</form>
{% endblock %}
```

> `{% csrf_token %}` is **required** in every POST form, otherwise Django rejects the request (403).

---

## 9. User Registration and Roles (Admin / Staff / Normal User)

Django already has a built-in `User` model with auth. Roles are decided by two flags:

| Role | `is_staff` | `is_superuser` | Can do |
|---|---|---|---|
| **Admin** (superuser) | True | True | Everything, including the admin panel and all permissions |
| **Staff** | True | False | Log in to admin panel, only with permissions given to them |
| **Normal user** | False | False | Use the website only |

### Creating each type

**Admin:**
```powershell
python manage.py createsuperuser
```

**Normal user:** through the registration page (below).

**Staff:** log in to http://127.0.0.1:8000/admin/ as admin -> Users -> select the user -> tick **Staff status** -> (optionally give permissions) -> Save.
Or in the shell:
```python
from django.contrib.auth.models import User
User.objects.create_user("teacher1", password="Pass@1234", is_staff=True)
```

> **Security note:** The public registration page should create **normal users only**. Never let visitors choose "admin" or "staff" themselves, or anyone could make themselves an admin. Admin/staff are created by an existing admin.

### Registration page

`core/forms.py` (new file):
```python
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
```

`core/views.py` (add):
```python
from django.contrib.auth import login
from .forms import RegisterForm


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()          # is_staff / is_superuser are False by default
            login(request, user)        # log them in right after registering
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})
```

`templates/registration/register.html`:
```html
{% extends "base.html" %}
{% block content %}
<h2>Register</h2>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Create Account</button>
</form>
<p>Already have an account? <a href="{% url 'login' %}">Login</a></p>
{% endblock %}
```

---

## 10. Login and Logout

Django has built-in `LoginView` and `LogoutView`, so you do not write the logic yourself.

### Settings: `mysite/settings.py` (add at the bottom)
```python
LOGIN_URL = 'login'                 # where @login_required sends anonymous users
LOGIN_REDIRECT_URL = 'dashboard'    # after successful login
LOGOUT_REDIRECT_URL = 'login'       # after logout
```

### URLs: `core/urls.py`
```python
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ... earlier routes ...
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
```
`LoginView` looks for the template `registration/login.html` by default.

### Login template: `templates/registration/login.html`
```html
{% extends "base.html" %}
{% block content %}
<h2>Login</h2>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Login</button>
</form>
<p>New here? <a href="{% url 'register' %}">Register</a></p>
{% endblock %}
```

### Logout
Logout must be a **POST** request (Django 5+). That is why `base.html` uses a small form with a button instead of a plain link:
```html
<form method="post" action="{% url 'logout' %}">
    {% csrf_token %}
    <button type="submit">Logout</button>
</form>
```

---

## 11. Role-based Dashboards

After login, each user should see **their own** dashboard depending on role.

### Single dashboard view that picks the template by role

`core/views.py` (add):
```python
from django.contrib.auth.decorators import login_required


@login_required                      # anonymous users are redirected to the login page
def dashboard(request):
    user = request.user

    if user.is_superuser:
        template = "core/dashboard_admin.html"
    elif user.is_staff:
        template = "core/dashboard_staff.html"
    else:
        template = "core/dashboard_user.html"

    context = {
        "total_users": None,
    }
    if user.is_superuser:
        from django.contrib.auth.models import User
        context["total_users"] = User.objects.count()

    return render(request, template, context)
```

### Templates

`core/templates/core/dashboard_admin.html`
```html
{% extends "base.html" %}
{% block content %}
<h1>Admin Dashboard</h1>
<p>Welcome, {{ user.username }}.</p>
<p>Total users: {{ total_users }}</p>
<a href="/admin/">Open Django Admin Panel</a>
{% endblock %}
```

`core/templates/core/dashboard_staff.html`
```html
{% extends "base.html" %}
{% block content %}
<h1>Staff Dashboard</h1>
<p>Welcome, {{ user.username }}. You can manage students here.</p>
<a href="{% url 'student_list' %}">Manage Students</a>
{% endblock %}
```

`core/templates/core/dashboard_user.html`
```html
{% extends "base.html" %}
{% block content %}
<h1>My Dashboard</h1>
<p>Welcome, {{ user.username }}.</p>
<p>Email: {{ user.email }}</p>
<p>Joined: {{ user.date_joined|date:"d M Y" }}</p>
{% endblock %}
```

### Protecting pages by role
Use decorators so users cannot open pages by typing the URL:

```python
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
def my_profile(request): ...                       # any logged-in user

@user_passes_test(lambda u: u.is_staff)
def staff_only(request): ...                       # staff and admin

@user_passes_test(lambda u: u.is_superuser)
def admin_only(request): ...                       # admin only
```

Protect the student CRUD views from section 8 the same way, for example add `@user_passes_test(lambda u: u.is_staff)` above `student_add`, `student_edit`, `student_delete`.

In templates you can also show/hide parts:
```html
{% if user.is_superuser %} ... {% elif user.is_staff %} ... {% else %} ... {% endif %}
```

### Full test flow
1. `python manage.py migrate`
2. `python manage.py createsuperuser` -> log in at `/login/` -> see **Admin dashboard**
3. In `/admin/` create a user and tick **Staff status** -> log in -> see **Staff dashboard**
4. Open `/register/`, create a normal account -> see **User dashboard**
5. Click **Logout** -> redirected to login page
6. Open `/dashboard/` while logged out -> redirected to `/login/?next=/dashboard/`

---

## 12. Quick Command Cheat Sheet

```powershell
python -m venv venv                         # create venv
.\venv\Scripts\Activate.ps1                 # activate (Windows)
pip install django                          # install Django
django-admin startproject mysite .          # new project
python manage.py startapp core              # new app
python manage.py runserver                  # start server
python manage.py makemigrations             # create migration files
python manage.py migrate                    # apply to database
python manage.py createsuperuser            # create admin
python manage.py shell                      # Python shell with Django loaded
pip freeze > requirements.txt               # save packages
```

### Common errors
| Error | Fix |
|---|---|
| `TemplateDoesNotExist` | Check folder path `app/templates/app/file.html`, app is in `INSTALLED_APPS`, and `DIRS` / `APP_DIRS` are set |
| `No module named 'django'` | Activate the venv |
| `no such table` | Run `makemigrations` then `migrate` |
| `CSRF verification failed` | Add `{% csrf_token %}` inside the POST form |
| `NoReverseMatch` | The `name=` in `urls.py` does not match what you used in `{% url %}` |
| `Page not found (404)` | URL not added to `core/urls.py`, or app urls not included in `mysite/urls.py` |
| Logout gives 405 | Logout needs a POST form (see section 10) |

Happy coding!
