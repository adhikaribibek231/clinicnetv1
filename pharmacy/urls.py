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
    path('issue_item/<int:pk>/', issue_item, name='issue_item'),
    path('add_to_stock/<int:pk>/', add_to_stock, name='add_to_stock'),
    path('logout/', logout_view, name='logout'),
]

