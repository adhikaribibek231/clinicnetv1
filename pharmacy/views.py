from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.db import transaction
from .models import Product, Sale, Category, MedicineBatch
from .forms import AddForm, SaleForm, ProductForm, MedicineBatchForm
from clinic.models import Patient  # Import Patient for customer selection
from datetime import date, timedelta
# Create your views here.

@login_required
def Pharmacy(request):
    """Main inventory view"""
    products = Product.objects.all().order_by('-id')
    # Find batches expiring within 30 days
    today = date.today()
    soon = today + timedelta(days=30)
    expiring_batches = MedicineBatch.objects.filter(expiry_date__lte=soon, expiry_date__gte=today, quantity__gt=0).order_by('expiry_date')
    # Annotate each batch with total_value
    for product in products:
        for batch in product.batches.all():
            batch.total_value = str((batch.quantity or 0) * (product.unit_price or 0))
    return render(request, 'products/index.html', {'products': products, 'expiring_batches': expiring_batches})

@login_required
def home(request):
    """Home dashboard view"""
    from datetime import date, timedelta
    today = date.today()
    soon = today + timedelta(days=30)
    expiring_batches = MedicineBatch.objects.filter(expiry_date__lte=soon, expiry_date__gte=today, quantity__gt=0).order_by('expiry_date')
    total_products = Product.objects.count()
    total_sales = Sale.objects.count()
    # Calculate total inventory value
    total_value = sum(product.get_total_value() for product in Product.objects.all())
    context = {
        'expiring_batches': expiring_batches,
        'total_products': total_products,
        'total_sales': total_sales,
        'total_value': total_value,
    }
    return render(request, 'products/home.html', context)

@login_required
def receipt(request): 
    """View all sales receipts"""
    sales = Sale.objects.all().order_by('-date_created')
    return render(request, 'products/receipt.html', {'sales': sales})

@login_required
def receipt_print(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    batch = MedicineBatch.objects.filter(product=sale.item).order_by('expiry_date').first()
    return render(request, 'products/receipt_print.html', {
        'sale': sale,
        'batch': batch,
    })

@login_required
def product_detail(request, product_id):
    """View individual product details"""
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'products/product_detail.html', {'product': product})

@login_required
def all_sales(request):
    """View comprehensive sales report"""
    sales = Sale.objects.all().order_by('-date_created')
    total = sum([items.amount_received for items in sales])
    change = sum([items.get_change() for items in sales])
    net = total - change
    return render(request, 'products/all_sales.html', {
        'sales': sales, 
        'total': total,
        'change': change, 
        'net': net,
    })

@login_required
def add_to_stock(request, pk):
    """Add items to stock"""
    issued_item = get_object_or_404(Product, id=pk)
    
    if request.method == 'POST':
        form = AddForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    added_quantity = form.cleaned_data['received_quantity']
                    
                    # Update stock quantities
                    issued_item.total_quantity += added_quantity
                    issued_item.received_quantity += added_quantity
                    issued_item.save()
                    
                    messages.success(request, f'Successfully added {added_quantity} items to {issued_item.item_name} stock.')
                    return redirect('pharmacy:index')
                    
            except Exception as e:
                messages.error(request, f'Error updating stock: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddForm()

    return render(request, 'products/add_to_stock.html', {
        'form': form,
        'product': issued_item,
    })

@login_required
def add_medicine(request):
    """Add a new medicine/product to the inventory"""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'New medicine added successfully!')
            return redirect('pharmacy:index')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()
    return render(request, 'products/add_medicine.html', {'form': form})

@login_required
def add_medicine_batch(request):
    """Add a new batch of medicine to the inventory"""
    if request.method == 'POST':
        form = MedicineBatchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'New medicine batch added successfully!')
            return redirect('pharmacy:index')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MedicineBatchForm()
    return render(request, 'products/add_medicine_batch.html', {'form': form})

@login_required
def sell_medicine(request):
    """Sell medicine from a batch, select patient or enter customer name, and generate receipt"""
    batches = MedicineBatch.objects.select_related('product').filter(quantity__gt=0).order_by('product__item_name', 'expiry_date')
    patients = Patient.objects.all().order_by('name')
    if request.method == 'POST':
        batch_id = request.POST.get('batch')
        quantity = int(request.POST.get('quantity', 0))
        is_patient = request.POST.get('is_patient') == 'on'
        patient_id = request.POST.get('patient')
        customer_name = request.POST.get('customer_name')
        batch = MedicineBatch.objects.get(id=batch_id)
        if is_patient and patient_id:
            patient = Patient.objects.get(id=patient_id)
            issued_to = patient.name
        else:
            issued_to = customer_name
        if quantity <= 0 or quantity > batch.quantity:
            messages.error(request, f'Invalid quantity. Only {batch.quantity} available.')
        else:
            # Create sale
            sale = Sale.objects.create(
                item=batch.product,
                quantity=quantity,
                amount_received=quantity * batch.product.unit_price,
                issued_to=issued_to,
                unit_price=batch.product.unit_price
            )
            # Update batch
            batch.quantity -= quantity
            batch.save()
            return redirect('pharmacy:receipt_print', sale_id=sale.id)
    return render(request, 'products/sell_medicine.html', {
        'batches': batches,
        'patients': patients,
    })

@login_required
def edit_medicine(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine updated successfully!')
            return redirect('pharmacy:index')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/add_medicine.html', {'form': form, 'edit': True, 'product': product})

@login_required
def delete_medicine(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Medicine deleted successfully!')
        return redirect('pharmacy:index')
    return render(request, 'products/confirm_delete.html', {'object': product, 'type': 'medicine'})

@login_required
def edit_batch(request, batch_id):
    batch = get_object_or_404(MedicineBatch, id=batch_id)
    if request.method == 'POST':
        form = MedicineBatchForm(request.POST, instance=batch)
        if form.is_valid():
            form.save()
            messages.success(request, 'Batch updated successfully!')
            return redirect('pharmacy:index')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MedicineBatchForm(instance=batch)
    return render(request, 'products/add_medicine_batch.html', {'form': form, 'edit': True, 'batch': batch})

@login_required
def delete_batch(request, batch_id):
    batch = get_object_or_404(MedicineBatch, id=batch_id)
    if request.method == 'POST':
        batch.delete()
        messages.success(request, 'Batch deleted successfully!')
        return redirect('pharmacy:index')
    return render(request, 'products/confirm_delete.html', {'object': batch, 'type': 'batch'})

def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('unified_login')