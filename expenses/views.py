from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ExpenseFilterForm, ExpenseForm
from .models import Expense


def home(request):
    if not request.user.is_authenticated:
        return render(request, "expenses/home.html")

    today = timezone.localdate()
    expenses = Expense.objects.filter(user=request.user)

    # 1. This month vs last month
    this_month = expenses.filter(date__year=today.year, date__month=today.month)
    month_total = this_month.aggregate(total=Sum("amount"))["total"] or 0
    month_count = this_month.count()

    last_month_day = today.replace(day=1) - timedelta(days=1)
    last_month_total = expenses.filter(
        date__year=last_month_day.year, date__month=last_month_day.month
    ).aggregate(total=Sum("amount"))["total"] or 0

    # 2. Spending by category (this month)
    by_category = list(
        this_month.values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )
    for row in by_category:
        row["percent"] = row["total"] * 100 / month_total

    # 3. Recent expenses
    recent = expenses.select_related("category")[:8]

    # 4. Monthly summary (last 6 months, including months with no spending)
    months = []
    year, month = today.year, today.month
    for _ in range(6):
        months.append(date(year, month, 1))
        month -= 1
        if month == 0:
            month, year = 12, year - 1

    totals = (
        expenses.filter(date__gte=months[-1], date__lte=today)
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("amount"), count=Count("id"))
        .order_by()
    )
    totals_by_month = {row["month"]: row for row in totals}

    monthly_summary = []
    for m in months:
        row = totals_by_month.get(m)
        monthly_summary.append({
            "month": m,
            "total": row["total"] if row else 0,
            "count": row["count"] if row else 0,
        })

    context = {
        "today": today,
        "last_month_day": last_month_day,
        "month_total": month_total,
        "month_count": month_count,
        "last_month_total": last_month_total,
        "by_category": by_category,
        "recent": recent,
        "monthly_summary": monthly_summary,
    }
    return render(request, "expenses/dashboard.html", context)


@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).select_related("category")

    filter_form = ExpenseFilterForm(request.GET or None)
    is_filtered = False

    if filter_form.is_valid():
        data = filter_form.cleaned_data

        if data["category"]:
            expenses = expenses.filter(category=data["category"])
        if data["date_from"]:
            expenses = expenses.filter(date__gte=data["date_from"])
        if data["date_to"]:
            expenses = expenses.filter(date__lte=data["date_to"])
        if data["min_amount"] is not None:
            expenses = expenses.filter(amount__gte=data["min_amount"])
        if data["max_amount"] is not None:
            expenses = expenses.filter(amount__lte=data["max_amount"])

        is_filtered = any(value is not None for value in data.values())

    total = expenses.aggregate(total=Sum("amount"))["total"] or 0

    context = {
        "expenses": expenses,
        "total": total,
        "filter_form": filter_form,
        "is_filtered": is_filtered,
    }
    return render(request, "expenses/expense_list.html", context)


@login_required
def expense_create(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, f'Expense "{expense.title}" was added.')
            return redirect("expense_list")
    else:
        form = ExpenseForm(initial={"date": timezone.localdate()})

    return render(request, "expenses/expense_form.html", {"form": form, "title": "Add expense"})


@login_required
def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)

    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, f'Expense "{expense.title}" was updated.')
            return redirect("expense_list")
    else:
        form = ExpenseForm(instance=expense)

    return render(request, "expenses/expense_form.html", {"form": form, "title": "Edit expense"})


@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)

    if request.method == "POST":
        title = expense.title
        expense.delete()
        messages.success(request, f'Expense "{title}" was deleted.')
        return redirect("expense_list")

    return render(request, "expenses/expense_confirm_delete.html", {"expense": expense})
