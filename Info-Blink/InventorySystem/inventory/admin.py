from django.contrib import admin
from .models import *


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'credit_limit', 'balance')
    search_fields = ('name', 'email',)


class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone')
    search_fields = ('name', 'email',)


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('type',)


class ProductsAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'name', 'category', 'unit_price')
    list_filter = ('category', 'unit_price', 'vendor')
    search_fields = ('category', 'unit_price', 'vendor')


class InvoicesAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'customer', 'agent', 'amount', 'type')
    search_fields = ('date', 'invoice_number',
                     'customer__name', 'agent__name', )
    list_filter = ('status', 'type',)


class PaymentsAdmin(admin.ModelAdmin):
    list_display = ('customer', 'agent', 'amount')
    search_fields = ['date', 'payment_number',
                     'customer__name', 'agent__name', ]


class InvoiceDetailAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'product', 'product_price')


class PaymentDetailAdmin(admin.ModelAdmin):
    list_display = ('payment', 'invoice')

admin.site.register(Customer, CustomerAdmin)

admin.site.register(Agent, AgentAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Products, ProductsAdmin)
admin.site.register(Invoices, InvoicesAdmin)
admin.site.register(PaymentDetail, PaymentDetailAdmin)
admin.site.register(Payments, PaymentsAdmin)
admin.site.register(InvoiceDetail, InvoiceDetailAdmin)
