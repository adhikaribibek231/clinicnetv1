from django import forms
from .models import Product, Sale, MedicineBatch

class AddForm(forms.Form):
    """Form for adding items to stock"""
    received_quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter quantity to add'
        }),
        label='Quantity to Add'
    )

    def clean_received_quantity(self):
        quantity = self.cleaned_data['received_quantity']
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than 0.")
        return quantity


class SaleForm(forms.ModelForm):
    """Form for processing sales"""
    class Meta:
        model = Sale
        fields = ["quantity", "amount_received", "issued_to"]
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter quantity'
            }),
            'amount_received': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter amount received'
            }),
            'issued_to': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter customer name'
            }),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than 0.")
        return quantity

    def clean_amount_received(self):
        amount = self.cleaned_data['amount_received']
        if amount < 0:
            raise forms.ValidationError("Amount received cannot be negative.")
        return amount

    def clean_issued_to(self):
        issued_to = self.cleaned_data['issued_to']
        if not issued_to or len(issued_to.strip()) == 0:
            raise forms.ValidationError("Customer name is required.")
        return issued_to.strip()


class ProductForm(forms.ModelForm):
    """Form for adding new medicines/products"""
    class Meta:
        model = Product
        fields = ["category_name", "item_name", "unit_price"]
        widgets = {
            'category_name': forms.Select(attrs={'class': 'form-control'}),
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter medicine name'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter unit price'}),
        }


class MedicineBatchForm(forms.ModelForm):
    """Form for adding a new batch of medicine"""
    class Meta:
        model = MedicineBatch
        fields = ["product", "batch_number", "manufacture_date", "expiry_date", "quantity"]
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Batch number (optional)'}),
            'manufacture_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter batch quantity'}),
        }