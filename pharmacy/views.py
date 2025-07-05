from django.shortcuts import render, redirect
from .models import *
# Create your views here.
def Pharmacy(request):
    products = Product.objects.all().order_by('-id')

    return render(request,
                  'products/index.html',
                  {'products': products})

def receipt(request): 
    sales = Sale.objects.all().order_by('-id')
    return render(request, 
    'products/receipt.html', 
    {'sales': sales,
    })

def product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        product = None
    
    return render(request, 'products/product_detail.html', {'product': product})


def all_sales(request):
    sales = Sale.objects.all()
    total  = sum([items.amount_received for items in sales])
    change = sum([items.get_change() for items in sales])
    net = total - change
    return render(request, 'products/all_sales.html',
     {
     'sales': sales, 
     'total': total,
     'change': change, 
     'net': net,
      })

from pharmacy.forms import AddForm, SaleForm

def issue_item(request, pk):
    issued_item = Product.objects.get(id = pk)
    sales_form = SaleForm(request.POST)  

    if request.method == 'POST':     
        if sales_form.is_valid():
            new_sale = sales_form.save(commit=False)
            new_sale.item = issued_item
            new_sale.unit_price = issued_item.unit_price   
            new_sale.save()
            #To keep track of the stock remaining after sales
            issued_quantity = int(request.POST['quantity'])
            issued_item.total_quantity -= issued_quantity
            issued_item.save()

            return redirect('receipt') 

    return render (request, 'products/issue_item.html',
     {
    'sales_form': sales_form,
    })


def add_to_stock(request, pk):
    issued_item = Product.objects.get(id = pk)
    form = AddForm(request.POST)

    if request.method == 'POST':
        if form.is_valid():
           #To add to the remaining stock quantity is reducing
            added_quantity = int(request.POST['received_quantity'])
            int(request.POST['received_quantity'])
            issued_item.total_quantity += added_quantity
            issued_item.save()
            return redirect('home')

    return render (request, 'products/add_to_stock.html', {'form': form})