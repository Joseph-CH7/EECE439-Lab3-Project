from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import render, redirect

from .forms import ProfileForm, RegisterForm


def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account was created.")
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    expenses = request.user.expenses.all()

    total_spent = expenses.aggregate(total=Sum("amount"))["total"] or 0

    top_category = (
        expenses.values("category__name")
        .annotate(count=Count("id"))
        .order_by("-count")
        .first()
    )

    context = {
        "expense_count": expenses.count(),
        "total_spent": total_spent,
        "top_category": top_category["category__name"] if top_category else None,
    }
    return render(request, "accounts/profile.html", context)


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile was updated.")
            return redirect("profile")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "accounts/edit_profile.html", {"form": form})