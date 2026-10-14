from django import forms

from .models import Category, Expense


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["title", "amount", "category", "date", "description"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "category":
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"
        self.fields["amount"].widget.attrs["min"] = "0.01"
        self.fields["amount"].widget.attrs["step"] = "0.01"

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than 0.")
        return amount


class ExpenseFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All categories",
    )
    date_from = forms.DateField(
        required=False,
        label="From",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    date_to = forms.DateField(
        required=False,
        label="To",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    min_amount = forms.DecimalField(required=False, min_value=0, decimal_places=2, label="Min amount")
    max_amount = forms.DecimalField(required=False, min_value=0, decimal_places=2, label="Max amount")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "category":
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"
        self.fields["min_amount"].widget.attrs["step"] = "0.01"
        self.fields["max_amount"].widget.attrs["step"] = "0.01"

    def clean(self):
        cleaned_data = super().clean()

        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError('"From" date must be before "To" date.')

        min_amount = cleaned_data.get("min_amount")
        max_amount = cleaned_data.get("max_amount")
        if min_amount is not None and max_amount is not None and min_amount > max_amount:
            raise forms.ValidationError("Min amount must be less than max amount.")

        return cleaned_data
