from django.contrib import admin
from .models import Customer, Agent, Category, Products, Invoices, Payments, InvoiceDetail, PaymentDetail
# Register your models here.


class CustomerAdmin(admin.ModelAdmin):
    search_fields = ('name',  'email',)


class AgentAdmin(admin.ModelAdmin):
    search_fields = ('name', 'email',)


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('type',)


class ProductsAdmin(admin.ModelAdmin):
    list_filter = ('category', 'unit_price', 'vendor')
    search_fields = ('category', 'unit_price', 'vendor')


class InvoicesAdmin(admin.ModelAdmin):
    search_fields = ('date', 'invoice_number', 'customer__name', 'agent__name', )
    list_filter = ('status', 'type',)


class PaymentsAdmin(admin.ModelAdmin):
    search_fields = ['date', 'payment_number', 'customer__name', 'agent__name', ]


class InvoiceDetailAdmin(admin.ModelAdmin):
    pass

class PaymentDetailAdmin(admin.ModelAdmin):
    pass

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Agent, AgentAdmin)
admin.site.register(Category, CategoryAdmin )
admin.site.register(Products, ProductsAdmin)
admin.site.register(Invoices, InvoicesAdmin)
admin.site.register(PaymentDetail, PaymentDetailAdmin)
admin.site.register(Payments, PaymentsAdmin)
admin.site.register(InvoiceDetail, InvoiceDetailAdmin)



