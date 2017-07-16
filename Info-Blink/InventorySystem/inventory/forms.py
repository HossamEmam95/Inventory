from django import forms
from .models import Products, Invoices, InvoiceDetail
from django.forms.models import inlineformset_factory


class UpdateProductForm(forms.ModelForm):

    class Meta:
        model = Products
        fields = ('description', 'category',
                  'quantity_in_stock', 'expire_date', 'unit_price',
                  'vendor', 'manufacturer', 'discount')


class NewInvoiceForm(forms.BaseModelFormSet):

    class Meta:
        model = InvoiceDetail
        exclude = ['amount', 'remaining', 'products', 'status']


DetailFromSet = inlineformset_factory(Invoices, InvoiceDetail,
                                      form=NewInvoiceForm,
                                      exclude=['product_description',
                                               'product_price', 'invoice'],
                                      extra=0)
