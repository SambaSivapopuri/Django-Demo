from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Student

staff_required = user_passes_test(lambda u: u.is_staff)


# ---------- Home / Hello World ----------
def home(request):
    return render(request, "core/home.html")


def hello(request):
    return HttpResponse("Hello World")


def hello_template(request):
    return render(request, "core/hello.html", {"message": "Hello World"})


# ---------- Student CRUD (staff only) ----------
@staff_required
def student_list(request):
    students = Student.objects.all()
    return render(request, "core/student_list.html", {"students": students})


@staff_required
def student_add(request):
    if request.method == "POST":
        Student.objects.create(
            name=request.POST["name"],
            email=request.POST["email"],
            age=request.POST["age"],
        )
        return redirect("student_list")
    return render(request, "core/student_form.html")


@staff_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.name = request.POST["name"]
        student.email = request.POST["email"]
        student.age = request.POST["age"]
        student.save()
        return redirect("student_list")
    return render(request, "core/student_form.html", {"student": student})


@staff_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.delete()
    return redirect("student_list")


# ---------- Auth ----------
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # is_staff / is_superuser are False by default
            login(request, user)
            return redirect("dashboard")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    user = request.user
    context = {}

    if user.is_superuser:
        template = "core/dashboard_admin.html"
        context["total_users"] = User.objects.count()
    elif user.is_staff:
        template = "core/dashboard_staff.html"
    else:
        template = "core/dashboard_user.html"

    return render(request, template, context)
