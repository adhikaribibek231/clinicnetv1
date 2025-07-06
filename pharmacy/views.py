from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.db import transaction
from .models import Product, Sale, Category
from .forms import AddForm, SaleForm
# Create your views here.

@login_required
def Pharmacy(request):
    """Main inventory view"""
    products = Product.objects.all().order_by('-id')
    return render(request, 'products/index.html', {'products': products})

@login_required
def home(request):
    """Home dashboard view"""
    products = Product.objects.all().order_by('-id')[:5]  # Show latest 5 products
    total_products = Product.objects.count()
    total_sales = Sale.objects.count()
    
    # Calculate total inventory value
    total_value = sum(product.get_total_value() for product in Product.objects.all())
    
    context = {
        'products': products,
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
def issue_item(request, pk):
    """Process item sale"""
    issued_item = get_object_or_404(Product, id=pk)
    
    if request.method == 'POST':
        sales_form = SaleForm(request.POST)
        if sales_form.is_valid():
            try:
                with transaction.atomic():
                    new_sale = sales_form.save(commit=False)
                    new_sale.item = issued_item
                    new_sale.unit_price = issued_item.unit_price
                    
                    # Check if enough stock is available
                    requested_quantity = new_sale.quantity
                    if requested_quantity > issued_item.total_quantity:
                        messages.error(request, f'Insufficient stock. Only {issued_item.total_quantity} items available.')
                        return render(request, 'products/issue_item.html', {'sales_form': sales_form})
                    
                    # Update stock
                    issued_item.total_quantity -= requested_quantity
                    issued_item.issued_quantity += requested_quantity
                    
                    # Save both objects
                    new_sale.save()
                    issued_item.save()
                    
                    messages.success(request, f'Successfully sold {requested_quantity} {issued_item.item_name} to {new_sale.issued_to}')
                    return redirect('pharmacy:receipt')
                    
            except Exception as e:
                messages.error(request, f'Error processing sale: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        sales_form = SaleForm()

    return render(request, 'products/issue_item.html', {
        'sales_form': sales_form,
        'product': issued_item,
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

def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('unified_login')