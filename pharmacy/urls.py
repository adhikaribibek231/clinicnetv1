from django.contrib import admin
from django.urls import path, include
from pharmacy.views import *


urlpatterns = [
    path('', Pharmacy, name='pharmacy'),
    path('receipt/', receipt, name = "receipt"),

    path('home/<int:product_id>/',product_detail, name='product_detail'),
    path('all_sales/', all_sales, name = 'all_sales')

]

