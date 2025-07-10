from django.contrib import admin
from django.urls import path, include
from pharmacy.views import *

app_name = 'pharmacy'

urlpatterns = [
    path('', Pharmacy, name='index'),  # Main inventory page
    path('home/', home, name='home'),  # Home dashboard
    path('receipt/', receipt, name='receipt'),
    path('all_sales/', all_sales, name='all_sales'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('add_to_stock/<int:pk>/', add_to_stock, name='add_to_stock'),
    path('add_medicine/', add_medicine, name='add_medicine'),
    path('add_medicine_batch/', add_medicine_batch, name='add_medicine_batch'),
    path('sell_medicine/', sell_medicine, name='sell_medicine'),
    path('receipt_print/<int:sale_id>/', receipt_print, name='receipt_print'),
    path('logout/', logout_view, name='logout'),
    path('edit_medicine/<int:product_id>/', edit_medicine, name='edit_medicine'),
    path('delete_medicine/<int:product_id>/', delete_medicine, name='delete_medicine'),
    path('edit_batch/<int:batch_id>/', edit_batch, name='edit_batch'),
    path('delete_batch/<int:batch_id>/', delete_batch, name='delete_batch'),
]

