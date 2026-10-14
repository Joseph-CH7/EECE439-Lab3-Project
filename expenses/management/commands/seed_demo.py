import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from expenses.models import Category, Expense

# Every demo expense gets this description, so --clear can find and remove them.
DEMO_NOTE = "Demo data"

# Expenses that happen once every month: (category, title, day of month, min amount, max amount)
MONTHLY = [
    ("Bills", "Rent", 1, 650, 650),
    ("Bills", "Electricity", 5, 40, 90),
    ("Bills", "Internet", 8, 35, 35),
    ("Bills", "Phone plan", 12, 25, 25),
    ("Entertainment", "Netflix", 15, 15.99, 15.99),
]

# Random expenses: category -> (min per month, max per month, [(title, min amount, max amount), ...])
RANDOM = {
    "Food": (12, 20, [("Groceries", 25, 90), ("Lunch", 8, 18), ("Coffee", 3, 6),
                      ("Dinner out", 25, 60), ("Bakery", 4, 12)]),
    "Transport": (6, 10, [("Taxi", 6, 20), ("Bus ticket", 1, 3), ("Fuel", 30, 60), ("Uber", 8, 25)]),
    "Shopping": (2, 4, [("Clothes", 30, 120), ("Household items", 10, 45), ("Books", 12, 35),
                        ("Electronics", 40, 250)]),
    "Entertainment": (2, 4, [("Cinema", 8, 15), ("Concert", 40, 90), ("Video game", 20, 70),
                             ("Bowling", 10, 25)]),
    "Other": (1, 2, [("Gift", 20, 80), ("Haircut", 15, 25), ("Pharmacy", 8, 40), ("Donation", 10, 50)]),
}


class Command(BaseCommand):
    help = "Add realistic demo expenses to a user's account (or remove them with --clear)."

    def add_arguments(self, parser):
        parser.add_argument("username", help="The user who will own the demo expenses")
        parser.add_argument("--months", type=int, default=6, help="How many months back to generate (default 6)")
        parser.add_argument("--clear", action="store_true", help="Remove this user's demo expenses instead")

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username=options["username"])
        except User.DoesNotExist:
            raise CommandError(f'User "{options["username"]}" does not exist.')

        demo_expenses = Expense.objects.filter(user=user, description=DEMO_NOTE)

        if options["clear"]:
            deleted, _ = demo_expenses.delete()
            self.stdout.write(self.style.SUCCESS(f"Removed {deleted} demo expenses from {user.username}."))
            return

        if demo_expenses.exists():
            raise CommandError(f"{user.username} already has demo data. Run with --clear first.")

        categories = {c.name: c for c in Category.objects.all()}
        rng = random.Random(42)  # fixed seed: the same data every time
        today = timezone.localdate()

        # First day of each month, oldest first
        months = []
        year, month = today.year, today.month
        for _ in range(options["months"]):
            months.insert(0, date(year, month, 1))
            month -= 1
            if month == 0:
                month, year = 12, year - 1

        new_expenses = []

        def add(category, title, day, low, high):
            amount = Decimal(str(round(rng.uniform(low, high), 2)))
            new_expenses.append(Expense(
                user=user, category=categories[category], title=title,
                amount=amount, date=day, description=DEMO_NOTE,
            ))

        for start in months:
            next_month = date(start.year + start.month // 12, start.month % 12 + 1, 1)
            days_in_month = (next_month - timedelta(days=1)).day
            last_day = min(days_in_month, today.day) if start.month == today.month and start.year == today.year else days_in_month

            for category, title, day, low, high in MONTHLY:
                if day <= last_day:
                    add(category, title, start.replace(day=day), low, high)

            for category, (min_count, max_count, options_list) in RANDOM.items():
                count = rng.randint(min_count, max_count)
                count = max(1, round(count * last_day / days_in_month))  # fewer for the current, unfinished month
                for _ in range(count):
                    title, low, high = rng.choice(options_list)
                    add(category, title, start.replace(day=rng.randint(1, last_day)), low, high)

        Expense.objects.bulk_create(new_expenses)
        self.stdout.write(self.style.SUCCESS(
            f"Added {len(new_expenses)} demo expenses to {user.username} "
            f"({months[0]:%b %Y} – {months[-1]:%b %Y})."
        ))
