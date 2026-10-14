# Expense Tracker

A full-stack expense tracker built with Python and Django for EECE 439 (Cloud Computing), Assignment 3.
Users can register, log their expenses by category, filter their history, and see a dashboard of their spending.
It runs locally on SQLite.

## Features

- **User accounts:** register, log in and out, view and edit your profile (name, email, spending stats)
- **Expenses:** add, edit, delete, and view your expense history with a running total
- **Categories:** Food, Transport, Bills, Shopping, Entertainment, Other
- **Dashboard:** total spending this month, spending by category, recent expenses, and a 6-month summary
- **Filtering:** by category, date range, and amount range
- **Privacy:** each user only ever sees and edits their own expenses

## Tech stack

- Python 3.12 or newer, Django 6.1
- SQLite
- Bootstrap 5 (loaded from a CDN)

## Getting started

1. Clone the repository and move into the project folder.

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   ```

   Windows:

   ```bash
   venv\Scripts\activate
   ```

   macOS / Linux:

   ```bash
   source venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create the database. This also adds the six categories:

   ```bash
   python manage.py migrate
   ```

5. Start the server:

   ```bash
   python manage.py runserver
   ```

6. Open http://127.0.0.1:8000/ and register an account.

### Optional: demo data

To see the dashboard with plenty of data, register an account, then fill it with about six months of
realistic sample expenses:

```bash
python manage.py seed_demo <your-username>
```

To remove the sample expenses again (your own expenses are kept):

```bash
python manage.py seed_demo <your-username> --clear
```

### Optional: admin panel

```bash
python manage.py createsuperuser
```

Then log in at http://127.0.0.1:8000/admin/.

## Project structure

```
expense_tracker/   Project settings and root URLs
accounts/          Register, login/logout, profile
expenses/          Expense and Category models, CRUD, filtering, dashboard
  management/commands/seed_demo.py   Demo data command
  migrations/0002_seed_categories.py Creates the six categories
templates/         HTML templates (base layout, accounts, expenses)
```

## Pages

| URL | Page |
| --- | --- |
| `/` | Dashboard (welcome page when logged out) |
| `/expenses/` | Expense history with filters |
| `/expenses/add/` | Add an expense |
| `/expenses/<id>/edit/` | Edit an expense |
| `/expenses/<id>/delete/` | Delete an expense |
| `/accounts/register/` | Register |
| `/accounts/login/` | Log in |
| `/accounts/profile/` | Profile |
| `/accounts/profile/edit/` | Edit profile |
| `/admin/` | Django admin |
